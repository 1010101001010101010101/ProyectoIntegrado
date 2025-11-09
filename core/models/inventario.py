from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .base import TimeStampedModel
from .productos import Producto
from .usuarios import Usuario
from .proveedores import Proveedor


class Bodega(TimeStampedModel):
    """Bodegas de almacenamiento"""
    
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código'
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    direccion = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Dirección'
    )
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='bodegas_responsable',
        null=True,
        blank=True,
        verbose_name='Responsable'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class MovimientoInventario(TimeStampedModel):
    """Movimientos de inventario"""
    
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]
    
    tipo_movimiento = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de movimiento'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Producto'
    )
    bodega = models.ForeignKey(
        Bodega,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Bodega'
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Cantidad'
    )
    
    # Trazabilidad
    lote = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Lote'
    )
    numero_serie = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Número de serie'
    )
    fecha_vencimiento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de vencimiento'
    )
    
    # Documentos
    documento_tipo = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Tipo de documento'
    )
    documento_numero = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Número de documento'
    )
    
    # Auditoría
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Usuario'
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha'
    )
    motivo = models.TextField(
        null=True,
        blank=True,
        verbose_name='Motivo'
    )
    observaciones = models.TextField(
        null=True,
        blank=True,
        verbose_name='Observaciones'
    )
    
    # Proveedor
    proveedor = models.ForeignKey(
        Proveedor,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Proveedor'
    )
    
    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} - {self.producto.sku} ({self.cantidad})"


class Lote(TimeStampedModel):
    """Control de lotes"""
    
    numero_lote = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número de lote'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='lotes',
        verbose_name='Producto'
    )
    fecha_fabricacion = models.DateField(
        verbose_name='Fecha de fabricación'
    )
    fecha_vencimiento = models.DateField(
        verbose_name='Fecha de vencimiento'
    )
    cantidad_inicial = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Cantidad inicial'
    )
    cantidad_actual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Cantidad actual'
    )
    
    class Meta:
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        ordering = ['fecha_vencimiento']
    
    def __str__(self):
        return f"Lote {self.numero_lote} - {self.producto.nombre}"