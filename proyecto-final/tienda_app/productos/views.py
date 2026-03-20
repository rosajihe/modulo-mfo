from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
from .models import Producto, Categoria,Venta,PerfilUsuario
from .forms import ProductoForm, VentaForm
from .utils import obtener_top_items, calcular_total
from rest_framework.decorators import api_view
from rest_framework.response import Response
from productos.models import Producto
from django.contrib import messages 
from django.contrib.auth import authenticate, login, logout 
from .forms import RegistroUsuarioForm, PerfilUsuarioForm, LoginForm
from .forms import VentaForm, DetalleVentaFormSet
from django.views.generic import ListView


#Inicio
def home(request):
    return render(request, "productos/home.html")

#Listado de productos con filtros
class ProductoListView(LoginRequiredMixin,View):
    def get(self, request):
        categoria = request.GET.get('categoria')
        activo = request.GET.get('activo')

        productos = Producto.objects.filter(activo=True)

        if categoria:
            productos = productos.filter(categoria__nombre=categoria)
        if activo is not None:
            productos = productos.filter(activo=(activo.lower() == 'true'))
            if categoria:
                productos = productos.filter(categoria__nombre=categoria)

        # HTML
        if request.headers.get('Accept') == 'application/json':
            data = list(productos.values())
            return JsonResponse(data, safe=False)
        return render(request, 'productos/listado.html', {'productos': productos})


# Crear producto
class ProductoCreateView(LoginRequiredMixin,View):
    def get(self, request):
        form = ProductoForm()
        return render(request, 'productos/crear.html', {'form': form})

    def post(self, request):
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos:productos_listado')
        return render(request, 'productos/crear.html', {'form': form})


# Editar producto
class ProductoUpdateView(LoginRequiredMixin,View):
    def get(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        form = ProductoForm(instance=producto)
        return render(request, 'productos/editar.html', {'form': form})

    def post(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos:productos_listado')
        return render(request, 'productos/editar.html', {'form': form})


# Eliminar producto (borrado lógico)
class ProductoDeleteView(LoginRequiredMixin,View):
    def post(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        producto.activo = False
        producto.save()
        return redirect('productos:productos_listado')


# Venta con detalle
@login_required 
def crear_venta(request):
    if request.method == "POST":
        venta_form = VentaForm(request.POST)

        if venta_form.is_valid():
            venta = venta_form.save(commit=False)
            venta.save()

            # Inicializar el formset con la instancia de venta
            formset = DetalleVentaFormSet(request.POST, instance=venta)

            if formset.is_valid():
                formset.save()

                venta.total = venta.calcular_total()
                venta.save()
                return redirect("productos:ventas_listado")
    else:
        venta_form = VentaForm()
        formset = DetalleVentaFormSet()

    productos = Producto.objects.all()
    precios_dict = {p.id: str(p.precio) for p in productos}
    return render(request, "productos/ventas/ventas.html", {
        "venta_form": venta_form,
        "formset": formset,
        "productos_json": precios_dict, 
    })

#Lista ventas
class VentaListView(LoginRequiredMixin,ListView):
    model = Venta
    template_name = "productos/ventas/ventas_listado.html"
    context_object_name = "ventas"

#Obtener precio del producto
def obtener_precio_producto(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    return JsonResponse({"precio": str(producto.precio)})

#Reporte de los 5 mas vendidos
@login_required 
def reporte_top_items(request):
    top_items = obtener_top_items()
    return render(request, 'productos/top_items.html', {'top_items': top_items})

#End point REST :listas y diccionarios
@api_view(["POST"])
def registrar_venta(request):
    # Ejemplo: recibir lista de detalles desde el body JSON
    detalles = request.data.get("detalles", [])

    # Calcular total
    total = calcular_total(detalles)

    # Construir respuesta como diccionario
    respuesta = {
        "total": total,
        "items": detalles
    }

    return Response(respuesta)

#endpoint map() y filter()
@api_view(["GET"])
def productos_activos(request):
    # Filtrar solo productos activos
    productos_activos = filter(lambda p: p.activo, Producto.objects.all())

    # Transformar productos a diccionario con map
    productos_dict = list(map(lambda p: {"id": p.id, "nombre": p.nombre}, productos_activos))

    return Response({"productos": productos_dict})


# Vistas de autenticacion 
def registro_usuario(request): 

    """Vista para registro de nuevos usuarios""" 
    if request.method == 'POST': 

        form = RegistroUsuarioForm(request.POST) 
        if form.is_valid(): 

            user = form.save() 
            username = form.cleaned_data.get('username') 
            messages.success(request, f'Cuenta creada para {username}!') 
            # Login automático después del registro 
            login(request, user) 
            return redirect('productos:home') 
    else: 

        form = RegistroUsuarioForm() 
    return render(request, 'productos/registro.html', {'form': form}) 

def login_usuario(request): 

    """Vista personalizada de login""" 
    if request.method == 'POST': 

        form = LoginForm(request.POST) 
        if form.is_valid(): 

            username = form.cleaned_data['username'] 
            password = form.cleaned_data['password'] 

            user = authenticate(request, username=username, password=password) 
            if user is not None: 

                login(request, user) 
                messages.success(request, f'¡Bienvenido {user.first_name}!') 
                # Redirigir a la página solicitada o al inicio 
                next_page = request.GET.get('next', 'productos:home') 
                return redirect(next_page) 
            else: 

                messages.error(request, 'Credenciales inválidas ⚠️') 

    else: 

        form = LoginForm() 

    return render(request, 'productos/login.html', {'form': form}) 


def logout_usuario(request):
    """Vista para cerrar sesión""" 
    logout(request) 
    messages.info(request, 'Has cerrado sesión exitosamente') 
    return redirect('productos:home')

@login_required 
def perfil_usuario(request): 
    """Vista del perfil del usuario autenticado""" 
    try: 

        perfil = request.user.perfil 
    except PerfilUsuario.DoesNotExist: 

        # Crear perfil si no existe 
        perfil = PerfilUsuario.objects.create(usuario=request.user) 

    if request.method == 'POST': 

        form = PerfilUsuarioForm(request.POST, instance=perfil) 
        if form.is_valid(): 

            form.save() 
            messages.success(request, 'Perfil actualizado exitosamente') 
            return redirect('productos:perfil') 
    else: 

        form = PerfilUsuarioForm(instance=perfil) 

 
    
    context = { 
        'form': form, 
        'perfil': perfil
    } 
    return render(request, 'productos/perfil.html', context) 