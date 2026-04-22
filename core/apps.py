from django.apps import AppConfig
import os
import sys

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # 1. Evitamos que se ejecute durante comandos como makemigrations o migrate
        if 'runserver' not in sys.argv:
            return

        # 2. RUN_MAIN asegura que solo se ejecute una vez (Django arranca 2 procesos en local)
        if os.environ.get('RUN_MAIN') == 'true':
            import threading
            from .utils import actualizar_tasa_bcv_automatica
            
            # Un print bien visible para que sepas que Arturo configuró esto bien
            print("\n" + "="*50)
            print("🚀 SISTEMA: Iniciando actualización de tasa BCV...")
            print("="*50 + "\n")
            
            # Lanzamos en un hilo para no bloquear el inicio del servidor
            thread = threading.Thread(target=actualizar_tasa_bcv_automatica, daemon=True)
            thread.start()