from django.urls import path
from . import views

urlpatterns = [
    # Dashboard y autenticación
    path('entrar/', views.redireccionar_por_rol, name='verificar_perfil'),
    path('', views.dashboard, name='dashboard'),
    path('salir/', views.salir_del_sistema, name='logout'),

    # Gestión de Socios
    path('socios/', views.lista_transparencia, name='transparencia'),
    path('crear-socio/', views.registrar_socio_completo, name='registrar_socio_completo'),
    path('socios/editar/<int:socio_id>/', views.editar_socio, name='editar_socio'),
    path('socios/importar-masivo/', views.importar_socios_masivo, name='importar_socios_masivo'),
    path('socios/descargar-plantilla/', views.descargar_plantilla_socios, name='descargar_plantilla_socios'),
    path('validar-solvencia/<uuid:slug_verificacion>/', views.validar_solvencia, name='validar_solvencia_externo'),

    # Seguridad del Socio
    path('socio/toggle-acceso/<int:socio_id>/', views.toggle_acceso_portal, name='toggle_acceso'),
    path('socio/crear-usuario/<int:socio_id>/', views.crear_usuario_portal, name='crear_usuario'),
    path('primer-ingreso/cambiar-clave/', views.cambiar_clave_inicial, name='cambiar_clave_inicial'),
    path('socio/reset-clave/<int:socio_id>/', views.resetear_clave, name='reset_clave'),

    # Cobranza (Administración)
    path('cobranza/', views.modulo_cobranza, name='modulo_cobranza'),
    path('generar-masivo/', views.generar_cobros_masivos, name='generar_cobros_masivos'),
    path('gestionar-cobranza-socio/<int:socio_id>/', views.gestionar_socio_cobranza, name='gestionar_socio_cobranza'),
    path('revision-pago/<int:pago_id>/', views.revision_transferencia_admin, name='revision_transferencia_admin'),
    path('importar-cargos/', views.importar_cargos_masivos, name='importar_cargos_masivos'),
    path('cobranza/gasto-comun/', views.registrar_gasto_colectivo, name='registrar_gasto_colectivo'),
    path('cobranza/cargar-deuda-manual/', views.cargar_deuda_manual_general, name='cargar_deuda_manual_general'),
    path('pago/<int:pago_id>/<str:accion>/', views.aprobar_rechazar_pago, name='aprobar_rechazar_pago'),
    path('contabilidad/cerrar-mes/', views.cerrar_mes_contable, name='cerrar_mes_contable'),
    path('administracion/auditoria/', views.bitacora_auditoria, name='bitacora_auditoria'),
    path('contabilidad/periodos/', views.gestion_periodos, name='gestion_periodos'),
    path('contabilidad/reporte-conceptos/', views.reporte_financiero_conceptos, name='reporte_conceptos'),
    path('historial-pagos/', views.historial_pagos, name='historial_pagos'),

    # Conceptos
    path('conceptos/', views.gestionar_conceptos, name='gestionar_conceptos'),
    path('conceptos/eliminar/<int:id>/', views.eliminar_concepto, name='eliminar_concepto'),

    # Portal del Socio
    path('portal/', views.portal_socio, name='portal_socio'),
    path('factura-mensual/<int:mes>/<int:anio>/', views.factura_mensual, name='factura_mensual'),
    path('mis-pagos/', views.mis_pagos, name='mis_pagos'),
    path('configuracion-perfil/', views.configuracion_perfil, name='configuracion_perfil'),
    
    # Rutas actualizadas de Deuda -> Aviso
    path('reportar-pago/<int:aviso_id>/', views.reportar_pago, name='reportar_pago'),
    path('aviso-cobro/<int:aviso_id>/', views.previsualizar_aviso, name='previsualizar_aviso'),
    path('recibo-imprimir/<int:aviso_id>/', views.recibo_print, name='recibo_print'),

    # Configuración de Cuentas
    path('configuracion-pagos/', views.configuracion_pagos, name='configuracion_pagos'),
    path('configuracion-pagos/eliminar/<int:metodo_id>/', views.eliminar_metodo_pago, name='eliminar_metodo_pago'),
    path('toggle-metodo/<int:metodo_id>/', views.toggle_metodo_pago, name='toggle_metodo'),
]