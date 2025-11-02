from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
    
    def __str__(self):
        return self.nombre


class Producto(models.Model):
    # Identificación
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')
    ean_upc = models.CharField(max_length=13, blank=True, null=True, verbose_name='EAN/UPC')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    marca = models.CharField(max_length=100, blank=True, null=True, verbose_name='Marca')
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name='Modelo')
    
    # Unidades y Precios
    uom_compra = models.CharField(max_length=10, verbose_name='Unidad de Compra')
    uom_venta = models.CharField(max_length=10, verbose_name='Unidad de Venta')
    factor_conversion = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name='Factor de Conversión')
    costo_estandar = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Costo Estándar')
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Precio de Venta')
    impuesto_iva = models.DecimalField(max_digits=5, decimal_places=2, default=19, verbose_name='IVA (%)')
    
    # Stock y Control
    stock_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Stock Actual')
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Stock Mínimo')
    stock_maximo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Stock Máximo')
    punto_reorden = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Punto de Reorden')
    
    # Opciones de Control
    perishable = models.BooleanField(default=False, verbose_name='Producto Perecedero')
    control_por_lote = models.BooleanField(default=False, verbose_name='Control por Lote')
    control_por_serie = models.BooleanField(default=False, verbose_name='Control por Serie')
    
    # Relaciones
    imagen_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='URL de Imagen')
    ficha_tecnica_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='URL Ficha Técnica')
    
    # Campos Derivados
    alerta_bajo_stock = models.BooleanField(default=False, verbose_name='Alerta Bajo Stock')
    alerta_por_vencer = models.BooleanField(default=False, verbose_name='Alerta Por Vencer')
    
    # Control
    activo = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha Actualización')
    
    class Meta:
        db_table = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.sku} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        # Actualizar alerta de bajo stock automáticamente
        self.alerta_bajo_stock = self.stock_actual < self.stock_minimo
        super().save(*args, **kwargs)
