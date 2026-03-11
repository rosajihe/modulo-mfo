from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required 
from django.shortcuts import render, redirect 
from django.contrib import messages 
from django.contrib.auth.models import User 
from .forms import RegistroUsuarioForm, PerfilUsuarioForm, LoginForm
from .models import PerfilUsuario, Prestamo, Libro, Autor
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from datetime import date, timedelta
from django.db.models import Count
#para vista API
from rest_framework.decorators import api_view, authentication_classes, permission_classes 
from rest_framework.authentication import TokenAuthentication 
from rest_framework.permissions import IsAuthenticated 
from rest_framework.response import Response 
from rest_framework.authtoken.models import Token 
from django.http import JsonResponse
# busqueda
from django.db.models import Q 
from django.core.paginator import Paginator
#dashbord admin
from django.contrib.admin.views.decorators import staff_member_required 
from django.utils.decorators import method_decorator 
from django.views.generic import TemplateView 
#serializers
from rest_framework import viewsets, status
from rest_framework.decorators import action 
from rest_framework.response import Response 
from .serializers import LibroSerializer, AutorSerializer, PrestamoSerializer
#optimizacion y mejores practicas
from django.views.generic import ListView 
from django.db.models import Prefetch



def inicio(request):
    """Vista principal con navegación""" 
    return render(request, 'biblioteca/inicio.html')

def lista_libros(request):
    """Vista que muestra la lista de libros"""
    libros = Libro.objects.all()
    return render(request, 'biblioteca/lista_libros.html', {
        'libros': libros
    })

@login_required
def detalle_libro(request, libro_id):
    """Vista que muestra el detalle de un libro específico"""
    try: 

        from .models import Libro 
        libro = Libro.objects.get(id=libro_id) 
        context = { 
            'libro': libro, 
            'puede_prestar': libro.disponible and request.user.is_authenticated 
        } 

        return render(request, 'biblioteca/detalle_libro.html', context) 
    except Libro.DoesNotExist: 

        messages.error(request, 'Libro no encontrado') 
        return redirect('biblioteca:lista_libros') 


def lista_autores(request):
    """Vista que muestra la lista de autores"""
    autores = Autor.objects.all()
    return render(request, 'biblioteca/lista_autores.html', {
        'autores': autores
    })

def detalle_autor(request, autor_id):
    """Vista que muestra el detalle de un autor específico"""
    autor = get_object_or_404(Autor, id=autor_id)
    return render(request, 'biblioteca/detalle_autor.html', {
        'autor': autor
    })


def libros_por_genero(request, genero):
    """Vista que filtra libros por género"""
    generos_disponibles = {
        'ficcion': ['1984', 'El Quijote', 'Cien años de soledad'],
        'ciencia': ['Cosmos', 'Breve historia del tiempo'],
        'historia': ['Sapiens', 'El arte de la guerra']
    }

    if genero in generos_disponibles:
        libros = generos_disponibles[genero]
        html = f"<h1>Libros de {genero.title()}</h1><ul>"
        for libro in libros:
            html += f"<li>{libro}</li>"
        html += "</ul>"
    else:
        html = f"<h1>Género '{genero}' no encontrado</h1>"

    return HttpResponse(html)

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
            return redirect('biblioteca:inicio') 
    else: 

        form = RegistroUsuarioForm() 
    return render(request, 'biblioteca/registro.html', {'form': form}) 

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
                next_page = request.GET.get('next', 'biblioteca:inicio') 
                return redirect(next_page) 
            else: 

                messages.error(request, 'Credenciales inválidas') 

    else: 

        form = LoginForm() 

    return render(request, 'biblioteca/login.html', {'form': form}) 


