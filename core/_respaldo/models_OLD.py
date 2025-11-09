from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

class Categoria(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
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
    # Identificación
    sku = models.CharField(max_length=30, unique=True)
    ean_upc = models.CharField(max_length=13, null=True, blank=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    marca = models.CharField(max_length=100, null=True, blank=True)
    modelo = models.CharField(max_length=100, null=True, blank=True)

    # Unidades y precios
    uom_compra = models.ForeignKey(
        'UnidadMedida', 
        on_delete=models.PROTECT, 
        related_name='productos_compra',
        verbose_name='Unidad de Compra'
    )
    uom_venta = models.ForeignKey(
        'UnidadMedida', 
        on_delete=models.PROTECT, 
        related_name='productos_venta',
        verbose_name='Unidad de Venta'
    )
    factor_conversion = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'), validators=[MinValueValidator(Decimal('0.01'))])
    costo_estandar = models.DecimalField(max_digits=14, decimal_places=0, default=Decimal('0'))
    costo_promedio = models.DecimalField(max_digits=14, decimal_places=0, default=Decimal('0'))
    precio_venta = models.DecimalField(max_digits=14, decimal_places=0, default=Decimal('0'))
    impuesto_iva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('19.00'), validators=[MinValueValidator(0), MaxValueValidator(100)])

    # Stock y control
    stock_actual = models.DecimalField(max_digits=14, decimal_places=0, default=Decimal('0'))
    stock_minimo = models.DecimalField(max_digits=14, decimal_places=0, default=Decimal('0'))
    stock_maximo = models.DecimalField(max_digits=14, decimal_places=0, default=Decimal('0'))
    punto_reorden = models.DecimalField(max_digits=14, decimal_places=0, default=Decimal('0'))

    # Control de inventario requeridos por la evaluación
    es_perecedero = models.BooleanField(default=False)
    dias_vida_util = models.PositiveIntegerField(null=True, blank=True)
    requiere_serie = models.BooleanField(default=False)
    requiere_lote = models.BooleanField(default=False)

    # Paso 3: URLs (opcionales para el usuario, pero presentes en BD)
    imagen_url = models.URLField(max_length=500, null=True, blank=True)
    ficha_tecnica_url = models.URLField(max_length=500, null=True, blank=True)

    activo = models.BooleanField(default=True)
    alerta_bajo_stock = models.BooleanField(default=True)
    alerta_por_vencer = models.BooleanField(default=False)
    permite_venta_sin_stock = models.BooleanField(
        default=False,
        verbose_name='Permite venta sin stock'
    )

    peso_kg = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name='Peso en kg',
        help_text='Peso unitario en kilogramos'
    )

    volumen_m3 = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name='Volumen en m³',
        help_text='Volumen unitario en metros cúbicos'
    )

    # ===== CAMPOS FALTANTES =====
    imagen = models.ImageField(
        upload_to='productos/',
        null=True,
        blank=True,
        verbose_name='Imagen del producto'
    )
    
    codigo_barra = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Código de barras',
        help_text='EAN13, Code128, etc.'
    )
    
    observaciones = models.TextField(
        null=True,
        blank=True,
        verbose_name='Observaciones',
        help_text='Notas adicionales sobre el producto'
    )
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.es_perecedero:
            if not self.dias_vida_util or self.dias_vida_util <= 0:
                raise ValidationError({'dias_vida_util': 'Obligatorio y > 0 para perecederos.'})
            self.requiere_lote = True
        else:
            self.dias_vida_util = None

        if self.stock_maximo and self.stock_minimo and self.stock_maximo < self.stock_minimo:
            raise ValidationError({'stock_maximo': 'Debe ser >= stock mínimo.'})
        if self.punto_reorden and self.stock_minimo and self.punto_reorden < self.stock_minimo:
            raise ValidationError({'punto_reorden': 'Debe ser >= stock mínimo.'})

    def save(self, *args, **kwargs):
        try:
            self.alerta_bajo_stock = (Decimal(self.stock_actual or 0) <= Decimal(self.stock_minimo or 0))
        except Exception:
            self.alerta_bajo_stock = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.sku} - {self.nombre}'


