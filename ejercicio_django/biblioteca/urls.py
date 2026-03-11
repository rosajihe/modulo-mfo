from django.urls import path, include 
from rest_framework.routers import DefaultRouter 
from . import views

# Configurar router para API 
router = DefaultRouter() 
router.register(r'libros', views.LibroViewSet) 
router.register(r'mis-prestamos', views.MisPrestamoViewSet, basename='misprestamos')

# Define el namespace de la aplicación 
app_name = 'biblioteca'

urlpatterns = [
    #URL basicas
    path('', views.inicio, name='inicio'),
    #Libros,autores
    path('libros/', views.lista_libros, name='lista_libros'),
    path('libros/<int:libro_id>/', views.detalle_libro, name='detalle_libro'),
    path('autores/', views.lista_autores, name='lista_autores'),
    path('autores/<int:autor_id>/', views.detalle_autor, name='detalle_autor'),
    path('libros/genero/<str:genero>/', views.libros_por_genero, name='libros_genero'),
    #Autenticación 
    path('registro/', views.registro_usuario, name='registro'), 
    path('login/', views.login_usuario, name='login'), 
    path('logout/', views.logout_usuario, name='logout'), 
    path('perfil/', views.perfil_usuario, name='perfil'), 
    #Prestamos
    path('mis-prestamos/', views.mis_prestamos, name='mis_prestamos'),
    path('prestamo/<int:libro_id>/', views.solicitar_prestamo, name='solicitar_prestamo'),
    # Funcionalidades avanzadas 
    path('busqueda/', views.busqueda_avanzada, name='busqueda'),  
    path('recomendaciones/', views.recomendaciones, name='recomendaciones'), 
    path('estadisticas/', views.estadisticas_biblioteca, name='estadisticas'), 
    # Administración 
    path('admin-dashboard/', views.dashboard_admin, name='dashboard_admin'), 
    path('gestionar-prestamo/<int:prestamo_id>/', views.gestionar_prestamo, name='gestionar_prestamo'), 
    path('reporte-prestamos/', views.generar_reporte_prestamos, name='reporte_prestamos'), 
    #API
    path('api/token/', views.obtener_token, name='api_token'), 
    path('api/mis-libros/', views.mis_libros_api, name='api_mis_libros'),
]