def logout_usuario(request):
    """Vista para cerrar sesión""" 
    logout(request) 
    messages.info(request, 'Has cerrado sesión exitosamente') 
    return redirect('biblioteca:inicio')

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
            return redirect('biblioteca:perfil') 
    else: 

        form = PerfilUsuarioForm(instance=perfil) 

    # Obtener préstamos del usuario 
    prestamos = Prestamo.objects.filter(usuario=request.user).order_by('-fecha_prestamo')[:5] 
    
    context = { 
        'form': form, 
        'perfil': perfil, 
        'prestamos': prestamos 
    } 
    return render(request, 'biblioteca/perfil.html', context) 

@login_required 
def mis_prestamos(request): 
    """Vista para mostrar los préstamos del usuario""" 
    prestamos = Prestamo.objects.filter(usuario=request.user).order_by('-fecha_prestamo') 

    context = { 
    'prestamos': prestamos 
    } 
    return render(request, 'biblioteca/mis_prestamos.html', context)


###

@login_required
def solicitar_prestamo(request, libro_id):
    """Vista para solicitar préstamo de un libro"""
    libro = get_object_or_404(Libro, id=libro_id)

    # Verificar disponibilidad
    if not libro.disponible:
        messages.error(request, 'Este libro no está disponible')
        return redirect('biblioteca:detalle_libro', libro_id=libro_id)

    # Verificar si el usuario ya tiene este libro prestado
    prestamo_existente = Prestamo.objects.filter(
        usuario=request.user,
        libro=libro,
        estado='activo'
    ).exists()

    if prestamo_existente:
        messages.warning(request, 'Ya tienes este libro en préstamo')
        return redirect('biblioteca:mis_prestamos')

    # Crear el préstamo
    Prestamo.objects.create(
        usuario=request.user,
        libro=libro,
        fecha_devolucion_esperada=date.today() + timedelta(days=14)
    )

    # Marcar libro como no disponible
    libro.disponible = False
    libro.save()

    messages.success(request, f'Préstamo de "{libro.titulo}" solicitado exitosamente')
    return redirect('biblioteca:mis_prestamos')


# Vista Simple API

@api_view(['POST']) 
def obtener_token(request): 
    
    """Vista para obtener token de autenticación""" 
    username = request.data.get('username') 
    password = request.data.get('password') 

    user = authenticate(username=username, password=password)
    if user: 

        token, created = Token.objects.get_or_create(user=user) 
        return Response({ 
        'token': token.key, 
        'user_id': user.id, 
        'username': user.username 
        }) 
    else: 

        return Response({'error': 'Credenciales inválidas'}, status=400) 

@api_view(['GET']) 
@authentication_classes([TokenAuthentication]) 
@permission_classes([IsAuthenticated]) 
def mis_libros_api(request): 

    """API para obtener libros del usuario autenticado""" 
    prestamos = Prestamo.objects.filter(usuario=request.user, estado='activo') 
    libros = [] 

    for prestamo in prestamos: 

        libros.append({ 
            'id': prestamo.libro.id, 
            'titulo': prestamo.libro.titulo, 
            'autor': prestamo.libro.autor.nombre, 
            'fecha_prestamo': prestamo.fecha_prestamo, 
            'fecha_devolucion': prestamo.fecha_devolucion_esperada 
        }) 

    return Response({'libros': libros})


# Vistas busqueda

def busqueda_avanzada(request): 

    """Vista para búsqueda avanzada de libros""" 
    query = request.GET.get('q', '') 
    genero = request.GET.get('genero', '') 
    autor_id = request.GET.get('autor', '') 
    disponible = request.GET.get('disponible', '') 

    # Construir la consulta base 
    libros = Libro.objects.all() 

    # Aplicar filtros 
    if query: 

        libros = libros.filter( 
            Q(titulo__icontains=query) | 
            Q(descripcion__icontains=query) | 
            Q(autor__nombre__icontains=query) | 
            Q(isbn__icontains=query) 
        ) 

    if genero: 

        libros = libros.filter(genero=genero) 

    if autor_id:

        libros = libros.filter(autor_id=autor_id) 

    if disponible: 

        libros = libros.filter(disponible=disponible == 'true') 

    # Ordenar por relevancia (título primero, luego autor) 
    libros = libros.order_by('titulo', 'autor__nombre') 

    # Paginación 
    paginator = Paginator(libros, 10) # 10 libros por página 
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number) 

    # Obtener datos para filtros 
    autores = Autor.objects.all().order_by('nombre') 
    generos = Libro.GENEROS 

    context = { 
    'page_obj': page_obj, 
    'query': query, 
    'genero_seleccionado': genero, 
    'autor_seleccionado': autor_id, 
    'disponible_seleccionado': disponible, 
    'autores': autores, 
    'generos': generos, 
    'total_resultados': libros.count() 
    } 

    return render(request, 'biblioteca/busqueda.html', context) 


