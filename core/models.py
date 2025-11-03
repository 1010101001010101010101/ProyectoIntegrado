from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


# ===============================================
# MODELO: CATEGORÍA
# ===============================================
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


# ===============================================
# MODELO: USUARIO (PERFIL EXTENDIDO)
# ===============================================
class Usuario(models.Model):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
        ('almacen', 'Almacén'),
        ('contador', 'Contador'),
    ]
    
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('BLOQUEADO', 'Bloqueado'),
        ('INACTIVO', 'Inactivo'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=30, blank=True, null=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='vendedor')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    mfa_habilitado = models.BooleanField(default=False, verbose_name='MFA Habilitado')
    ultimo_acceso = models.DateTimeField(blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True, verbose_name='Área/Unidad')
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.rol})"


# ===============================================
# MODELO: PRODUCTO
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
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')
    ean_upc = models.CharField(max_length=13, blank=True, null=True, unique=True, verbose_name='EAN/UPC')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    
    # Unidades y precios
    uom_compra = models.CharField(max_length=10, choices=UOM_CHOICES, default='UN', verbose_name='UOM Compra')
    uom_venta = models.CharField(max_length=10, choices=UOM_CHOICES, default='UN', verbose_name='UOM Venta')
    factor_conversion = models.DecimalField(max_digits=10, decimal_places=4, default=1, 
                                           validators=[MinValueValidator(Decimal('0.0001'))])
    costo_estandar = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True, default=0)
    costo_promedio = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True, default=0)
    precio_venta = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True, default=0)
    impuesto_iva = models.DecimalField(max_digits=5, decimal_places=2, default=19, 
                                       validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Stock y control
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                       validators=[MinValueValidator(0)])
    stock_maximo = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                       validators=[MinValueValidator(0)])
    punto_reorden = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                        validators=[MinValueValidator(0)])
    perishable = models.BooleanField(default=False, verbose_name='Perecedero')
    control_por_lote = models.BooleanField(default=False)
    control_por_serie = models.BooleanField(default=False)
    
    # Relaciones y soporte
    imagen_url = models.URLField(max_length=255, blank=True, null=True)
    ficha_tecnica_url = models.URLField(max_length=255, blank=True, null=True)
    
    # Campos derivados (calculados)
    stock_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    alerta_bajo_stock = models.BooleanField(default=False, editable=False)
    alerta_por_vencer = models.BooleanField(default=False, editable=False)
    
    # Control
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
    
    def save(self, *args, **kwargs):
        # Calcular alerta de bajo stock
        self.alerta_bajo_stock = self.stock_actual < self.stock_minimo
        super().save(*args, **kwargs)


# ===============================================
# MODELO: PROVEEDOR
# ===============================================
class Proveedor(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('BLOQUEADO', 'Bloqueado'),
    ]
    
    # Identificación legal y contacto
    rut_nif = models.CharField(max_length=20, unique=True, verbose_name='RUT/NIF')
    razon_social = models.CharField(max_length=255)
    nombre_fantasia = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=254)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    sitio_web = models.URLField(max_length=255, blank=True, null=True)
    
    # Dirección
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=128, blank=True, null=True)
    region = models.CharField(max_length=128, blank=True, null=True)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    pais = models.CharField(max_length=64, default='Chile')
    
    # Comercial
    condiciones_pago = models.CharField(max_length=100, blank=True, null=True)
    moneda = models.CharField(max_length=8, default='CLP')
    contacto_principal_nombre = models.CharField(max_length=120, blank=True, null=True)
    contacto_principal_email = models.EmailField(max_length=254, blank=True, null=True)
    contacto_principal_telefono = models.CharField(max_length=30, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    observaciones = models.TextField(blank=True, null=True)
    
    # Control
    activo = models.BooleanField(default=True)
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
        return f"{self.rut_nif} - {self.razon_social}"


# ===============================================
# MODELO: PRODUCTO-PROVEEDOR (Relación)
# ===============================================
class ProductoProveedor(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='producto_proveedores')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='proveedor_productos')
    
    # Datos comerciales
    costo = models.DecimalField(max_digits=18, decimal_places=6)
    lead_time_dias = models.IntegerField(default=7, validators=[MinValueValidator(0)])
    min_lote = models.DecimalField(max_digits=18, decimal_places=6, default=1,
                                   validators=[MinValueValidator(Decimal('0.01'))])
    descuento_pct = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,
                                        validators=[MinValueValidator(0), MaxValueValidator(100)])
    preferente = models.BooleanField(default=False)
    
    # Control
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
# MODELO: BODEGA
# ===============================================
class Bodega(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=128, blank=True, null=True)
    capacidad_m3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                       validators=[MinValueValidator(0)])
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                    related_name='bodegas_responsable')
    
    # Control
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bodegas'
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# ===============================================
# MODELO: MOVIMIENTO DE INVENTARIO
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
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de Movimiento')
    cantidad = models.DecimalField(max_digits=12, decimal_places=2,
                                   validators=[MinValueValidator(Decimal('0.01'))])
    
    # Relaciones principales
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='movimientos')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='movimientos')
    bodega = models.ForeignKey(Bodega, on_delete=models.PROTECT, related_name='movimientos')
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='movimientos_realizados')
    
    # Control por lote/serie
    lote = models.CharField(max_length=50, blank=True, null=True)
    serie = models.CharField(max_length=50, blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    
    # Referencias y observaciones
    doc_referencia = models.CharField(max_length=100, blank=True, null=True, 
                                      verbose_name='Documento de Referencia')
    motivo = models.CharField(max_length=200, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'movimientos_inventario'
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha', '-created_at']
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['tipo']),
            models.Index(fields=['producto']),
            models.Index(fields=['bodega']),
            models.Index(fields=['-fecha']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.sku} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Guardar el movimiento
        super().save(*args, **kwargs)
        
        # Actualizar stock del producto según el tipo de movimiento
        if self.tipo in ['INGRESO', 'DEVOLUCION']:
            self.producto.stock_actual += self.cantidad
        elif self.tipo == 'SALIDA':
            self.producto.stock_actual -= self.cantidad
        elif self.tipo == 'AJUSTE':
            # El ajuste ya viene con la cantidad final deseada
            pass
        
        # Guardar el producto con el nuevo stock
        self.producto.save()