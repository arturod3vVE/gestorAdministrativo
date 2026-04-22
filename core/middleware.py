# core/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class ForzarCambioClaveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Solo actuamos si el usuario está logueado y no es admin
        if request.user.is_authenticated and not request.user.is_staff:
            socio = getattr(request.user, 'socio', None)
            
            if socio and not socio.clave_cambiada:
                # Usamos los nombres EXACTOS de tu urls.py
                ruta_cambio = reverse('cambiar_clave_inicial')
                ruta_logout = reverse('logout')  # path('salir/', ..., name='logout')
                ruta_login = reverse('verificar_perfil') # path('entrar/', ..., name='verificar_perfil')

                rutas_permitidas = [ruta_cambio, ruta_logout, ruta_login]
                
                # Agregamos una validación extra: si el path es "/" (dashboard) 
                # y no ha cambiado clave, lo mandamos a cambiarla
                if request.path not in rutas_permitidas and not request.path.startswith('/static/'):
                    return redirect('cambiar_clave_inicial')

        return self.get_response(request)