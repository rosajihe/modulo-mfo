from django import forms
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User 
from .models import Categoria, Producto, Venta, DetalleVenta,PerfilUsuario 
from .utils import validar_cantidad
from django import forms
from django.forms import inlineformset_factory


# Formulario para Categoria
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']


# Formulario para Producto
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'activo']

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo.❌")
        return stock

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.❌")
        return precio


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = []  # solo fecha y total se calculan automáticamente
       

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ["producto", "cantidad", "precio_unitario"]

# Formset para detalles
DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    extra=1,            # número de formularios vacíos iniciales
    can_delete=True     # permitir eliminar filas
)

# Registro usuario
class RegistroUsuarioForm(UserCreationForm): 

    """Formulario extendido para registro de usuarios""" 
    email = forms.EmailField(required=True) 
    first_name = forms.CharField(max_length=30, required=True, label="Nombre") 
    last_name = forms.CharField(max_length=30, required=True, label="Apellido") 

    class Meta: 

        model = User 
        fields = ("username", "first_name", "last_name", "email", "password1", "password2") 

    def save(self, commit=True): 
        """Guarda el usuario y crea su perfil""" 
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"] 
        user.first_name = self.cleaned_data["first_name"] 
        user.last_name = self.cleaned_data["last_name"] 

        if commit: 
            user.save() 
            # Crear perfil automáticamente 
            PerfilUsuario.objects.create(usuario=user) 
        return user 

class PerfilUsuarioForm(forms.ModelForm): 
    """Formulario para editar perfil de usuario""" 
    class Meta: 

        model = PerfilUsuario 
        fields = ['telefono', 'direccion'] 
        widgets = { 
            'direccion': forms.Textarea(attrs={'rows': 3}), 
            'telefono': forms.TextInput(attrs={'placeholder': '+57 300 123 4567'}) 
        } 

class LoginForm(forms.Form): 
    """Formulario personalizado de login""" 
    username = forms.CharField( 
        max_length=150, 
        widget=forms.TextInput(attrs={ 
            'class': 'form-control', 
            'placeholder': 'Nombre de usuario' 
        }) 
    ) 
    password = forms.CharField( 
        widget=forms.PasswordInput(attrs={ 
            'class': 'form-control', 
            'placeholder': 'Contraseña' 
        }) 
    )

