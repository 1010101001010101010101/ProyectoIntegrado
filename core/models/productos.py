from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Categoria(models.Model):
    """Categorías de productos"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class UnidadMedida(models.Model):
    """Unidades de medida para productos"""
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Producto(models.Model):
    """Modelo principal de productos"""
    
    # ============================================
    # IDENTIFICACIÓN
    # ============================================
    sku = models.CharField(
        'SKU/Código',
        max_length=50,
        unique=True,
        help_text='Código único del producto'
    )
    
    ean_upc = models.CharField(
        'EAN/UPC',
        max_length=13,
        blank=True,
        null=True,
        help_text='Código de barras internacional'
    )
    
    nombre = models.CharField(
        'Nombre',
        max_length=200,
        help_text='Nombre del producto'
    )
    
    descripcion = models.TextField(
        'Descripción',
        blank=True,
        null=True,
        help_text='Descripción detallada del producto'
    )
    
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos',
        verbose_name='Categoría'
    )
    
    marca = models.CharField(
        'Marca',
        max_length=100,
        blank=True,
        null=True
    )
    
    modelo = models.CharField(
        'Modelo',
        max_length=100,
        blank=True,
        null=True
    )
    
    # ============================================
    # UNIDADES Y CONVERSIÓN
    # ============================================
    uom_compra = models.ForeignKey(
        UnidadMedida,
        on_delete=models.PROTECT,
        related_name='productos_compra',
        verbose_name='Unidad de Compra',
        help_text='Unidad en la que se compra el producto'
    )
    
    uom_venta = models.ForeignKey(
        UnidadMedida,
        on_delete=models.PROTECT,
        related_name='productos_venta',
        verbose_name='Unidad de Venta',
        help_text='Unidad en la que se vende el producto'
    )
    
    factor_conversion = models.DecimalField(
        'Factor de Conversión',
        max_digits=10,
        decimal_places=4,
        default=Decimal('1.0000'),
        validators=[MinValueValidator(Decimal('0.0001'))],
        help_text='Unidades de venta por unidad de compra'
    )
    
    # ============================================
    # PRECIOS
    # ============================================
    costo_estandar = models.DecimalField(
        'Costo Estándar',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Costo promedio estándar del producto'
    )
    
    costo_promedio = models.DecimalField(
        'Costo Promedio',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Calculado automáticamente con movimientos'
    )
    
    precio_venta = models.DecimalField(
        'Precio de Venta',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Precio de venta al público'
    )
    
    impuesto_iva = models.DecimalField(
        'IVA (%)',
        max_digits=5,
        decimal_places=2,
        default=Decimal('19.00'),
        validators=[
            MinValueValidator(Decimal('0')),
            MaxValueValidator(Decimal('100'))
        ],
        help_text='Porcentaje de IVA aplicable'
    )
    
    # ============================================
    # STOCK
    # ============================================
    stock_actual = models.IntegerField(
        'Stock Actual',
        default=0,
        help_text='Cantidad actual en inventario'
    )
    
    stock_minimo = models.DecimalField(
        'Stock Mínimo',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Cantidad mínima requerida'
    )
    
    stock_maximo = models.DecimalField(
        'Stock Máximo',
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Cantidad máxima permitida'
    )
    
    punto_reorden = models.DecimalField(
        'Punto de Reorden',
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Punto para reabastecimiento'
    )
    
    # ============================================
    # CONTROL ESPECIAL
    # ============================================
    es_perecedero = models.BooleanField(
        '¿Es Perecedero?',
        default=False,
        help_text='Producto con fecha de vencimiento'
    )
    
    requiere_lote = models.BooleanField(
        '¿Requiere Lote?',
        default=False,
        help_text='Control por número de lote'
    )
    
    requiere_serie = models.BooleanField(
        '¿Requiere Serie?',
        default=False,
        help_text='Control por número de serie'
    )
    
    # ============================================
    # RELACIONES Y MULTIMEDIA
    # ============================================
    imagen_url = models.URLField(
        'URL Imagen',
        max_length=500,
        blank=True,
        null=True,
        help_text='URL de la imagen del producto'
    )
    
    ficha_tecnica_url = models.URLField(
        'URL Ficha Técnica',
        max_length=500,
        blank=True,
        null=True,
        help_text='URL de la ficha técnica'
    )
    
    # ============================================
    # CAMPOS DERIVADOS/CALCULADOS
    # ============================================
    alerta_bajo_stock = models.BooleanField(
        'Alerta Bajo Stock',
        default=False,
        help_text='Indica si el stock está por debajo del mínimo'
    )
    
    alerta_por_vencer = models.BooleanField(
        'Alerta Por Vencer',
        default=False,
        help_text='Indica si hay productos próximos a vencer'
    )
    
    # ============================================
    # ESTADO Y AUDITORÍA
    # ============================================
    activo = models.BooleanField(
        'Activo',
        default=True,
        help_text='Producto activo en el sistema'
    )
    
    created_at = models.DateTimeField(
        'Fecha de Creación',
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        'Última Actualización',
        auto_now=True
    )
    
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='productos_creados',
        verbose_name='Creado Por',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['nombre']),
            models.Index(fields=['categoria']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return f"{self.sku} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        """Calcular campos derivados antes de guardar"""
        # Calcular alerta de bajo stock
        if self.stock_actual <= self.stock_minimo:
            self.alerta_bajo_stock = True
        else:
            self.alerta_bajo_stock = False
        
        # Convertir SKU a mayúsculas
        if self.sku:
            self.sku = self.sku.upper()
        
        # Si no hay punto de reorden, usar stock mínimo
        if not self.punto_reorden:
            self.punto_reorden = self.stock_minimo
        
        super().save(*args, **kwargs)
    
    @property
    def margen_ganancia(self):
        """Calcular margen de ganancia porcentual"""
        if self.costo_estandar > 0 and self.precio_venta > 0:
            margen = ((self.precio_venta - self.costo_estandar) / self.costo_estandar) * 100
            return round(margen, 2)
        return Decimal('0.00')
    
    @property
    def stock_disponible(self):
        """Alias para stock actual"""
        return self.stock_actual
    
    @property
    def valor_inventario(self):
        """Valor total del inventario actual"""
        return self.stock_actual * self.costo_promedio
    
    @property
    def requiere_reposicion(self):
        """Indica si necesita reposición"""
        if self.punto_reorden:
            return self.stock_actual <= self.punto_reorden
        return self.alerta_bajo_stock
    
    def actualizar_stock(self, cantidad, tipo='entrada'):
        """
        Actualizar el stock del producto
        tipo: 'entrada' o 'salida'
        """
        if tipo == 'entrada':
            self.stock_actual += Decimal(str(cantidad))
        elif tipo == 'salida':
            self.stock_actual -= Decimal(str(cantidad))
            if self.stock_actual < 0:
                self.stock_actual = Decimal('0')
        
        self.save()
    
    def calcular_costo_promedio(self, nuevo_costo, cantidad_entrada):
        """
        Calcular nuevo costo promedio ponderado
        """
        if self.stock_actual > 0:
            valor_actual = self.stock_actual * self.costo_promedio
            valor_nuevo = Decimal(str(cantidad_entrada)) * Decimal(str(nuevo_costo))
            stock_total = self.stock_actual + Decimal(str(cantidad_entrada))
            
            self.costo_promedio = (valor_actual + valor_nuevo) / stock_total
        else:
            self.costo_promedio = Decimal(str(nuevo_costo))
        
        self.save()