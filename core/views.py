from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.shortcuts import render

def login_view(request):
    # Si ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember')
        
        # Autenticar usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Usuario autenticado correctamente
            login(request, user)
            
            # Configurar duración de sesión según "Recordarme"
            if not remember:
                # Sesión expira al cerrar el navegador
                request.session.set_expiry(0)
            else:
                # Sesión dura 2 semanas
                request.session.set_expiry(1209600)  # 14 días en segundos
            
            # Redirigir al dashboard
            messages.success(request, f'¡Bienvenido de vuelta, {user.get_full_name() or user.username}!')
            return redirect('core:dashboard')
        else:
            # Credenciales inválidas
            messages.error(request, 'Usuario o contraseña incorrectos')
            return render(request, 'login.html', {
                'error': True,
                'username': username  # Mantener el username en el formulario
            })
    
    return render(request, 'login.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect('core:login')

def recuperar_password(request):
    return render(request, 'recuperar_password.html')

def validar_token(request, token=None):
    return render(request, 'validar_token.html', {'token': token})

def nueva_password(request):
    return render(request, 'nueva_password.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def lista_usuarios(request):
    return render(request, 'usuarios/lista.html')

def crear_usuario(request):
    return render(request, 'usuarios/crear.html')

def editar_usuario(request, id):
    return render(request, 'usuarios/editar.html', {'id': id})

def lista_productos(request):
    return render(request, 'productos/lista.html')

def crear_producto(request):
    return render(request, 'productos/crear.html')

def producto_paso1(request):
    return render(request, 'productos/paso1.html')

def producto_paso2(request):
    return render(request, 'productos/paso2.html')

def producto_paso3(request):
    return render(request, 'productos/paso3.html')

def editar_producto(request, id):
    return render(request, 'productos/editar.html', {'id': id})

def lista_proveedores(request):
    return render(request, 'proveedores/lista.html')

def crear_proveedor(request):
    return render(request, 'proveedores/crear.html')

def editar_proveedor(request, id):
    return render(request, 'proveedores/editar.html', {'id': id})

# ===============================================
# MODELO: Usuario Extendido
# ===============================================
class Usuario(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('BLOQUEADO', 'Bloqueado'),
        ('INACTIVO', 'Inactivo'),
    ]
    
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
        ('almacen', 'Almacén'),
        ('contador', 'Contador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=30, blank=True, null=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='vendedor')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    mfa_habilitado = models.BooleanField(default=False)
    ultimo_acceso = models.DateTimeField(blank=True, null=True)
    sesiones_activas = models.IntegerField(default=0)
    area = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"


# ===============================================
# MODELO: Categoría de Productos
# ===============================================
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


# ===============================================
# MODELO: Producto
# ===============================================
class Producto(models.Model):
    UOM_CHOICES = [
        ('UN', 'Unidad'),
        ('CAJA', 'Caja'),
        ('KG', 'Kilogramo'),
        ('LT', 'Litro'),
        ('PACK', 'Pack'),
    ]
    
    # Identificación
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    ean_upc = models.CharField(max_length=13, blank=True, null=True, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    
    # Unidades y precios
    uom_compra = models.CharField(max_length=10, choices=UOM_CHOICES, default='UN')
    uom_venta = models.CharField(max_length=10, choices=UOM_CHOICES, default='UN')
    factor_conversion = models.DecimalField(max_digits=10, decimal_places=6, default=Decimal('1.0'))
    costo_estandar = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    costo_promedio = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    precio_venta = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    impuesto_iva = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('19.0'),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Stock y control
    stock_minimo = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal('0.0'))
    stock_maximo = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    punto_reorden = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    stock_actual = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal('0.0'))
    
    perecible = models.BooleanField(default=False)
    control_por_lote = models.BooleanField(default=False)
    control_por_serie = models.BooleanField(default=False)
    
    # Relaciones y soporte
    imagen_url = models.URLField(blank=True, null=True)
    ficha_tecnica_url = models.URLField(blank=True, null=True)
    
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['categoria']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return f"{self.sku} - {self.nombre}"
    
    @property
    def alerta_bajo_stock(self):
        return self.stock_actual < self.stock_minimo
    
    @property
    def estado_stock(self):
        if self.stock_actual <= 0:
            return 'SIN_STOCK'
        elif self.stock_actual < self.stock_minimo:
            return 'BAJO'
        elif self.stock_maximo and self.stock_actual > self.stock_maximo:
            return 'EXCESO'
        return 'OK'


# ===============================================
# MODELO: Proveedor
# ===============================================
class Proveedor(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('BLOQUEADO', 'Bloqueado'),
        ('INACTIVO', 'Inactivo'),
    ]
    
    MONEDA_CHOICES = [
        ('CLP', 'Peso Chileno'),
        ('USD', 'Dólar'),
        ('EUR', 'Euro'),
        ('ARS', 'Peso Argentino'),
        ('BRL', 'Real'),
    ]
    
    # Identificación legal y contacto
    rut_nif = models.CharField(max_length=20, unique=True, db_index=True)
    razon_social = models.CharField(max_length=255)
    nombre_fantasia = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=30, blank=True, null=True)
    sitio_web = models.URLField(blank=True, null=True)
    
    # Dirección
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=128, blank=True, null=True)
    region = models.CharField(max_length=128, blank=True, null=True)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    pais = models.CharField(max_length=64, default='Chile')
    
    # Comercial
    condiciones_pago = models.CharField(max_length=100, blank=True, null=True)
    moneda = models.CharField(max_length=8, choices=MONEDA_CHOICES, default='CLP')
    contacto_principal_nombre = models.CharField(max_length=120, blank=True, null=True)
    contacto_principal_email = models.EmailField(blank=True, null=True)
    contacto_principal_telefono = models.CharField(max_length=30, blank=True, null=True)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    observaciones = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'proveedores'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['razon_social']
        indexes = [
            models.Index(fields=['rut_nif']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.razon_social} ({self.rut_nif})"


# ===============================================
# MODELO: Relación Producto-Proveedor
# ===============================================
class ProductoProveedor(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='proveedores')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='productos')
    
    costo = models.DecimalField(max_digits=18, decimal_places=6)
    lead_time_dias = models.IntegerField(default=7, validators=[MinValueValidator(0)])
    min_lote = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal('1.0'))
    descuento_pct = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.0'),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    preferente = models.BooleanField(default=False)
    
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'producto_proveedor'
        verbose_name = 'Producto-Proveedor'
        verbose_name_plural = 'Productos-Proveedores'
        unique_together = [['producto', 'proveedor']]
        indexes = [
            models.Index(fields=['producto', 'proveedor']),
            models.Index(fields=['preferente']),
        ]
    
    def __str__(self):
        return f"{self.producto.sku} - {self.proveedor.razon_social}"


