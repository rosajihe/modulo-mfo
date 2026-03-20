import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tienda_app.settings")
django.setup()

import csv
from productos.models import Categoria, Producto

def limpiar_texto(texto):
    return texto.strip().title()

def limpiar_numero(valor):
    try:
        return float(valor.strip())
    except (ValueError, AttributeError):
        return None

def importar_csv(ruta_csv):
    importados = 0
    descartados = 0

    with open(ruta_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            nombre_categoria = limpiar_texto(row["nombre_categoria"])
            nombre_producto = limpiar_texto(row["nombre_producto"])
            precio = limpiar_numero(row["precio"])
            stock = limpiar_numero(row["stock"])

            if precio is None or precio < 0 or stock is None or stock < 0:
                print(f"❌ Registro descartado: {row}")
                descartados += 1
                continue

            categoria, _ = Categoria.objects.get_or_create(nombre=nombre_categoria)

            Producto.objects.create(
                nombre=nombre_producto,
                precio=precio,
                stock=int(stock),
                categoria=categoria,
                activo=True
            )
            importados += 1

    print("✅ Resumen de importación")
    print(f"Registros importados: {importados}")
    print(f"Registros descartados: {descartados}")

if __name__ == "__main__":
    importar_csv("datos_iniciales.csv")