# ===============================================
# MODELO: PROVEEDOR
# ===============================================
class Proveedor(models.Model):
    """Modelo de Proveedor"""
    
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
    ]
    
    # Identificación
    rut = models.CharField(
        max_length=12,
        unique=True,
        verbose_name='RUT',
        help_text='Formato: 12345678-9'
    )
    razon_social = models.CharField(
        max_length=200,
        verbose_name='Razón Social'
    )
    nombre_fantasia = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Nombre Fantasía'
    )
    giro = models.CharField(
        max_length=200,
        verbose_name='Giro Comercial'
    )
    
    # Contacto
    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Teléfono'
    )
    email = models.EmailField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Email'
    )
    sitio_web = models.URLField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Sitio Web'
    )
    
    # Dirección
    direccion = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Dirección'
    )
    comuna = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Comuna'
    )
    ciudad = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Ciudad'
    )
    region = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Región'
    )
    
    # Contacto comercial
    contacto_nombre = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name='Nombre de contacto'
    )
    contacto_telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Teléfono de contacto'
    )
    contacto_email = models.EmailField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Email de contacto'
    )
    
    # Información adicional
    observaciones = models.TextField(
        null=True,
        blank=True,
        verbose_name='Observaciones'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='ACTIVO',
        verbose_name='Estado'
    )
    
    # Auditoría
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última modificación'
    )
    
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['razon_social']
    
    def __str__(self):
        return f"{self.rut} - {self.razon_social}"


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
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True, default='')  # ← Agregar default=''
    capacidad = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    activa = models.BooleanField(default=True)
    
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


# ===============================================
# MODELOS DE VENTAS - AGREGAR AL FINAL
# ===============================================

class Venta(models.Model):
    """Modelo para registrar ventas"""
    TIPO_COMPROBANTE = [
        ('BOLETA', 'Boleta'),
        ('FACTURA', 'Factura'),
        ('TICKET', 'Ticket'),
    ]
    
    ESTADO = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADA', 'Pagada'),
        ('ANULADA', 'Anulada'),
    ]
    
    METODO_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA_DEBITO', 'Tarjeta de Débito'),
        ('TARJETA_CREDITO', 'Tarjeta de Crédito'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]
    
    numero_comprobante = models.CharField(max_length=20, unique=True)
    tipo_comprobante = models.CharField(max_length=10, choices=TIPO_COMPROBANTE, default='BOLETA')
    fecha = models.DateTimeField(auto_now_add=True)
    
    # Cliente (opcional para boletas)
    cliente_nombre = models.CharField(max_length=200, blank=True)
    cliente_rut = models.CharField(max_length=12, blank=True)
    cliente_email = models.EmailField(blank=True)
    cliente_telefono = models.CharField(max_length=20, blank=True)
    
    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Estado y pago
    estado = models.CharField(max_length=10, choices=ESTADO, default='PENDIENTE')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO, default='EFECTIVO')
    
    # Relaciones
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='ventas')
    bodega = models.ForeignKey(Bodega, on_delete=models.PROTECT, related_name='ventas')
    
    # Campos adicionales
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
    
    def __str__(self):
        return f"{self.tipo_comprobante} {self.numero_comprobante} - ${self.total}"
    
    def calcular_totales(self):
        """Calcular subtotal, impuesto y total basado en los detalles"""
        detalles = self.detalles.all()
        self.subtotal = sum(d.subtotal for d in detalles)
        self.impuesto = self.subtotal * Decimal('0.19')  # IVA 19%
        self.total = self.subtotal + self.impuesto - self.descuento
        self.save()


class DetalleVenta(models.Model):
    """Detalle de productos en una venta"""
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        # Calcular subtotal con descuento
        base = self.cantidad * self.precio_unitario
        descuento = base * (self.descuento_porcentaje / 100)
        self.subtotal = base - descuento
        
        super().save(*args, **kwargs)
        
        # Actualizar totales de la venta
        if self.venta_id:
            self.venta.calcular_totales()
    
    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"


class UnidadMedida(models.Model):
    """Unidades de medida para productos (UOM - Unit of Measure)"""
    codigo = models.CharField(max_length=10, unique=True, help_text='Ej: UN, KG, LT')
    nombre = models.CharField(max_length=50, help_text='Ej: Unidad, Kilogramo, Litro')
    tipo = models.CharField(max_length=20, choices=[
        ('CANTIDAD', 'Cantidad'),
        ('PESO', 'Peso'),
        ('VOLUMEN', 'Volumen'),
        ('LONGITUD', 'Longitud'),
    ], default='CANTIDAD')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'unidades_medida'
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"