# ===============================================
# MODELO: Bodega
# ===============================================
class Bodega(models.Model):
    codigo = models.CharField(max_length=50, unique=True, db_index=True)
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=128, blank=True, null=True)
    responsable = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bodegas'
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# ===============================================
# MODELO: Movimiento de Inventario
# ===============================================
class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('INGRESO', 'Ingreso'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste'),
        ('DEVOLUCION', 'Devolución'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]
    
    # Datos del movimiento
    fecha = models.DateTimeField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.DecimalField(max_digits=18, decimal_places=6)
    
    # Relaciones
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='movimientos')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos')
    bodega = models.ForeignKey(Bodega, on_delete=models.PROTECT, related_name='movimientos')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='movimientos_realizados')
    
    # Control avanzado
    lote = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    serie = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    
    # Referencias
    doc_referencia = models.CharField(max_length=100, blank=True, null=True)
    motivo = models.CharField(max_length=200, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    # Transferencias (bodega destino)
    bodega_destino = models.ForeignKey(
        Bodega, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='movimientos_recibidos'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'movimientos_inventario'
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha', '-created_at']
        indexes = [
            models.Index(fields=['fecha', 'tipo']),
            models.Index(fields=['producto', 'bodega']),
            models.Index(fields=['lote']),
            models.Index(fields=['serie']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.sku} - {self.fecha.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        """Actualizar stock del producto al guardar movimiento"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            if self.tipo in ['INGRESO', 'DEVOLUCION']:
                self.producto.stock_actual += self.cantidad
            elif self.tipo == 'SALIDA':
                self.producto.stock_actual -= self.cantidad
            elif self.tipo == 'AJUSTE':
                # El ajuste puede ser positivo o negativo
                self.producto.stock_actual = self.cantidad
            
            self.producto.save(update_fields=['stock_actual', 'updated_at'])


# ===============================================
# MODELO: Log de Auditoría
# ===============================================
class LogAuditoria(models.Model):
    ACCION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='logs')
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    modelo = models.CharField(max_length=100)
    objeto_id = models.IntegerField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'log_auditoria'
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['usuario', 'timestamp']),
            models.Index(fields=['modelo', 'objeto_id']),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} - {self.modelo} - {self.timestamp}"