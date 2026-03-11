from django.contrib import admin
from .models import Autor, Libro, PerfilUsuario, Prestamo
# Register your models here.


# biblioteca/admin.py 
from django.contrib import admin 
from .models import Autor, Libro, PerfilUsuario, Prestamo 

@admin.register(Autor) 
class AutorAdmin(admin.ModelAdmin): 

    list_display = ['nombre', 'nacionalidad', 'fecha_nacimiento'] 
    list_filter = ['nacionalidad'] 
    search_fields = ['nombre'] 

@admin.register(Libro) 
class LibroAdmin(admin.ModelAdmin): 

    list_display = ['titulo', 'autor', 'genero', 'disponible', 'fecha_publicacion'] 
    list_filter = ['genero', 'disponible', 'autor'] 
    search_fields = ['titulo', 'autor__nombre', 'isbn'] 
    list_editable = ['disponible']


# Completa el registro para PerfilUsuario 
@admin.register(PerfilUsuario) 
class PerfilUsuarioAdmin(admin.ModelAdmin): 

    list_display = ['usuario', 'telefono', 'direccion'] 
    list_filter = ['usuario'] 

@admin.register(Prestamo) 
class PrestamoAdmin(admin.ModelAdmin): 

    list_display = ['libro', 'usuario', 'fecha_prestamo', 'fecha_devolucion_esperada', 'estado'] 
    list_filter = ['estado', 'fecha_prestamo'] 
    search_fields = ['libro__titulo', 'usuario__username']

