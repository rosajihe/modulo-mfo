from django.urls import path
from . import views
from .views import (
    ProductoListView,
    ProductoCreateView,
    ProductoUpdateView,
    ProductoDeleteView,
    VentaListView,
)

# Define el namespace de la aplicación 
app_name = 'productos'

urlpatterns = [
    # Página de inicio
    path('', views.home, name='home'),
    # Listado de productos
    path('productos/', ProductoListView.as_view(), name='productos_listado'),

    # Crear producto
    path('productos/crear/', ProductoCreateView.as_view(), name='productos_crear'),

    # Editar producto
    path('productos/<int:pk>/editar/', ProductoUpdateView.as_view(), name='productos_editar'),

    # Eliminar producto (borrado lógico)
    path('productos/<int:pk>/eliminar/', ProductoDeleteView.as_view(), name='productos_eliminar'),

    # Crear movimiento (venta con detalle)
    path("ventas/nueva/", views.crear_venta, name="crear_venta"),

    path("ventas/", VentaListView.as_view(), name="ventas_listado"),

    # Reporte mas vendidos
    path('reportes/top-items/', views.reporte_top_items, name='reporte_top_items'),

    # Endpoints(postman-urlsitio)
    path("registrar-venta/", views.registrar_venta, name="registrar_venta"),

    path("productos-activos/", views.productos_activos, name="productos_activos"),

    # Autenticación 
    path('registro/', views.registro_usuario, name='registro'), 

    path('login/', views.login_usuario, name='login'), 

    path('logout/', views.logout_usuario, name='logout'), 
    
    path('perfil/', views.perfil_usuario, name='perfil'), 

]
