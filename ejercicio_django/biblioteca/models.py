from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Autor(models.Model): 

    """Modelo para representar autores de libros""" 
    nombre = models.CharField(max_length=100, help_text="Nombre completo del autor") 
    fecha_nacimiento = models.DateField(null=True, blank=True) 
    nacionalidad = models.CharField(max_length=50, blank=True) 
    biografia = models.TextField(blank=True, help_text="Biografía del autor") 
    fecha_creacion = models.DateTimeField(auto_now_add=True) 

    def __str__(self): 
        """Representación en cadena del autor""" 
        return self.nombre 

    class Meta: 
        verbose_name = "Autor" 
        verbose_name_plural = "Autores" 
        ordering = ['nombre']


class Libro(models.Model): 
    """Modelo para representar libros en la biblioteca""" 

    # Opciones para el género 
    GENEROS = [ 
    ('ficcion', 'Ficción'), 
    ('no_ficcion', 'No Ficción'), 
    ('ciencia', 'Ciencia'), 
    ('historia', 'Historia'), 
    ('biografia', 'Biografía'), 
    ('tecnologia', 'Tecnología'),
    ] 

    titulo = models.CharField(max_length=200) 
    # Completa la relación con Autor 
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='libros') 
    isbn = models.CharField(max_length=13, unique=True, help_text="Código ISBN de 13 dígitos") 
    fecha_publicacion = models.DateField() 
    genero = models.CharField(max_length=20, choices=GENEROS, default='ficcion') 
    paginas = models.PositiveIntegerField() 
    descripcion = models.TextField(blank=True) 
    disponible = models.BooleanField(default=True) 
    fecha_agregado = models.DateTimeField(auto_now_add=True) 

    def __str__(self): 

        return f"{self.titulo} - {self.autor.nombre}" 

    def esta_disponible(self): 

        """Método para verificar disponibilidad""" 
        return self.disponible 

    class Meta: 

        verbose_name = "Libro" 
        verbose_name_plural = "Libros" 
        ordering = ['-fecha_agregado']



class PerfilUsuario(models.Model): 
    """Perfil extendido para usuarios de la biblioteca""" 

    # Relación uno a uno con el usuario de Django 
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



class Prestamo(models.Model): 

    """Modelo para gestionar préstamos de libros""" 

    ESTADOS = [ 
    ('activo', 'Activo'), 
    ('devuelto', 'Devuelto'), 
    ('vencido', 'Vencido'), 
    ] 

    # Completa las relaciones 
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prestamos') 
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='prestamos') 
    fecha_prestamo = models.DateTimeField(auto_now_add=True) 
    fecha_devolucion_esperada = models.DateField() 
    fecha_devolucion_real = models.DateTimeField(null=True, blank=True) 
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo') 

    def __str__(self): 

        return f"{self.libro.titulo} - {self.usuario.username}" 

    def esta_vencido(self): 

        """Verifica si el préstamo está vencido""" 
        from django.utils import timezone 
        if self.estado == 'activo': 

            return timezone.now().date() > self.fecha_devolucion_esperada 
        return False 

    def duracion_prestamo(self):

        """Calcula la duración del préstamo en días""" 
        if self.fecha_devolucion_real: 

            return (self.fecha_devolucion_real.date() - self.fecha_prestamo.date()).days 

        else: 

            from django.utils import timezone 
            return (timezone.now().date() - self.fecha_prestamo.date()).days 

    class Meta: 
        verbose_name = "Préstamo" 
        verbose_name_plural = "Préstamos" 
        ordering = ['-fecha_prestamo']






