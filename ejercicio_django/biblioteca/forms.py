# biblioteca/forms.py 
from django import forms 
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User 
from .models import PerfilUsuario 


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

