# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, F
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from decimal import Decimal, InvalidOperation
import csv

from .models import (
    Usuario, Producto, Proveedor, ProductoProveedor, 
    Bodega, MovimientoInventario, Categoria, Venta, DetalleVenta
)
from .forms import (
    UsuarioForm, ProductoPaso1Form, ProductoPaso2Form, ProductoPaso3Form,
    ProveedorPaso1Form, ProveedorPaso2Form, ProveedorPaso3Form,
    MovimientoPaso1Form, MovimientoPaso2Form, MovimientoPaso3Form,
    VentaForm, DetalleVentaForm
)
from .decorators import admin_required, vendedor_o_admin, bodeguero_required


# ===============================================
# AUTENTICACIÓN
# ===============================================
def login_view(request):
    """Vista de inicio de sesión SOLO con correo"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember')

        UserModel = get_user_model()
        user_obj = UserModel.objects.filter(email__iexact=email).first()

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
        else:
            user = None

        if user is not None:
            login(request, user)
            request.session.set_expiry(1209600 if remember else 0)

            if hasattr(user, 'perfil'):
                user.perfil.ultimo_acceso = timezone.now()
                user.perfil.save()

            messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.email}!')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Correo o contraseña incorrectos')
            return render(request, 'auth/login.html', {'username': email})

    return render(request, 'auth/login.html')


@login_required
def dashboard(request):
    """Página principal después del login"""
    context = {
        'total_usuarios': Usuario.objects.filter(user__is_active=True).count(),
        'total_productos': Producto.objects.filter(activo=True).count(),
        'total_proveedores': Proveedor.objects.filter(estado='ACTIVO').count(),
        'total_movimientos': MovimientoInventario.objects.count(),
        'productos_bajo_stock': Producto.objects.filter(alerta_bajo_stock=True).count(),
    }
    return render(request, 'dashboard.html', context)


@login_required
def logout_view(request):
    """Cerrar sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('core:login')


def recuperar_password(request):
    return render(request, 'auth/recuperar_password.html')


def validar_token(request, token=None):
    return render(request, 'auth/validar_token.html', {'token': token})


def nueva_password(request):
    return render(request, 'auth/nueva_password.html')


# ===============================================
# USUARIOS - CRUD
# ===============================================
@login_required
def lista_usuarios(request):
    q = request.GET.get('q', '')
    rol = request.GET.get('rol', '')
    estado = request.GET.get('estado', '')

    usuarios = Usuario.objects.select_related('user').all()

    if q:
        usuarios = usuarios.filter(
            Q(user__username__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__email__icontains=q)
        )
    if rol:
        usuarios = usuarios.filter(rol__iexact=rol)
    if estado:
        usuarios = usuarios.filter(estado__iexact=estado)

    usuarios = usuarios.order_by('user__username')
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})


@login_required
@transaction.atomic
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            nombres = form.cleaned_data['nombres']
            apellidos = form.cleaned_data['apellidos']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=nombres,
                last_name=apellidos
            )

            usuario = form.save(commit=False)
            usuario.user = user
            usuario.save()

            messages.success(request, f'Usuario {username} creado exitosamente.')
            return redirect('core:lista_usuarios')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/crear_usuario.html', {'form': form})


@login_required
@transaction.atomic
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    user = usuario.user

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['nombres']
            user.last_name = form.cleaned_data['apellidos']
            password = form.cleaned_data.get('password')

            if password:
                user.set_password(password)
            user.save()
            form.save()

            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('core:lista_usuarios')
        else:
            messages.error(request, 'Corrige los errores antes de continuar.')
    else:
        initial_data = {
            'username': user.username,
            'email': user.email,
            'nombres': user.first_name,
            'apellidos': user.last_name,
        }
        form = UsuarioForm(instance=usuario, initial=initial_data)

    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})


@login_required
@transaction.atomic
def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    nombre = usuario.user.get_full_name() or usuario.user.username

    if request.method == 'POST':
        usuario.user.delete()
        messages.success(request, f'Usuario {nombre} eliminado correctamente.')
        return redirect('core:lista_usuarios')

    return render(request, 'usuarios/confirmar_eliminar.html', {'usuario': usuario})


