from django.core.management.base import BaseCommand
from core.models import Usuario, Producto, Proveedor, MovimientoInventario, Categoria, Bodega
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Elimina todos los datos de prueba'

    def handle(self, *args, **kwargs):
        self.stdout.write('Eliminando datos de prueba...')
        
        MovimientoInventario.objects.all().delete()
        Producto.objects.all().delete()
        Proveedor.objects.all().delete()
        Categoria.objects.all().delete()
        Bodega.objects.all().delete()
        Usuario.objects.all().delete()
        # NO eliminar el superusuario
        # User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(self.style.SUCCESS('✓ Datos eliminados correctamente'))