def estadisticas_biblioteca(request): 

    """Vista con estadísticas generales de la biblioteca""" 
    from django.db.models import Count, Avg 
    from datetime import date, timedelta 

    # Estadísticas básicas 
    total_libros = Libro.objects.count() 
    total_autores = Autor.objects.count() 
    total_usuarios = User.objects.count() 
    libros_disponibles = Libro.objects.filter(disponible=True).count() 

    # Estadísticas de préstamos 
    prestamos_activos = Prestamo.objects.filter(estado='activo').count() 
    prestamos_vencidos = Prestamo.objects.filter( 
        estado='activo', 
        fecha_devolucion_esperada__lt=date.today() 
    ).count() 

    # Libros más prestados
    libros_populares = Libro.objects.annotate( 
        num_prestamos=Count('prestamos') 
    ).order_by('-num_prestamos')[:5] 

    # Géneros más populares 
    generos_populares = Libro.objects.values('genero').annotate( 
        count=Count('genero')
    ).order_by('-count') 


    # Usuarios más activos 
    usuarios_activos = User.objects.annotate( 
        num_prestamos=Count('prestamos') 
    ).order_by('-num_prestamos')[:5] 

    context = { 
    'total_libros': total_libros, 
    'total_autores': total_autores, 
    'total_usuarios': total_usuarios, 
    'libros_disponibles': libros_disponibles, 
    'prestamos_activos': prestamos_activos, 
    'prestamos_vencidos': prestamos_vencidos, 
    'libros_populares': libros_populares, 
    'generos_populares': generos_populares, 
    'usuarios_activos': usuarios_activos, 
    } 
    return render(request, 'biblioteca/estadisticas.html', context)

#vista dashbord admin
@staff_member_required 
def dashboard_admin(request):
 
    """Dashboard administrativo""" 
    from datetime import date, timedelta 

    # Métricas del último mes 
    hace_un_mes = date.today() - timedelta(days=30) 

    nuevos_usuarios = User.objects.filter(date_joined__gte=hace_un_mes).count() 
    nuevos_libros = Libro.objects.filter(fecha_agregado__gte=hace_un_mes).count() 
    prestamos_mes = Prestamo.objects.filter(fecha_prestamo__gte=hace_un_mes).count()


    # Préstamos por devolver hoy 
    devolver_hoy = Prestamo.objects.filter( 
        estado='activo', 
        fecha_devolucion_esperada=date.today() 
    ) 

    # Préstamos vencidos 
    prestamos_vencidos = Prestamo.objects.filter( 
        estado='activo', 
        fecha_devolucion_esperada__lt=date.today() 
    ) 

    # Actividad reciente 
    actividad_reciente = Prestamo.objects.select_related( 
        'usuario', 'libro' 
    ).order_by('-fecha_prestamo')[:10] 

    context = { 
        'nuevos_usuarios': nuevos_usuarios, 
        'nuevos_libros': nuevos_libros, 
        'prestamos_mes': prestamos_mes, 
        'devolver_hoy': devolver_hoy, 
        'prestamos_vencidos': prestamos_vencidos, 
        'actividad_reciente': actividad_reciente, 
    } 

    return render(request, 'biblioteca/dashboard_admin.html', context) 


