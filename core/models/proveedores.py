from django.db import models
from .base import TimeStampedModel
from core.models.productos import Producto
from django.contrib import messages


class Proveedor(TimeStampedModel):
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
        help_text='Formato: 12345678-9',
        db_index=True
    )
    razon_social = models.CharField(
        max_length=200,
        verbose_name='Razón Social',
        db_index=True
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
        verbose_name='Email',
        db_index=True
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
        verbose_name='Ciudad',
        db_index=True
    )
    region = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Región',
        db_index=True
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
    lead_time = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Lead time (días)'
    )
    pedido_minimo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Pedido mínimo'
    )
    es_proveedor_preferente = models.BooleanField(
        default=False,
        verbose_name='Proveedor preferente'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='ACTIVO',
        verbose_name='Estado'
    )
    productos = models.ManyToManyField(
        Producto,
        through='ProveedorProducto',
        related_name='proveedores',
        blank=True,
    )

    @property
    def nombre_display(self):
        return self.nombre_fantasia or self.razon_social

    @property
    def esta_activo(self):
        return self.estado == 'ACTIVO'

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['razon_social']
    
    def __str__(self):
        return f"{self.rut} - {self.razon_social}"


class ProveedorProducto(TimeStampedModel):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    costo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lead_time = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Lead time (días)'
    )
    activo = models.BooleanField(default=True)
    pedido_minimo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Pedido mínimo'
    )
    es_proveedor_preferente = models.BooleanField(
        default=False,
        verbose_name='Proveedor preferente'
    )
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('proveedor', 'producto')