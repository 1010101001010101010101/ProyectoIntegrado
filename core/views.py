from django.shortcuts import render, redirect




def login_view(request):
    if request.method == 'POST':
        return redirect('core:dashboard')
    return render(request, 'login.html')

def recuperar_password(request):
    """Vista para solicitar recuperación de contraseña"""
    if request.method == 'POST':
        email = request.POST.get('email')
        # Aquí implementarías el envío de email con el token
        # Por ahora solo redirigimos mostrando un mensaje de éxito
        return render(request, 'auth/recuperar_password.html', {'success': True})
    
    return render(request, 'auth/recuperar_password.html')

def validar_token(request, token=None):
    """Vista para validar el token enviado por correo"""
    # Aquí validarías el token
    # Si es válido, redirige a crear nueva contraseña
    # Por ahora asumimos que es válido
    if token:
        # Verificar que el token sea válido
        return redirect('core:nueva_password')
    
    # Si no hay token, mostrar error o redirigir
    return redirect('core:recuperar_password')

def nueva_password(request):
    """Vista para crear nueva contraseña"""
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            return render(request, 'auth/nueva_password.html', {
                'error': 'Las contraseñas no coinciden'
            })
        
        if len(password) < 8:
            return render(request, 'auth/nueva_password.html', {
                'error': 'La contraseña debe tener al menos 8 caracteres'
            })
        
        # Aquí guardarías la nueva contraseña en la base de datos
        # Por ahora solo redirigimos al login
        return redirect('core:login')
    
    return render(request, 'auth/nueva_password.html')

def dashboard(request):
    context = {
        'total_usuarios': 25,
        'total_productos': 150,
        'total_proveedores': 12,
        'total_movimientos': 342
    }
    return render(request, 'dashboard.html', context)

def lista_usuarios(request):
    return render(request, 'usuarios/lista_usuarios.html')

def crear_usuario(request):
    return render(request, 'usuarios/crear_usuario.html')

def producto_paso1(request):
    if request.method == 'POST':
        if 'producto_data' not in request.session:
            request.session['producto_data'] = {}
        
        request.session['producto_data']['sku'] = request.POST.get('sku')
        request.session['producto_data']['ean_upc'] = request.POST.get('ean_upc')
        request.session['producto_data']['nombre'] = request.POST.get('nombre')
        request.session['producto_data']['descripcion'] = request.POST.get('descripcion')
        request.session['producto_data']['categoria'] = request.POST.get('categoria')
        request.session['producto_data']['marca'] = request.POST.get('marca')
        request.session['producto_data']['modelo'] = request.POST.get('modelo')
        request.session['producto_data']['uom_compra'] = request.POST.get('uom_compra')
        request.session['producto_data']['uom_venta'] = request.POST.get('uom_venta')
        request.session['producto_data']['factor_conversion'] = request.POST.get('factor_conversion')
        request.session['producto_data']['costo_estandar'] = request.POST.get('costo_estandar')
        request.session['producto_data']['precio_venta'] = request.POST.get('precio_venta')
        request.session['producto_data']['impuesto_iva'] = request.POST.get('impuesto_iva')
        request.session.modified = True
        
        return redirect('core:producto_paso2')
    
    data = request.session.get('producto_data', {})
    return render(request, 'productos/producto_paso1.html', {'data': data})

# Paso 2: Stock y control
def producto_paso2(request):
    if 'producto_data' not in request.session:
        return redirect('core:producto_paso1')
    
    if request.method == 'POST':
        request.session['producto_data']['stock_minimo'] = request.POST.get('stock_minimo')
        request.session['producto_data']['stock_maximo'] = request.POST.get('stock_maximo')
        request.session['producto_data']['punto_reorden'] = request.POST.get('punto_reorden')
        request.session['producto_data']['perishable'] = request.POST.get('perishable', '0')
        request.session['producto_data']['control_por_lote'] = request.POST.get('control_por_lote', '0')
        request.session['producto_data']['control_por_serie'] = request.POST.get('control_por_serie', '0')
        request.session.modified = True
        
        return redirect('core:producto_paso3')
    
    data = request.session.get('producto_data', {})
    return render(request, 'productos/producto_paso2.html', {'data': data})

