from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
import uuid
from decimal import Decimal, ROUND_HALF_UP

# --- 1. CONFIGURACIÓN DEL SISTEMA ---
class ConfigSistema(models.Model):
    tasa_bcv = models.DecimalField(
        max_digits=20, 
        decimal_places=4, 
        default=Decimal('36.0000'), 
        verbose_name="Tasa BCV"
    )
    nombre_linea = models.CharField(max_length=100, default="Línea de Conductores Unidos")
    
    # Nuevo campo: Plazo en días antes de bloquear al socio
    dias_gracia = models.PositiveIntegerField(
        default=30, 
        verbose_name="Días de Gracia",
        help_text="Días permitidos para tener deuda antes de bloquear el QR"
    )
    
    ultima_actualizacion = models.DateTimeField(auto_now=True) 

    def save(self, *args, **kwargs):
        if self.pk:
            original = ConfigSistema.objects.get(pk=self.pk)
            user_audit = kwargs.pop('user_audit', None)
            
            # Auditoría para cambio de Tasa
            if original.tasa_bcv != self.tasa_bcv:
                BitacoraAuditoria.objects.create(
                    admin=user_audit,
                    accion='ACTUALIZAR_TASA',
                    modulo='Configuración',
                    descripcion=f"Tasa cambiada: {original.tasa_bcv} -> {self.tasa_bcv} Bs."
                )

            # Auditoría para cambio de Días de Gracia (Importante para control interno)
            if original.dias_gracia != self.dias_gracia:
                BitacoraAuditoria.objects.create(
                    admin=user_audit,
                    accion='ACTUALIZAR_CONFIG',
                    modulo='Configuración',
                    descripcion=f"Días de gracia modificados: {original.dias_gracia} -> {self.dias_gracia} días."
                )

        super(ConfigSistema, self).save(*args, **kwargs)


# --- 2. CATÁLOGO DE CONCEPTOS ---
class ConceptoCobro(models.Model):
    nombre = models.CharField(max_length=100)
    
    monto_sugerido = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Precio Base (Dueño Conductor)"
    )
    
    monto_chofer = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Precio con Avance/Chofer"
    )
    
    def __str__(self):
        return f"{self.nombre}"


# --- 3. SOCIOS (DUEÑOS) ---
class Socio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Socio (Dueño)")
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    codigo_verificacion = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    unidad = models.CharField(
        max_length=10,
        unique=True,
        help_text="Número de unidad/autobús"
    )

    tiene_avance = models.BooleanField(
        default=False, 
        verbose_name="¿Tiene Avance Asignado?",
        help_text="Marcar si la unidad es trabajada por un chofer (Avance)"
    )
    
    nombre_avance = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Nombre del Avance",
        help_text="Opcional. Solo informativo."
    )
    
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateField(auto_now_add=True)
    clave_cambiada = models.BooleanField(default=False)

    @property
    def es_solvente(self):
        # 1. Obtenemos la configuración (o usamos 5 por defecto si no existe)
        config = ConfigSistema.objects.first()
        plazo = config.dias_gracia if config else 30
        
        # 2. Calculamos el "Punto de Corte"
        # Si un aviso fue creado DESPUÉS de esta fecha, todavía está en periodo de gracia.
        fecha_limite = timezone.now() - timedelta(days=plazo)

        # 3. Buscamos avisos de deuda que ya pasaron el periodo de gracia
        # lt = Less Than (creados hace más tiempo que los días permitidos)
        deudas_vencidas = self.avisos.filter(
            estado__in=['PENDIENTE', 'PARCIAL'],
            fecha_creacion__lt=fecha_limite 
        ).exists()

        return not deudas_vencidas

    def __str__(self):
        tipo = "CON AVANCE" if self.tiene_avance else "DUEÑO CONDUCTOR"
        return f"{self.unidad} - {self.nombre} [{tipo}]"


# --- 6. MÉTODOS DE PAGO ---
class MetodoPago(models.Model):
    TIPOS = [
        ('PAGO_MOVIL', 'Pago Móvil'),
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
        ('ZELLE', 'Zelle / Divisas Digitales'),
        ('EFECTIVO', 'Efectivo'),
    ]

    MONEDAS = [
        ('BS', 'Bolívares (Bs.)'),
        ('USD', 'Dólares ($)'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS)
    moneda = models.CharField(max_length=3, choices=MONEDAS, default='BS')
    nombre_banco = models.CharField(max_length=50)
    titular = models.CharField(max_length=100)
    cedula_rif = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    numero_cuenta = models.CharField(max_length=30, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    @property
    def datos_cuenta(self):
        if self.tipo == 'PAGO_MOVIL':
            return f"Banco: {self.nombre_banco} | Tlf: {self.telefono} | C.I: {self.cedula_rif}"
        elif self.tipo == 'TRANSFERENCIA':
            return f"Banco: {self.nombre_banco} | Cta: {self.numero_cuenta}"
        else:
            return f"{self.nombre_banco} | {self.correo}"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre_banco}"

# --- 8. GASTOS GENERALES ---
class GastoGeneral(models.Model):
    concepto = models.CharField(max_length=200)
    monto_total_usd = models.DecimalField(max_digits=20, decimal_places=2)
    fecha_factura = models.DateField()
    comprobante = models.FileField(upload_to='facturas_gastos/', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.concepto} - ${self.monto_total_usd}"

class HistorialTasa(models.Model):
    fecha = models.DateField(auto_now_add=True, unique=True)
    valor = models.DecimalField(max_digits=20, decimal_places=4)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.fecha} - Bs. {self.valor}"
    
