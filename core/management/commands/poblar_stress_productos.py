from django.core.management.base import BaseCommand
from core.models import Producto, Categoria, UnidadMedida, Proveedor, ProveedorProducto
import random

class Command(BaseCommand):
    help = 'Genera 10.000 productos de prueba para stress test y los asocia a uno o más proveedores existentes.'

    def handle(self, *args, **options):
        categorias = list(Categoria.objects.all())
        unidades = list(UnidadMedida.objects.all())
        proveedores = list(Proveedor.objects.all())
        if not categorias or not unidades or not proveedores:
            self.stdout.write(self.style.ERROR('Debes tener al menos una categoría, una unidad de medida y un proveedor.'))
            return
        productos = []
        for i in range(1, 10001):
            producto = Producto(
                sku=f'ST-PROD-{i:05d}',
                nombre=f'Producto Stress {i}',
                descripcion=f'Producto generado para pruebas de stress #{i}',
                categoria=random.choice(categorias),
                marca='StressTest',
                modelo='ST-2025',
                uom_compra=random.choice(unidades),
                uom_venta=random.choice(unidades),
                stock_actual=random.randint(0, 1000),
                precio_venta=random.randint(100, 10000),
                activo=True
            )
            productos.append(producto)
        Producto.objects.bulk_create(productos, batch_size=1000)
        nuevos_productos = Producto.objects.order_by('-id')[:10000]
        relaciones = []
        for producto in nuevos_productos:
            # Cada producto se asocia a 1-3 proveedores aleatorios
            num_proveedores = random.choices([1,2,3], weights=[0.7,0.2,0.1])[0]
            proveedores_asignados = random.sample(proveedores, k=num_proveedores)
            for proveedor in proveedores_asignados:
                relacion = ProveedorProducto(
                    proveedor=proveedor,
                    producto=producto,
                    costo=producto.precio_venta,
                    activo=True
                )
                relaciones.append(relacion)
        ProveedorProducto.objects.bulk_create(relaciones, batch_size=1000)
        self.stdout.write(self.style.SUCCESS('Se crearon 10.000 productos y se asociaron a uno o más proveedores correctamente.'))
