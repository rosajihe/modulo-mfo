from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.core.validators import MinValueValidator

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    

class Producto(models.Model):
    sku = models.PositiveIntegerField(unique=True, editable=False) # Identificador único
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2,validators=[MinValueValidator(0)])
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)  # <-- campo para borrado lógico
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.sku:
            ultimo = Producto.objects.order_by("-sku").first()
            self.sku = (ultimo.sku + 1) if ultimo else 1
        super().save(*args, **kwargs)

    def clean(self):
        if self.stock < 0:
            raise ValidationError("El stock no puede ser negativo.")

    def __str__(self):
        return self.nombre
    

class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calcular_total(self):
        return sum(detalle.subtotal() for detalle in self.detalles.all())

    def save(self, *args, **kwargs):
        # Solo recalcular si la venta ya existe en la BD
        if self.pk:
            self.total = self.calcular_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Venta {self.id} - {self.fecha.strftime('%Y-%m-%d')}"
    

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey("Producto", on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario
    

    def clean(self):
        # Validar que la cantidad sea positiva
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser positiva.")
        # Validar que el precio no sea negativo
        if self.precio_unitario < 0:
            raise ValidationError("El precio unitario no puede ser negativo.")

    def save(self, *args, **kwargs):
        # Ejecutar validaciones antes de guardar
        self.clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"


class PerfilUsuario(models.Model): 
   
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil') 
    telefono = models.CharField(max_length=15, blank=True) 
    direccion = models.TextField(blank=True) 
    fecha_registro = models.DateTimeField(auto_now_add=True) 
    activo = models.BooleanField(default=True) 

    def __str__(self):

        return f"Perfil de {self.usuario.username}" 

    def nombre_completo(self): 

        """Retorna el nombre completo del usuario""" 
        return f"{self.usuario.first_name} {self.usuario.last_name}" 

    class Meta: 
        verbose_name = "Perfil de Usuario" 
        verbose_name_plural = "Perfiles de Usuario"