@staff_member_required
def gestionar_prestamo(request, prestamo_id):
    """Vista para gestionar préstamos (devolver, renovar)"""
    try:
        prestamo = Prestamo.objects.get(id=prestamo_id)

        if request.method == 'POST':
            accion = request.POST.get('accion')

            if accion == 'devolver':
                from django.utils import timezone
                prestamo.fecha_devolucion_real = timezone.now()
                prestamo.estado = 'devuelto'
                prestamo.save()

                # Marcar libro como disponible
                prestamo.libro.disponible = True
                prestamo.libro.save()
                messages.success(request, f'Libro "{prestamo.libro.titulo}" devuelto exitosamente')

            elif accion == 'renovar':
                from datetime import timedelta
                prestamo.fecha_devolucion_esperada += timedelta(days=14)
                prestamo.save()
                messages.success(request, 'Préstamo renovado por 14 días más')

            return redirect('biblioteca:dashboard_admin')

        # Si es GET, simplemente renderiza la plantilla con los datos del préstamo
        context = {'prestamo': prestamo}
        return render(request, 'biblioteca/gestionar_prestamo.html', context)

    except Prestamo.DoesNotExist:
        messages.error(request, 'Préstamo no encontrado')
        return redirect('biblioteca:dashboard_admin')

    
# Sistema de recomendaciones
@login_required 
def recomendaciones(request): 

    """Vista que muestra recomendaciones personalizadas""" 
    usuario = request.user 

    # Obtener géneros de libros que el usuario ha prestado 
    generos_usuario = Prestamo.objects.filter( 
        usuario=usuario 
    ).values_list('libro__genero', flat=True).distinct() 


    # Obtener autores de libros que el usuario ha prestado 
    autores_usuario = Prestamo.objects.filter( 
        usuario=usuario 
    ).values_list('libro__autor', flat=True).distinct() 

    recomendaciones = [] 
    
    libros_mismo_genero = []
    libros_mismo_autor = []

    # Recomendar libros del mismo género 
    if generos_usuario: 

        libros_mismo_genero = Libro.objects.filter( 
            genero__in=generos_usuario, 
            disponible=True
        ).exclude( 
            prestamos__usuario=usuario 
        ).distinct()[:5] 

    if libros_mismo_genero: 

        recomendaciones.append({ 
            'titulo': 'Basado en tus géneros favoritos', 
            'libros': libros_mismo_genero 
        }) 

    # Recomendar libros de los mismos autores 
    if autores_usuario: 

        libros_mismo_autor = Libro.objects.filter( 
            autor__in=autores_usuario, 
            disponible=True 
        ).exclude( 
            prestamos__usuario=usuario 
        ).distinct()[:5] 

        if libros_mismo_autor: 

            recomendaciones.append({ 
                'titulo': 'Más libros de tus autores favoritos', 
                'libros': libros_mismo_autor 
            }) 

    # Libros populares (más prestados) 
    libros_populares = Libro.objects.annotate( 
        num_prestamos=Count('prestamos') 
    ).filter( 
    disponible=True, 
        num_prestamos__gt=0 
    ).exclude( 
        prestamos__usuario=usuario 
    ).order_by('-num_prestamos')[:5] 

    if libros_populares: 
        recomendaciones.append({ 
            'titulo': 'Libros populares', 
            'libros': libros_populares 
        }) 

    # Si no hay recomendaciones personalizadas, mostrar novedades 
    if not recomendaciones: 

        novedades = Libro.objects.filter( 
            disponible=True 
        ).order_by('-fecha_agregado')[:10]

        recomendaciones.append({ 
            'titulo': 'Novedades en la biblioteca', 
            'libros': novedades 
        }) 

    context = { 
        'recomendaciones': recomendaciones, 
        'tiene_historial': bool(generos_usuario or autores_usuario) 
    } 

    return render(request, 'biblioteca/recomendaciones.html', context)