# Paso 3: Relaciones y derivados
def producto_paso3(request):
    if 'producto_data' not in request.session:
        return redirect('core:producto_paso1')
    
    if request.method == 'POST':
        request.session['producto_data']['imagen_url'] = request.POST.get('imagen_url')
        request.session['producto_data']['ficha_tecnica_url'] = request.POST.get('ficha_tecnica_url')
        request.session.modified = True
        
        # Aquí guardarías el producto en la base de datos
        del request.session['producto_data']
        
        return redirect('core:lista_productos')
    
    data = request.session.get('producto_data', {})
    return render(request, 'productos/producto_paso3.html', {'data': data}) 
def editar_usuario(request, id):
    return render(request, 'usuarios/editar_usuario.html')

def lista_productos(request):
    return render(request, 'productos/lista_productos.html')

def crear_producto(request):
    return render(request, 'productos/crear_producto.html')

def editar_producto(request, id):
    return render(request, 'productos/editar_producto.html')

def lista_proveedores(request):
    return render(request, 'proveedores/lista_proveedores.html')

def crear_proveedor(request):
    return render(request, 'proveedores/crear_proveedor.html')

def proveedor_paso1(request):
    if request.method == 'POST':
        # Guardar datos en sesión
        if 'proveedor_data' not in request.session:
            request.session['proveedor_data'] = {}
        
        request.session['proveedor_data']['id'] = request.POST.get('id')
        request.session['proveedor_data']['rut_nif'] = request.POST.get('rut_nif')
        request.session['proveedor_data']['razon_social'] = request.POST.get('razon_social')
        request.session['proveedor_data']['nombre_fantasia'] = request.POST.get('nombre_fantasia')
        request.session['proveedor_data']['email'] = request.POST.get('email')
        request.session['proveedor_data']['telefono'] = request.POST.get('telefono')
        request.session['proveedor_data']['sitio_web'] = request.POST.get('sitio_web')
        request.session.modified = True
        
        return redirect('core:proveedor_paso2')
    
    # Recuperar datos si existen
    data = request.session.get('proveedor_data', {})
    return render(request, 'proveedores/proveedor_paso1.html', {'data': data})

# Paso 2: Dirección y comercial
def proveedor_paso2(request):
    # Verificar que existan datos del paso 1
    if 'proveedor_data' not in request.session:
        return redirect('core:proveedor_paso1')
    
    if request.method == 'POST':
        # Guardar datos en sesión
        request.session['proveedor_data']['direccion'] = request.POST.get('direccion')
        request.session['proveedor_data']['ciudad'] = request.POST.get('ciudad')
        request.session['proveedor_data']['region'] = request.POST.get('region')
        request.session['proveedor_data']['codigo_postal'] = request.POST.get('codigo_postal')
        request.session['proveedor_data']['pais'] = request.POST.get('pais')
        request.session['proveedor_data']['plazo_pago'] = request.POST.get('plazo_pago')
        request.session['proveedor_data']['moneda'] = request.POST.get('moneda')
        request.session['proveedor_data']['descuento'] = request.POST.get('descuento')
        request.session['proveedor_data']['notas_comerciales'] = request.POST.get('notas_comerciales')
        request.session.modified = True
        
        return redirect('core:proveedor_paso3')
    
    data = request.session.get('proveedor_data', {})
    return render(request, 'proveedores/proveedor_paso2.html', {'data': data})

