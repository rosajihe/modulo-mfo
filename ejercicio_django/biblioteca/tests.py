from django.test import TestCase, Client
from django.contrib.auth.models import User 
from django.urls import reverse 
from .models import Autor, Libro, Prestamo, PerfilUsuario 
from datetime import date, timedelta 

class BibliotecaTestCase(TestCase): 

    def setUp(self): 

        """Configuración inicial para las pruebas""" 
        self.client = Client() 

        # Crear usuario de prueba 
        self.usuario = User.objects.create_user( 
            username='testuser', 
            email='test@test.com', 
            password='testpass123' 
        ) 

        # Crear perfil 
        self.perfil = PerfilUsuario.objects.create(usuario=self.usuario) 

        # Crear autor y libro de prueba 
        self.autor = Autor.objects.create( 
            nombre='Autor Test', 
            nacionalidad='Test Country' 
        ) 

        self.libro = Libro.objects.create( 
            titulo='Libro Test', 
            autor=self.autor, 
            isbn='1234567890123', 
            fecha_publicacion=date.today(), 
            genero='ficcion', 
            paginas=200 
        ) 

    def test_registro_usuario(self): 
        """Prueba el registro de usuarios""" 

        response = self.client.post(reverse('biblioteca:registro'), { 
            'username': 'newuser', 
            'first_name': 'New', 
            'last_name': 'User', 
            'email': 'new@test.com', 
            'password1': 'newpass123', 
            'password2': 'newpass123' 
        }) 

        self.assertEqual(response.status_code, 302) # Redirección después del registro 
        self.assertTrue(User.objects.filter(username='newuser').exists())


    def test_solicitar_prestamo(self): 
        """Prueba la solicitud de préstamo""" 
        self.client.login(username='testuser', password='testpass123') 

        response = self.client.post( 
        reverse('biblioteca:solicitar_prestamo', args=[self.libro.id]) 
        ) 

        self.assertEqual(response.status_code, 302) 
        self.assertTrue( 
            Prestamo.objects.filter(usuario=self.usuario, libro=self.libro).exists() 
        ) 

        # Verificar que el libro ya no está disponible 
        self.libro.refresh_from_db() 
        self.assertFalse(self.libro.disponible) 

    def test_busqueda_libros(self): 

        """Prueba la funcionalidad de búsqueda""" 
        response = self.client.get(reverse('biblioteca:busqueda'), { 'q': 'Test' }) 

        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'Libro Test') 