# ===============================================
# PRODUCTOS - CRUD CON WIZARD DE 3 PASOS
# ===============================================
@login_required
def crear_producto(request):
    """Redirige al Paso 1 del asistente"""
    return redirect('core:producto_paso1')


@login_required
@transaction.atomic
def producto_paso1(request):
    """Paso 1: Información básica + Unidades + Precios"""
    if request.method == 'POST':
        form = ProductoPaso1Form(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.costo_promedio = 0  # Se calculará con movimientos
            producto.save()
            
            request.session['producto_id'] = producto.id
            messages.success(request, '✓ Paso 1 completado. Continúa con el Paso 2.')
            return redirect('core:producto_paso2')
    else:
        form = ProductoPaso1Form()
    
    return render(request, 'productos/producto_paso1.html', {'form': form})


@login_required
@transaction.atomic
def producto_paso2(request):
    """Paso 2: Stock y características"""
    producto_id = request.session.get('producto_id')
    if not producto_id:
        messages.error(request, 'Debes completar el Paso 1 primero.')
        return redirect('core:producto_paso1')
    
    producto = get_object_or_404(Producto, pk=producto_id)
    
    if request.method == 'POST':
        form = ProductoPaso2Form(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Paso 2 completado. Continúa con el Paso 3.')
            return redirect('core:producto_paso3')
        else:
            messages.error(request, '⚠️ Por favor corrige los errores del formulario.')
    else:
        form = ProductoPaso2Form(instance=producto)
    
    return render(request, 'productos/producto_paso2.html', {
        'form': form,
        'producto': producto
    })


@login_required
@transaction.atomic
def producto_paso3(request):
    """Paso 3: URLs opcionales"""
    producto_id = request.session.get('producto_id')
    if not producto_id:
        messages.error(request, 'Debes completar el Paso 1 primero.')
        return redirect('core:producto_paso1')
    
    producto = get_object_or_404(Producto, pk=producto_id)
    
    if request.method == 'POST':
        form = ProductoPaso3Form(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            del request.session['producto_id']
            messages.success(request, f'✓ Producto {producto.sku} creado exitosamente.')
            return redirect('core:lista_productos')
    else:
        form = ProductoPaso3Form(instance=producto)
    
    return render(request, 'productos/producto_paso3.html', {
        'form': form,
        'producto': producto
    })


@login_required
def editar_producto(request, pk):
    """Vista stub para editar producto"""
    producto = get_object_or_404(Producto, pk=pk)
    messages.info(request, f'Edición de {producto.nombre} - Próximamente')
    return redirect('core:lista_productos')


@login_required
@require_POST
def eliminar_producto(request, pk):
    """Desactiva un producto (no lo elimina físicamente)"""
    producto = get_object_or_404(Producto, pk=pk)
    try:
        producto.activo = False
        producto.save()
        messages.success(request, f'✓ Producto "{producto.nombre}" desactivado correctamente')
    except Exception as e:
        messages.error(request, f'❌ Error: {str(e)}')
    return redirect('core:lista_productos')


@login_required
@vendedor_o_admin
def lista_productos(request):
    """Lista paginada de productos con filtros"""
    qs = Producto.objects.select_related('categoria')
    
    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(Q(sku__icontains=q) | Q(nombre__icontains=q) | Q(categoria__nombre__icontains=q))
    
    categoria_filtro = (request.GET.get('categoria') or '').strip()
    if categoria_filtro:
        qs = qs.filter(categoria__nombre=categoria_filtro)
    
    estado_filtro = (request.GET.get('estado') or '').strip()
    if estado_filtro == 'bajo':
        qs = qs.filter(stock_actual__lte=F('stock_minimo'))
    elif estado_filtro == 'ok':
        qs = qs.filter(stock_actual__gt=F('stock_minimo'))
    
    orden = (request.GET.get('orden') or 'nombre').strip()
    orden_map = {
        'nombre': 'nombre', '-nombre': '-nombre',
        'sku': 'sku', 'precio': 'precio_venta',
        '-precio': '-precio_venta', 'stock': 'stock_actual',
        '-stock': '-stock_actual'
    }
    qs = qs.order_by(orden_map.get(orden, 'nombre'))

    page_obj = Paginator(qs, 20).get_page(request.GET.get('page'))
    
    return render(request, 'productos/lista_productos.html', {
        'productos': page_obj,
        'categorias': Categoria.objects.order_by('nombre'),
        'query': q,
        'categoria_filtro': categoria_filtro,
        'estado_filtro': estado_filtro,
        'orden': orden,
    })


@login_required
def exportar_productos_excel(request):
    """Exporta productos a CSV"""
    qs = Producto.objects.select_related('categoria').order_by('sku')
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename=productos.csv'
    writer = csv.writer(response)
    writer.writerow(['SKU', 'Nombre', 'Categoría', 'Stock', 'Precio Venta'])
    for p in qs:
        writer.writerow([
            p.sku,
            p.nombre,
            getattr(p.categoria, 'nombre', ''),
            p.stock_actual,
            int(p.precio_venta or 0)
        ])
    return response


# ===============================================
# PROVEEDORES - CRUD + LISTAS
# ===============================================
@login_required
def lista_proveedores(request):
    """Lista de proveedores con filtros"""
    proveedores = Proveedor.objects.all().order_by('razon_social')
    return render(request, 'proveedores/lista_proveedores.html', {'proveedores': proveedores})


@login_required
@admin_required
def crear_proveedor(request):
    """Redirige al wizard de proveedores"""
    return redirect('core:proveedor_paso1')


@login_required
@admin_required
@transaction.atomic
def proveedor_paso1(request):
    """Paso 1: Información básica del proveedor"""
    if request.method == 'POST':
        form = ProveedorPaso1Form(request.POST)
        if form.is_valid():
            proveedor = form.save()
            request.session['proveedor_id'] = proveedor.id
            messages.success(request, '✓ Paso 1 completado. Continúa con el Paso 2.')
            return redirect('core:proveedor_paso2')
    else:
        form = ProveedorPaso1Form()
    
    return render(request, 'proveedores/proveedor_paso1.html', {'form': form})


@login_required
@admin_required
@transaction.atomic
def proveedor_paso2(request):
    """Paso 2: Dirección y contacto"""
    proveedor_id = request.session.get('proveedor_id')
    if not proveedor_id:
        messages.error(request, 'Debes completar el Paso 1 primero.')
        return redirect('core:proveedor_paso1')
    
    proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
    
    if request.method == 'POST':
        form = ProveedorPaso2Form(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Paso 2 completado. Continúa con el Paso 3.')
            return redirect('core:proveedor_paso3')
    else:
        form = ProveedorPaso2Form(instance=proveedor)
    
    return render(request, 'proveedores/proveedor_paso2.html', {
        'form': form,
        'proveedor': proveedor
    })


@login_required
@admin_required
@transaction.atomic
def proveedor_paso3(request):
    """Paso 3: Observaciones finales"""
    proveedor_id = request.session.get('proveedor_id')
    if not proveedor_id:
        messages.error(request, 'Debes completar el Paso 1 primero.')
        return redirect('core:proveedor_paso1')
    
    proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
    
    if request.method == 'POST':
        form = ProveedorPaso3Form(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            del request.session['proveedor_id']
            messages.success(request, f'✓ Proveedor {proveedor.razon_social} creado exitosamente.')
            return redirect('core:lista_proveedores')
    else:
        form = ProveedorPaso3Form(instance=proveedor)
    
    return render(request, 'proveedores/proveedor_paso3.html', {
        'form': form,
        'proveedor': proveedor
    })


@login_required
@admin_required
def editar_proveedor(request, pk):
    """Editar proveedor existente"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    messages.info(request, f'Edición de {proveedor.razon_social} - Próximamente')
    return redirect('core:lista_proveedores')


@login_required
@admin_required
@require_POST
def eliminar_proveedor(request, pk):
    """Desactiva un proveedor"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    try:
        proveedor.estado = 'INACTIVO'
        proveedor.save()
        messages.success(request, f'✓ Proveedor "{proveedor.razon_social}" desactivado')
    except Exception as e:
        messages.error(request, f'❌ Error: {str(e)}')
    return redirect('core:lista_proveedores')


# ===============================================
# MOVIMIENTOS - CRUD
# ===============================================
@login_required
def lista_movimientos(request):
    """Lista de movimientos de inventario"""
    movimientos = MovimientoInventario.objects.select_related('producto', 'bodega').order_by('-fecha')[:100]
    return render(request, 'movimientos/lista_movimientos.html', {'movimientos': movimientos})


@login_required
@bodeguero_required
def crear_movimiento(request):
    """Redirige al wizard de movimientos"""
    return redirect('core:movimiento_paso1')


@login_required
@bodeguero_required
@transaction.atomic
def movimiento_paso1(request):
    """Paso 1: Datos básicos del movimiento"""
    if request.method == 'POST':
        form = MovimientoPaso1Form(request.POST)
        if form.is_valid():
            producto_sku = form.cleaned_data['producto_sku']
            bodega_codigo = form.cleaned_data['bodega_codigo']
            
            try:
                producto = Producto.objects.get(sku=producto_sku)
                bodega = Bodega.objects.get(codigo=bodega_codigo)
            except Producto.DoesNotExist:
                messages.error(request, f'Producto con SKU "{producto_sku}" no existe')
                return render(request, 'movimientos/movimiento_paso1.html', {'form': form})
            except Bodega.DoesNotExist:
                messages.error(request, f'Bodega con código "{bodega_codigo}" no existe')
                return render(request, 'movimientos/movimiento_paso1.html', {'form': form})
            
            movimiento = form.save(commit=False)
            movimiento.producto = producto
            movimiento.bodega = bodega
            movimiento.usuario = request.user.perfil
            movimiento.save()
            
            request.session['movimiento_id'] = movimiento.id
            messages.success(request, '✓ Paso 1 completado. Continúa con el Paso 2.')
            return redirect('core:movimiento_paso2')
    else:
        form = MovimientoPaso1Form()
    
    return render(request, 'movimientos/movimiento_paso1.html', {'form': form})


@login_required
@bodeguero_required
@transaction.atomic
def movimiento_paso2(request):
    """Paso 2: Lote, serie y vencimiento"""
    movimiento_id = request.session.get('movimiento_id')
    if not movimiento_id:
        messages.error(request, 'Debes completar el Paso 1 primero.')
        return redirect('core:movimiento_paso1')
    
    movimiento = get_object_or_404(MovimientoInventario, pk=movimiento_id)
    
    if request.method == 'POST':
        form = MovimientoPaso2Form(request.POST, instance=movimiento)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Paso 2 completado. Continúa con el Paso 3.')
            return redirect('core:movimiento_paso3')
    else:
        form = MovimientoPaso2Form(instance=movimiento)
    
    return render(request, 'movimientos/movimiento_paso2.html', {
        'form': form,
        'movimiento': movimiento
    })


@login_required
@bodeguero_required
@transaction.atomic
def movimiento_paso3(request):
    """Paso 3: Documentos y observaciones"""
    movimiento_id = request.session.get('movimiento_id')
    if not movimiento_id:
        messages.error(request, 'Debes completar el Paso 1 primero.')
        return redirect('core:movimiento_paso1')
    
    movimiento = get_object_or_404(MovimientoInventario, pk=movimiento_id)
    
    if request.method == 'POST':
        form = MovimientoPaso3Form(request.POST, instance=movimiento)
        if form.is_valid():
            form.save()
            del request.session['movimiento_id']
            messages.success(request, '✓ Movimiento registrado exitosamente.')
            return redirect('core:lista_movimientos')
    else:
        form = MovimientoPaso3Form(instance=movimiento)
    
    return render(request, 'movimientos/movimiento_paso3.html', {
        'form': form,
        'movimiento': movimiento
    })


# ===============================================
# VENTAS - CRUD
# ===============================================
@login_required
def lista_ventas(request):
    """Lista de ventas"""
    ventas = Venta.objects.select_related('usuario').order_by('-fecha')[:100]
    return render(request, 'ventas/lista_ventas.html', {'ventas': ventas})