#vista serializer
class LibroViewSet(viewsets.ReadOnlyModelViewSet): 

    """ViewSet para libros - solo lectura""" 
    queryset = Libro.objects.all() 
    serializer_class = LibroSerializer 
    authentication_classes = [TokenAuthentication] 
    permission_classes = [IsAuthenticated] 


    def get_queryset(self): 

        queryset = Libro.objects.all() 
        genero = self.request.query_params.get('genero', None) 
        disponible = self.request.query_params.get('disponible', None) 

        if genero: 

            queryset = queryset.filter(genero=genero) 
        if disponible: 

            queryset = queryset.filter(disponible=disponible.lower() == 'true') 

        return queryset 


    @action(detail=True, methods=['post']) 
    def solicitar_prestamo(self, request, pk=None): 

        """Endpoint para solicitar préstamo de un libro"""
        libro = self.get_object() 

        if not libro.disponible: 

            return Response( 
                {'error': 'Libro no disponible'}, 
                status=status.HTTP_400_BAD_REQUEST 
            ) 

        # Verificar si ya tiene el libro prestado 
        prestamo_existente = Prestamo.objects.filter( 
            usuario=request.user, 
            libro=libro, 
            estado='activo' 
        ).exists() 

        if prestamo_existente: 

            return Response( 
                {'error': 'Ya tienes este libro en préstamo'},
                status=status.HTTP_400_BAD_REQUEST
            ) 

        # Crear préstamo 
        from datetime import date, timedelta 
        prestamo = Prestamo.objects.create( 
            usuario=request.user, 
            libro=libro, 
            fecha_devolucion_esperada=date.today() + timedelta(days=14) 
        ) 

        libro.disponible = False 
        libro.save() 

        return Response( 
            {'message': 'Préstamo solicitado exitosamente'}, 
            status=status.HTTP_201_CREATED 
        ) 

class MisPrestamoViewSet(viewsets.ReadOnlyModelViewSet): 

    """ViewSet para préstamos del usuario autenticado""" 
    serializer_class = PrestamoSerializer 
    authentication_classes = [TokenAuthentication] 
    permission_classes = [IsAuthenticated] 

    def get_queryset(self): 

        return Prestamo.objects.filter(usuario=self.request.user)


#vista optimizacion 
class LibroListView(ListView): 

    """Vista optimizada para listar libros""" 
    model = Libro 
    template_name = 'biblioteca/lista_libros_optimizada.html' 
    context_object_name = 'libros' 
    paginate_by = 20 

    def get_queryset(self): 

        # Optimizar consultas con select_related y prefetch_related 
        return Libro.objects.select_related('autor').prefetch_related( 
            Prefetch('prestamos', queryset=Prestamo.objects.filter(estado='activo')
        ) 
        ).order_by('-fecha_agregado')

    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs) 
        context['generos'] = Libro.GENEROS 
        context['total_libros'] = self.get_queryset().count() 
        return context 

# Función para generar reportes 
@staff_member_required 
def generar_reporte_prestamos(request): 

    """Genera reporte de préstamos en formato CSV""" 
    import csv 
    from django.http import HttpResponse 
    from datetime import date 

    response = HttpResponse(content_type='text/csv') 
    response['Content-Disposition'] = f'attachment; filename="prestamos_{date.today()}.csv"' 

    writer = csv.writer(response) 
    writer.writerow(['Usuario', 'Libro', 'Autor', 'Fecha Préstamo', 'Fecha Devolución', 'Estado']) 

    prestamos = Prestamo.objects.select_related( 
        'usuario', 'libro', 'libro__autor' 
    ).order_by('-fecha_prestamo') 

    for prestamo in prestamos: 

        writer.writerow([ 
        prestamo.usuario.get_full_name() or prestamo.usuario.username, 
        prestamo.libro.titulo, 
        prestamo.libro.autor.nombre, 
        prestamo.fecha_prestamo.strftime('%Y-%m-%d'), 
        prestamo.fecha_devolucion_esperada.strftime('%Y-%m-%d'), 
        prestamo.get_estado_display() 
    ]) 
        
    return response