class AvisoCobro(models.Model):
    ESTADOS = (
        ('PENDIENTE', 'Por Pagar'),
        ('PARCIAL', 'Abono Parcial'),
        ('REVISION', 'En Revisión (Pagos Reportados)'),
        ('PAGADO', 'Pagado Totalmente'),
    )

    socio = models.ForeignKey('Socio', on_delete=models.CASCADE, related_name='avisos')
    mes = models.PositiveIntegerField()
    anio = models.PositiveIntegerField()
    fecha_emision = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='PENDIENTE')

    class Meta:
        unique_together = ('socio', 'mes', 'anio')
        ordering = ['-anio', '-mes']

    def __str__(self):
        return f"{self.periodo_formateado} - {self.socio.unidad}"

    @property
    def periodo_formateado(self):
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        try:
            return f"Aviso de Cobro {meses[self.mes - 1]} {self.anio}"
        except IndexError:
            return f"Aviso {self.mes}/{self.anio}"

    @property
    def total_facturado_usd(self):
        return self.detalles.aggregate(total=Sum('monto_dolares'))['total'] or Decimal('0.00')

    @property
    def total_pagado_usd(self):
        return self.pagos.filter(estado='APROBADO').aggregate(total=Sum('monto_dolares'))['total'] or Decimal('0.00')

    @property
    def saldo_pendiente_usd(self):
        return self.total_facturado_usd - self.total_pagado_usd

class ItemAviso(models.Model):
    aviso = models.ForeignKey(AvisoCobro, on_delete=models.CASCADE, related_name='detalles')
    descripcion = models.CharField(max_length=200)
    monto_dolares = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return f"{self.descripcion} - ${self.monto_dolares}"
    
class Pago(models.Model):
    ESTADOS = (
        ('REVISION', 'En Revisión'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    )
    aviso = models.ForeignKey(AvisoCobro, on_delete=models.CASCADE, related_name='pagos')
    metodo = models.ForeignKey(MetodoPago, on_delete=models.PROTECT, related_name='pagos')
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    referencia = models.CharField(max_length=50)
    comprobante = models.ImageField(upload_to='comprobantes/')
    
    monto_bolivares = models.DecimalField(max_digits=20, decimal_places=2)
    tasa_bcv_usada = models.DecimalField(max_digits=20, decimal_places=4) 
    monto_dolares = models.DecimalField(max_digits=20, decimal_places=2) 
    
    estado = models.CharField(max_length=15, choices=ESTADOS, default='REVISION')

    def save(self, *args, **kwargs):
        if self.monto_bolivares and self.tasa_bcv_usada:
            calculo = self.monto_bolivares / self.tasa_bcv_usada
            self.monto_dolares = calculo.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pago {self.referencia} - {self.metodo.nombre} - ${self.monto_dolares}"
    
class CierreMes(models.Model):
    mes = models.IntegerField()
    anio = models.IntegerField()
    fecha_cierre = models.DateTimeField(auto_now_add=True)
    cerrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('mes', 'anio')

class BitacoraAuditoria(models.Model):
    ACCIONES = (
        # Módulo de Pagos
        ('APROBAR', 'Aprobación de Pago'),
        ('RECHAZAR', 'Rechazo de Pago'),
        
        # Módulo de Cobranzas y Deudas
        ('CARGO_MANUAL', 'Cargo Individual Creado'),
        ('CARGO_MASIVO', 'Generación Masiva (Formulario)'),
        ('GASTO_COLECTIVO', 'Distribución de Gasto Común'),
        ('IMPORTAR_CARGOS', 'Importación de Cargos (Excel)'),
        
        # Módulo de Socios
        ('EDITAR_SOCIO', 'Edición de Datos de Socio'),
        ('IMPORTAR_SOCIOS', 'Importación de Socios (Excel)'),
        
        # Módulo de Configuración y Control
        ('CIERRE_MES', 'Cierre de Periodo Contable'),
        ('ACTUALIZAR_METODO', 'Actualización de Método de Pago'),
        ('ELIMINAR_METODO', 'Eliminación de Método de Pago'),
        ('ACTUALIZAR_TASA', 'Actualización de Tasa Cambiaria'),
    )

    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='acciones_auditoria')
    accion = models.CharField(max_length=20, choices=ACCIONES)
    modulo = models.CharField(max_length=50)
    descripcion = models.TextField(help_text="Detalle de lo que se hizo y a quién afectó")
    fecha = models.DateTimeField(auto_now_add=True)
    # Opcional pero recomendado para auditorías
    ip_address = models.GenericIPAddressField(null=True, blank=True) 

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        usuario = self.admin.username if self.admin else "Sistema"
        return f"{self.fecha.strftime('%d/%m/%Y %H:%M')} - {usuario} ({self.get_accion_display()})"
    
@receiver(post_save, sender=ItemAviso)
@receiver(post_delete, sender=ItemAviso)
def actualizar_estado_aviso_por_items(sender, instance, **kwargs):
    try:
        aviso = instance.aviso
        
        total_facturado = aviso.detalles.aggregate(total=Sum('monto_dolares'))['total'] or Decimal('0.00')
        total_pagado = aviso.pagos.filter(estado='APROBADO').aggregate(total=Sum('monto_dolares'))['total'] or Decimal('0.00')

        if total_facturado == Decimal('0.00'):
            aviso.estado = 'PAGADO'
        elif total_pagado >= (total_facturado - Decimal('0.01')): 
            aviso.estado = 'PAGADO'
        elif total_pagado > Decimal('0.00'):
            aviso.estado = 'PARCIAL'
        else:
            aviso.estado = 'PENDIENTE'
            
        aviso.save()
        
    except Exception as e:
        print(f"Error en signal de AvisoCobro: {e}")