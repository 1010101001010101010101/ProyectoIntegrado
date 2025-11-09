from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modelo abstracto que proporciona campos de auditoría
    """
    fecha_creacion = models.DateTimeField(
        default=timezone.now,  # ← Cambiar de auto_now_add a default
        verbose_name='Fecha de creación'
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última modificación'
    )
    
    class Meta:
        abstract = True