from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import datetime

from ..decorators import bodeguero_required
from ..models import MovimientoInventario, Producto, Bodega, Proveedor, Usuario
from ..forms import MovimientoPaso1Form, MovimientoPaso2Form, MovimientoPaso3Form


@login_required
def lista_movimientos(request):
    """Lista de movimientos"""
    base_qs = MovimientoInventario.objects.select_related('producto', 'bodega')
    total = base_qs.count()
    ingresos = base_qs.filter(tipo_movimiento='ingreso').count()
    salidas = base_qs.filter(tipo_movimiento='salida').count()
    este_mes = base_qs.filter(fecha__month=timezone.now().month, fecha__year=timezone.now().year).count()
    movimientos = base_qs.order_by('-fecha')[:100]
    contexto = {
        'movimientos': movimientos,
        'total_movimientos': total,
        'total_ingresos': ingresos,
        'total_salidas': salidas,
        'total_mes': este_mes,
    }
    return render(request, 'inventario/lista_movimientos.html', contexto)


@login_required
@bodeguero_required
def crear_movimiento(request):
    """Redirige al wizard"""
    return redirect('core:movimiento_paso1')


@login_required
@bodeguero_required
@transaction.atomic
def movimiento_paso1(request):
    productos = Producto.objects.all()
    bodegas = Bodega.objects.all()
    proveedores = Proveedor.objects.all()
    data = {}

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        tipo = request.POST.get('tipo')
        cantidad = request.POST.get('cantidad')
        producto_sku = request.POST.get('producto')
        proveedor_rut = request.POST.get('proveedor')
        bodega_codigo = request.POST.get('bodega')

        # Guarda los datos para volver a mostrar si hay error
        data = {
            'fecha': fecha,
            'tipo': tipo,
            'cantidad': cantidad,
            'producto': producto_sku,
            'proveedor': proveedor_rut,
            'bodega': bodega_codigo,
        }

        # Validación de campos obligatorios
        if not (fecha and tipo and cantidad and producto_sku and bodega_codigo):
            messages.error(request, "Todos los campos obligatorios deben estar completos.")
            return render(request, 'inventario/movimiento_paso1.html', {'data': data, 'productos': productos, 'bodegas': bodegas})

        # Validación de fecha
        try:
            fecha_dt = datetime.datetime.strptime(fecha, "%Y-%m-%dT%H:%M")
            fecha_dt = timezone.make_aware(fecha_dt)
        except Exception:
            messages.error(request, "Formato de fecha inválido.")
            return render(request, 'inventario/movimiento_paso1.html', {'data': data, 'productos': productos, 'bodegas': bodegas})

        if fecha_dt > timezone.now():
            messages.error(request, "No se puede registrar un movimiento con fecha futura.")
            return render(request, 'inventario/movimiento_paso1.html', {'data': data, 'productos': productos, 'bodegas': bodegas})

        # Buscar relaciones
        try:
            producto = Producto.objects.get(sku=producto_sku)
        except Producto.DoesNotExist:
            print("ERROR: Producto no existe:", producto_sku)
            messages.error(request, f'El producto con SKU "{producto_sku}" no existe.')
            return render(request, 'inventario/movimiento_paso1.html', {'data': data, 'productos': productos, 'bodegas': bodegas})

        try:
            bodega = Bodega.objects.get(codigo=bodega_codigo)
        except Bodega.DoesNotExist:
            print("ERROR: Bodega no existe:", bodega_codigo)
            messages.error(request, f'La bodega con código "{bodega_codigo}" no existe.')
            return render(request, 'inventario/movimiento_paso1.html', {'data': data, 'productos': productos, 'bodegas': bodegas})

        # Buscar proveedor si se ingresó
        proveedor = None
        if proveedor_rut:
            try:
                proveedor = Proveedor.objects.get(rut=proveedor_rut)
            except Proveedor.DoesNotExist:
                proveedor = None  # Opcional

        # Coloca aquí los print para depuración
        print("Datos recibidos:", fecha, tipo, cantidad, producto_sku, proveedor_rut, bodega_codigo)
        print("Producto:", producto)
        print("Bodega:", bodega)
        print("Proveedor:", proveedor)

        # Obtener el usuario de inventario
        try:
            usuario_inventario = Usuario.objects.get(user=request.user)
        except Usuario.DoesNotExist:
            messages.error(request, "No se encontró el perfil de usuario.")
            return render(request, 'inventario/movimiento_paso1.html', {
                'data': data,
                'productos': productos,
                'bodegas': bodegas,
                'proveedores': proveedores,
            })

        # Crear el movimiento
        movimiento = MovimientoInventario.objects.create(
            fecha=fecha_dt,
            tipo_movimiento=tipo,
            cantidad=cantidad,
            producto=producto,
            bodega=bodega,
            usuario=usuario_inventario,  # <-- Aquí va el usuario correcto
            proveedor=proveedor,
        )

        # Guarda el ID en sesión para los siguientes pasos
        request.session['movimiento_id'] = movimiento.id

        # Redirige al paso 2
        return redirect('core:movimiento_paso2')

    # Si es GET, muestra el formulario vacío
    return render(request, 'inventario/movimiento_paso1.html', {
        'data': data,
        'productos': productos,
        'bodegas': bodegas,
        'proveedores': proveedores,
    })

@login_required
@bodeguero_required
@transaction.atomic
def movimiento_paso2(request):
    """Paso 2: Lote y serie"""
    movimiento_id = request.session.get('movimiento_id')
    if not movimiento_id:
        messages.error(request, 'Debes completar el Paso 1 primero')
        return redirect('core:movimiento_paso1')
    
    movimiento = get_object_or_404(MovimientoInventario, pk=movimiento_id)
    
    if request.method == 'POST':
        form = MovimientoPaso2Form(request.POST, instance=movimiento)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Paso 2 completado')
            return redirect('core:movimiento_paso3')
    else:
        form = MovimientoPaso2Form(instance=movimiento)
    
    return render(request, 'inventario/movimiento_paso2.html', {
        'form': form,
        'movimiento': movimiento
    })

@login_required
@bodeguero_required
@transaction.atomic
def movimiento_paso3(request):
    """Paso 3: Documentos"""
    movimiento_id = request.session.get('movimiento_id')
    if not movimiento_id:
        messages.error(request, 'Debes completar el Paso 1 primero')
        return redirect('core:movimiento_paso1')
    
    movimiento = get_object_or_404(MovimientoInventario, pk=movimiento_id)
    
    if request.method == 'POST':
        form = MovimientoPaso3Form(request.POST, instance=movimiento)
        if form.is_valid():
            form.save()
            del request.session['movimiento_id']
            messages.success(request, '✓ Movimiento registrado')
            return redirect('core:lista_movimientos')
    else:
        form = MovimientoPaso3Form(instance=movimiento)
    
    return render(request, 'inventario/movimiento_paso3.html', {
        'form': form,
        'movimiento': movimiento
    })


def editar_movimiento(request, pk):
    movimiento = get_object_or_404(MovimientoInventario, pk=pk)
    return render(request, 'inventario/editar_movimiento.html', {'movimiento': movimiento})

def movimiento_editar_paso1(request, pk):
    movimiento = get_object_or_404(MovimientoInventario, pk=pk)
    form = MovimientoPaso1Form(instance=movimiento)
    return render(request, 'inventario/movimiento_paso1.html', {'form': form, 'movimiento': movimiento})