from django.contrib import admin
from .models import Categoria, Producto, Venta, DetalleVenta

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'precio', 'stock', 'categoria', 'activo')
    readonly_fields = ('sku',)  # Solo lectura, no editable

admin.site.register(Categoria)
admin.site.register(Venta)
admin.site.register(DetalleVenta)