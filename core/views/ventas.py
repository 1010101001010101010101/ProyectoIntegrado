from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import Venta


@login_required
def lista_ventas(request):
    """Lista de ventas"""
    ventas = Venta.objects.select_related('usuario').order_by('-fecha')[:100]
    return render(request, 'ventas/lista_ventas.html', {'ventas': ventas})


@login_required
def crear_venta(request):
    """Crear venta (placeholder)"""
    messages.info(request, 'Módulo de ventas - Próximamente')
    return redirect('core:lista_ventas')


@login_required
def detalle_venta(request, pk):
    """Detalle de venta"""
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, 'ventas/detalle_venta.html', {'venta': venta})