# Paso 3: Relación con productos
def proveedor_paso3(request):
    # Verificar que existan datos del paso 1
    if 'proveedor_data' not in request.session:
        return redirect('core:proveedor_paso1')
    
    if request.method == 'POST':
        # Guardar datos finales
        request.session['proveedor_data']['es_proveedor_preferente'] = request.POST.get('es_proveedor_preferente', '0')
        request.session['proveedor_data']['lead_time'] = request.POST.get('lead_time')
        request.session['proveedor_data']['pedido_minimo'] = request.POST.get('pedido_minimo')
        request.session['proveedor_data']['calificacion'] = request.POST.get('calificacion')
        request.session['proveedor_data']['observaciones'] = request.POST.get('observaciones')
        request.session['proveedor_data']['estado'] = request.POST.get('estado', 'activo')
        request.session.modified = True
        
        # Aquí procesarías y guardarías el proveedor en la base de datos
        # Por ahora solo simulamos
        
        # Limpiar sesión después de guardar
        del request.session['proveedor_data']
        
        return redirect('core:lista_proveedores')
    
    data = request.session.get('proveedor_data', {})
    return render(request, 'proveedores/proveedor_paso3.html', {'data': data})


def editar_proveedor(request, id):
    return render(request, 'proveedores/editar_proveedor.html')

def lista_movimientos(request):
    return render(request, 'inventario/lista_movimientos.html')

# Vista principal - Muestra las opciones de los 3 pasos
def crear_movimiento(request):
    # Limpiar la sesión al iniciar un nuevo movimiento
    if 'movimiento_data' in request.session:
        del request.session['movimiento_data']
    return render(request, 'inventario/crear_movimiento.html')

# Paso 1: Datos del movimiento
def movimiento_paso1(request):
    if request.method == 'POST':
        # Guardar datos en sesión
        if 'movimiento_data' not in request.session:
            request.session['movimiento_data'] = {}
        
        request.session['movimiento_data']['fecha'] = request.POST.get('fecha')
        request.session['movimiento_data']['tipo'] = request.POST.get('tipo')
        request.session['movimiento_data']['cantidad'] = request.POST.get('cantidad')
        request.session['movimiento_data']['producto'] = request.POST.get('producto')
        request.session['movimiento_data']['proveedor'] = request.POST.get('proveedor')
        request.session['movimiento_data']['bodega'] = request.POST.get('bodega')
        request.session.modified = True
        
        return redirect('core:movimiento_paso2')
    
    # Recuperar datos si existen
    data = request.session.get('movimiento_data', {})
    return render(request, 'inventario/movimiento_paso1.html', {'data': data})

# Paso 2: Control avanzado
def movimiento_paso2(request):
    # Verificar que existan datos del paso 1
    if 'movimiento_data' not in request.session:
        return redirect('core:movimiento_paso1')
    
    if request.method == 'POST':
        # Guardar datos en sesión
        request.session['movimiento_data']['manejo_lotes'] = request.POST.get('manejo_lotes', '0')
        request.session['movimiento_data']['manejo_series'] = request.POST.get('manejo_series', '0')
        request.session['movimiento_data']['perecible'] = request.POST.get('perecible', '0')
        request.session['movimiento_data']['lote'] = request.POST.get('lote')
        request.session['movimiento_data']['serie'] = request.POST.get('serie')
        request.session['movimiento_data']['fecha_vencimiento'] = request.POST.get('fecha_vencimiento')
        request.session.modified = True
        
        return redirect('core:movimiento_paso3')
    
    data = request.session.get('movimiento_data', {})
    return render(request, 'inventario/movimiento_paso2.html', {'data': data})

# Paso 3: Referencias/Observaciones
def movimiento_paso3(request):
    # Verificar que existan datos del paso 1
    if 'movimiento_data' not in request.session:
        return redirect('core:movimiento_paso1')
    
    if request.method == 'POST':
        # Guardar datos finales
        request.session['movimiento_data']['doc_referencia'] = request.POST.get('doc_referencia')
        request.session['movimiento_data']['motivo'] = request.POST.get('motivo')
        request.session['movimiento_data']['observaciones'] = request.POST.get('observaciones')
        request.session.modified = True
        
        # Aquí procesarías y guardarías el movimiento en la base de datos
        # Por ahora solo simulamos
        
        # Limpiar sesión después de guardar
        del request.session['movimiento_data']
        
        return redirect('core:lista_movimientos')
    
    data = request.session.get('movimiento_data', {})
    return render(request, 'inventario/movimiento_paso3.html', {'data': data})

