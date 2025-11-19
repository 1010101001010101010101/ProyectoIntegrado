from django.db import models
from django.contrib.auth.models import User
from .base import TimeStampedModel



class Usuario(TimeStampedModel):
    """Perfil extendido de usuario"""
    
    ROL_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('BODEGA', 'Bodeguero'),
        ('CONSULTA', 'Consulta'),
    ]
    
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario',
        db_index=True
    )
    
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='LECTOR',
        verbose_name='Rol',
        db_index=True
    )
    
    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Teléfono'
    )
    
    direccion = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Dirección'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='ACTIVO',
        verbose_name='Estado',
        db_index=True
    )
    
    ultimo_acceso = models.DateTimeField(null=True, blank=True, verbose_name='Último acceso')
    must_change_password = models.BooleanField(default=False)
    intentos_fallidos = models.PositiveIntegerField(default=0, verbose_name='Intentos fallidos')
    bloqueado = models.BooleanField(default=False, verbose_name='Bloqueado por intentos', db_index=True)
    ultima_modificacion_password = models.DateTimeField(null=True, blank=True, verbose_name='Última modificación de contraseña')
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_rol_display()})"

