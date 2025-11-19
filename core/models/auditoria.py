from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class EventoAuditoria(models.Model):
    ACCIONES = [
        ('CREAR', 'Crear'),
        ('EDITAR', 'Editar'),
        ('BORRAR', 'Borrar'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=10, choices=ACCIONES)
    objeto = models.CharField(max_length=50)  # Ej: Usuario, Producto, Movimiento
    detalle = models.TextField(blank=True)

    def __str__(self):
        return f"{self.fecha_hora} - {self.usuario} - {self.accion} {self.objeto}"
