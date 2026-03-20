from django.db import DatabaseError
from django.db.models import Sum
from .models import DetalleVenta

def validar_cantidad(cantidad: int) -> bool:
    """Valida que la cantidad sea positiva."""
    return cantidad > 0

def calcular_total(detalles: list[dict]) -> float:
    """Calcula el total de una venta a partir de una lista de detalles."""
    return sum(item['cantidad'] * item['precio_unitario'] for item in detalles)

def obtener_top_items(limit=5):
    """Consulta los productos más vendidos."""
    try:
        return (
            DetalleVenta.objects
            .values('producto__nombre')
            .annotate(total_vendido=Sum('cantidad'))
            .order_by('-total_vendido')[:limit]
        )
    except DatabaseError:
        return []


