# core/management/commands/tarea_bcv.py
from django.core.management.base import BaseCommand
from core.utils import actualizar_tasa_bcv_automatica
from datetime import datetime

class Command(BaseCommand):
    help = 'Actualiza la tasa del BCV de Lunes a Viernes a medianoche'

    def handle(self, *args, **options):
        # 0=Lunes, 4=Viernes
        hoy = datetime.now().weekday()
        
        if hoy <= 4:
            exito, valor = actualizar_tasa_bcv_automatica()
            if exito:
                self.stdout.write(self.style.SUCCESS(f'Éxito: Tasa actualizada a {valor}'))
            else:
                self.stdout.write(self.style.ERROR('Error: No se pudo conectar con el BCV'))
        else:
            self.stdout.write('Sábado/Domingo: El BCV no actualiza tasa oficial.')