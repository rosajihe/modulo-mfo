import os
import django
import random
from django.utils import timezone

# Inicializar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tienda_app.settings")
django.setup()

from productos.models import Venta, DetalleVenta, Producto

# Poblar ventas y detalles
productos = list(Producto.objects.all())

for i in range(10):  # Generar 10 ventas nuevas
    venta = Venta.objects.create(
        fecha=timezone.now(),
        total=0
    )

    total = 0
    for j in range(random.randint(2, 4)):
        producto = random.choice(productos)
        cantidad = random.randint(1, 5)
        precio_unitario = producto.precio

        detalle = DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario
        )

        total += detalle.subtotal()

    venta.total = total
    venta.save()

print("✅ Se insertaron 10 ventas con detalles aleatorios correctamente.")