def editar_producto(request, id):
    return render(request, 'productos/editar_producto.html')

def lista_proveedores(request):
    return render(request, 'proveedores/lista_proveedores.html')

def crear_proveedor(request):
    return render(request, 'proveedores/crear_proveedor.html')

def editar_proveedor(request, id):
    return render(request, 'proveedores/editar_proveedor.html')

def lista_movimientos(request):
    return render(request, 'inventario/lista_movimientos.html')

# Vista principal - Muestra las opciones de los 3 pasos
def crear_movimiento(request):
    # Limpiar la sesión al iniciar un nuevo movimiento
    if 'movimiento_data' in request.session:
        del request.session['movimiento_data']
    return render(request, 'inventario/crear_movimiento.html')

# Paso 1: Datos del movimiento
def movimiento_paso1(request):
    if request.method == 'POST':
        # Guardar datos en sesión
        if 'movimiento_data' not in request.session:
            request.session['movimiento_data'] = {}
        
        request.session['movimiento_data']['fecha'] = request.POST.get('fecha')
        request.session['movimiento_data']['tipo'] = request.POST.get('tipo')
        request.session['movimiento_data']['cantidad'] = request.POST.get('cantidad')
        request.session['movimiento_data']['producto'] = request.POST.get('producto')
        request.session['movimiento_data']['proveedor'] = request.POST.get('proveedor')
        request.session['movimiento_data']['bodega'] = request.POST.get('bodega')
        request.session.modified = True
        
        return redirect('core:movimiento_paso2')
    
    # Recuperar datos si existen
    data = request.session.get('movimiento_data', {})
    return render(request, 'inventario/movimiento_paso1.html', {'data': data})

# Paso 2: Control avanzado
def movimiento_paso2(request):
    # Verificar que existan datos del paso 1
    if 'movimiento_data' not in request.session:
        return redirect('core:movimiento_paso1')
    
    if request.method == 'POST':
        # Guardar datos en sesión
        request.session['movimiento_data']['manejo_lotes'] = request.POST.get('manejo_lotes', '0')
        request.session['movimiento_data']['manejo_series'] = request.POST.get('manejo_series', '0')
        request.session['movimiento_data']['perecible'] = request.POST.get('perecible', '0')
        request.session['movimiento_data']['lote'] = request.POST.get('lote')
        request.session['movimiento_data']['serie'] = request.POST.get('serie')
        request.session['movimiento_data']['fecha_vencimiento'] = request.POST.get('fecha_vencimiento')
        request.session.modified = True
        
        return redirect('core:movimiento_paso3')
    
    data = request.session.get('movimiento_data', {})
    return render(request, 'inventario/movimiento_paso2.html', {'data': data})

# Paso 3: Referencias/Observaciones
def movimiento_paso3(request):
    # Verificar que existan datos del paso 1
    if 'movimiento_data' not in request.session:
        return redirect('core:movimiento_paso1')
    
    if request.method == 'POST':
        # Guardar datos finales
        request.session['movimiento_data']['doc_referencia'] = request.POST.get('doc_referencia')
        request.session['movimiento_data']['motivo'] = request.POST.get('motivo')
        request.session['movimiento_data']['observaciones'] = request.POST.get('observaciones')
        request.session.modified = True
        
        # Aquí procesarías y guardarías el movimiento en la base de datos
        # Por ahora solo simulamos
        
        # Limpiar sesión después de guardar
        del request.session['movimiento_data']
        
        return redirect('core:lista_movimientos')
    
    data = request.session.get('movimiento_data', {})
    return render(request, 'inventario/movimiento_paso3.html', {'data': data})

def editar_movimiento(request, id):
    return render(request, 'inventario/editar_movimiento.html', {'movimiento_id': id})

def movimiento_editar_paso1(request, id):
    # Similar a movimiento_paso1 pero para edición
    if request.method == 'POST':
        # Lógica de edición
        pass
    
    data = request.session.get('movimiento_data', {})
    return render(request, 'inventario/movimiento_paso1.html', {'data': data, 'movimiento_id': id, 'es_edicion': True})