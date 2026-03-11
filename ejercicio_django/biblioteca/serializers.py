from rest_framework import serializers 
from .models import Libro, Autor, Prestamo 

class AutorSerializer(serializers.ModelSerializer): 

    class Meta: 

        model = Autor 
        fields = ['id', 'nombre', 'nacionalidad', 'fecha_nacimiento'] 


class LibroSerializer(serializers.ModelSerializer): 
    autor = AutorSerializer(read_only=True) 

    class Meta: 
        model = Libro 
        fields = ['id', 'titulo', 'autor', 'isbn', 'genero', 'paginas', 'descripcion', 'disponible', 'fecha_publicacion'] 


class PrestamoSerializer(serializers.ModelSerializer):

    libro = LibroSerializer(read_only=True) 
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True) 

    class Meta: 

        model = Prestamo 
        fields = ['id', 'libro', 'usuario_nombre', 'fecha_prestamo', 'fecha_devolucion_esperada', 'estado']






