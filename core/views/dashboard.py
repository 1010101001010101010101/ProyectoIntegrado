"""
Vista del Dashboard con estadísticas y gráficos
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from decimal import Decimal
import json

from ..models import Producto, MovimientoInventario, Proveedor, Usuario
from ..decorators import lector_o_superior


@login_required
@lector_o_superior
def dashboard_view(request):
    """
    Dashboard principal con métricas y gráficos
    """
    # ========================================
    # 1. ESTADÍSTICAS GENERALES
    # ========================================
    total_productos = Producto.objects.filter(activo=True).count()
    
    productos_bajo_stock = Producto.objects.filter(
        alerta_bajo_stock=True,
        activo=True
    ).count()
    
    # Movimientos del mes actual
    hoy = datetime.now()
    primer_dia_mes = hoy.replace(day=1)
    movimientos_mes = MovimientoInventario.objects.filter(
        fecha__gte=primer_dia_mes,
        fecha__lte=hoy
    ).count()
    
    # Proveedores activos
    proveedores_activos = Proveedor.objects.filter(
        estado='ACTIVO'
    ).count()
    
    # ========================================
    # 2. DATOS PARA GRÁFICO DE MOVIMIENTOS POR MES
    # ========================================
    # Últimos 6 meses
    seis_meses_atras = hoy - timedelta(days=180)
    
    # Obtener movimientos agrupados por tipo y mes
    movimientos_raw = MovimientoInventario.objects.filter(
        fecha__gte=seis_meses_atras
    ).values('tipo_movimiento', 'fecha__month').annotate(
        total=Count('id')
    )
    
    # Preparar estructura para los últimos 6 meses
    meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    meses_labels = []
    ingresos_data = []
    salidas_data = []
    ajustes_data = []
    
    for i in range(5, -1, -1):  # Últimos 6 meses
        mes = (hoy.month - i) % 12
        if mes == 0:
            mes = 12
        meses_labels.append(meses_nombres[mes - 1])
        
        # Contar movimientos de cada tipo para este mes
        ingresos = sum(m['total'] for m in movimientos_raw 
                      if m['fecha__month'] == mes and m['tipo_movimiento'] == 'ingreso')
        salidas = sum(m['total'] for m in movimientos_raw 
                     if m['fecha__month'] == mes and m['tipo_movimiento'] == 'salida')
        ajustes = sum(m['total'] for m in movimientos_raw 
                     if m['fecha__month'] == mes and m['tipo_movimiento'] == 'ajuste')
        
        ingresos_data.append(ingresos)
        salidas_data.append(salidas)
        ajustes_data.append(ajustes)
    
    # ========================================
    # 3. DATOS PARA GRÁFICO DE ESTADO DEL STOCK
    # ========================================
    productos_totales = Producto.objects.filter(activo=True)
    
    stock_ok = productos_totales.filter(
        alerta_bajo_stock=False,
        stock_actual__gt=0
    ).count()
    
    sin_stock = productos_totales.filter(
        stock_actual=0
    ).count()
    
    stock_data = [stock_ok, productos_bajo_stock, sin_stock]
    
    # ========================================
    # 4. TOP 5 PRODUCTOS CON MÁS MOVIMIENTOS
    # ========================================
    top_productos = MovimientoInventario.objects.values(
        'producto__nombre'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    top_productos_labels = [p['producto__nombre'][:25] for p in top_productos]  # Limitar largo
    top_productos_data = [p['total'] for p in top_productos]
    
    # ========================================
    # 5. PROVEEDORES MÁS ACTIVOS
    # ========================================
    top_proveedores = MovimientoInventario.objects.filter(
        proveedor__isnull=False
    ).values('proveedor__razon_social').annotate(
        total=Count('id')
    ).order_by('-total')[:4]
    
    proveedores_labels = [p['proveedor__razon_social'][:20] for p in top_proveedores]
    proveedores_data = [p['total'] for p in top_proveedores]
    
    # ========================================
    # 6. PERMISOS SEGÚN ROL
    # ========================================
    usuario = request.user.perfil if hasattr(request.user, 'perfil') else None
    
    permisos_dashboard = {
        'usuarios': usuario and usuario.rol in ['ADMIN', 'EDITOR', 'BODEGA'],
        'productos': True,  # Todos pueden ver productos
        'proveedores': True,  # Todos pueden ver proveedores
        'movimientos': True,  # Todos pueden ver movimientos
    }
    
    # ========================================
    # 7. CONTEXTO PARA EL TEMPLATE
    # ========================================
    context = {
        # Estadísticas
        'total_productos': total_productos,
        'movimientos_mes': movimientos_mes,
        'proveedores_activos': proveedores_activos,
        'productos_bajo_stock': productos_bajo_stock,
        
        # Gráfico 1: Movimientos por mes
        'meses_labels': json.dumps(meses_labels),
        'ingresos_data': json.dumps(ingresos_data),
        'salidas_data': json.dumps(salidas_data),
        'ajustes_data': json.dumps(ajustes_data),
        
        # Gráfico 2: Estado del stock
        'stock_data': json.dumps(stock_data),
        
        # Gráfico 3: Top productos
        'top_productos_labels': json.dumps(top_productos_labels),
        'top_productos_data': json.dumps(top_productos_data),
        
        # Gráfico 4: Proveedores activos
        'proveedores_labels': json.dumps(proveedores_labels),
        'proveedores_data': json.dumps(proveedores_data),
        
        # Permisos
        'permisos_dashboard': permisos_dashboard,
    }
    
    return render(request, 'dashboard/dashboard.html', context)