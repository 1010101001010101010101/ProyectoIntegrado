import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Producto, Proveedor, Bodega, Usuario, MovimientoInventario
from django.contrib.auth import get_user_model

TIPOS = ['ingreso', 'salida', 'ajuste', 'devolucion', 'transferencia']

class Command(BaseCommand):
    help = 'Genera movimientos de inventario masivos para pruebas de stress'

    def add_arguments(self, parser):
        parser.add_argument('--cantidad', type=int, default=10000, help='Cantidad de movimientos a crear')

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        productos = list(Producto.objects.all())
        proveedores = list(Proveedor.objects.all())
        bodegas = list(Bodega.objects.all())
        usuarios = list(Usuario.objects.all())
        User = get_user_model()

        if not productos:
            self.stdout.write(self.style.WARNING('No hay productos, creando 100...'))
            for i in range(100):
                productos.append(Producto.objects.create(sku=f'STRESSSKU{i}', nombre=f'Producto Stress {i}', stock_actual=1000))
        if not proveedores:
            self.stdout.write(self.style.WARNING('No hay proveedores, creando 20...'))
            for i in range(20):
                proveedores.append(Proveedor.objects.create(rut=f'999999{i}', razon_social=f'Proveedor Stress {i}'))
        if not bodegas:
            self.stdout.write(self.style.WARNING('No hay bodegas, creando 5...'))
            for i in range(5):
                bodegas.append(Bodega.objects.create(codigo=f'STRESSBOD{i}', nombre=f'Bodega Stress {i}'))
        if not usuarios:
            self.stdout.write(self.style.WARNING('No hay usuarios, creando 1...'))
            u = User.objects.create_user(username='stressuser', password='stresspass')
            usuarios.append(Usuario.objects.create(user=u, rol='ADMIN'))

        self.stdout.write(self.style.SUCCESS(f'Creando {cantidad} movimientos de inventario...'))
        base_fecha = timezone.now() - timedelta(days=365)
        for i in range(cantidad):
            fecha = base_fecha + timedelta(days=random.randint(0, 364), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            tipo = random.choice(TIPOS)
            producto = random.choice(productos)
            # Seleccionar proveedor asociado al producto si existe
            proveedores_producto = list(producto.proveedores.all())
            if proveedores_producto:
                proveedor = random.choice(proveedores_producto)
            else:
                proveedor = random.choice(proveedores)
            bodega = random.choice(bodegas)
            usuario = random.choice(usuarios)
            cantidad_mov = random.randint(1, 100)
            lote = f'Lote-{random.randint(1, 1000)}' if random.random() < 0.3 else ''
            serie = f'Serie-{random.randint(1, 1000)}' if random.random() < 0.2 else ''
            fecha_venc = fecha.date() + timedelta(days=random.randint(30, 365)) if random.random() < 0.1 else None
            doc_num = f'DOC-{random.randint(1000,9999)}' if random.random() < 0.5 else ''
            MovimientoInventario.objects.create(
                fecha=fecha,
                tipo_movimiento=tipo,
                cantidad=cantidad_mov,
                producto=producto,
                proveedor=proveedor,
                bodega=bodega,
                usuario=usuario,
                lote=lote,
                numero_serie=serie,
                fecha_vencimiento=fecha_venc,
                documento_numero=doc_num,
            )
            if (i+1) % 1000 == 0:
                self.stdout.write(f'{i+1} movimientos creados...')
        self.stdout.write(self.style.SUCCESS('Movimientos de inventario generados correctamente.'))
