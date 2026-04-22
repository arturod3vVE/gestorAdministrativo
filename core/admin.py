from django.contrib import admin
from .models import Socio, ConfigSistema, ConceptoCobro, MetodoPago, HistorialTasa, CierreMes, BitacoraAuditoria

# --- 1. CONFIGURACIÓN DEL SISTEMA ---
@admin.register(ConfigSistema)
class ConfigSistemaAdmin(admin.ModelAdmin):
    # Mostramos los campos principales en la lista
    list_display = ('nombre_linea', 'tasa_bcv', 'dias_gracia', 'ultima_actualizacion')
    
    # Permitimos que se editen directamente desde la lista para mayor rapidez
    list_editable = ('tasa_bcv', 'dias_gracia')

    # --- INTEGRACIÓN CON TU BITÁCORA DE AUDITORÍA ---
    def save_model(self, request, obj, form, change):
        """
        Sobrescribimos el guardado del admin para pasarle el usuario actual
        al método save() del modelo y que la auditoría funcione.
        """
        # Llamamos al save del modelo pasando el user_audit
        obj.save(user_audit=request.user)

    # Opcional: Si quieres que solo exista un registro de configuración (Singleton)
    def has_add_permission(self, request):
        if ConfigSistema.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False # Evitamos borrar la configuración por error

# --- 2. GESTIÓN DE CONCEPTOS (NUEVO) ---
@admin.register(ConceptoCobro)
class ConceptoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'monto_sugerido', 'monto_chofer')
    search_fields = ('nombre',)

# --- 3. GESTIÓN DE MÉTODOS DE PAGO (NUEVO) ---
@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'nombre_banco', 'titular', 'activo')
    list_filter = ('tipo', 'activo')

# --- 4. SOCIOS ---
@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    # Agregamos 'tiene_avance' para que veas rápido quién tiene chofer
    list_display = ('unidad', 'nombre', 'cedula', 'telefono', 'tiene_avance', 'user') 
    search_fields = ('nombre', 'cedula', 'unidad')
    list_filter = ('activo', 'tiene_avance') # Filtros laterales útiles
    
    # Tu truco para vincular usuarios rápido
    list_editable = ('user',) 

@admin.register(HistorialTasa)
class HistorialTasaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'valor') # Esto hace que se vea bonito en columnas
    list_filter = ('fecha',)         # Permite filtrar por fecha
    readonly_fields = ('fecha',)

@admin.register(CierreMes)
class CierreMesAdmin(admin.ModelAdmin):
    # Columnas que verás en la lista
    list_display = ('anio', 'mes', 'cerrado_por', 'fecha_cierre')
    # Filtros laterales
    list_filter = ('anio', 'mes')
    # Para que el cierre sea fácil de encontrar
    search_fields = ('anio', 'mes')

@admin.register(BitacoraAuditoria)
class BitacoraAuditoriaAdmin(admin.ModelAdmin):
    # Usamos una función personalizada para mostrar el nombre del admin
    list_display = ('fecha', 'get_admin_display', 'accion', 'modulo', 'ip_address')
    
    # Filtros laterales
    list_filter = ('accion', 'modulo', 'admin', 'fecha')
    
    # Buscador (admin__username funciona bien aquí porque Django hace el Join automáticamente)
    search_fields = ('descripcion', 'admin__username', 'ip_address')
    
    # Orden predeterminado: lo más nuevo primero
    ordering = ('-fecha',)

    # --- LÓGICA PARA EVITAR EL ERROR DE NONETYPE ---
    @admin.display(description='Administrador')
    def get_admin_display(self, obj):
        """Muestra el nombre del usuario o 'Sistema' si es nulo."""
        if obj.admin:
            return obj.admin.username
        return "🤖 Sistema"
    
    def has_add_permission(self, request):
        """Impide que se creen logs manualmente desde el admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Impide que se edite cualquier log existente."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Solo los superusuarios pueden borrar logs (por limpieza de BD)."""
        return request.user.is_superuser