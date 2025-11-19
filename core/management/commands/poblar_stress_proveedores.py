from django.core.management.base import BaseCommand
from core.models import Proveedor
import random

def generar_rut_valido():
    # Genera un rut chileno válido (simple, sin verificador real)
    numero = random.randint(1000000, 99999999)
    dv = str(random.randint(0, 9))  # Para stress test, no importa el verificador real
    return f"{numero}-{dv}"

class Command(BaseCommand):
    help = 'Genera 5.000 proveedores de prueba para stress test.'

    def handle(self, *args, **options):
        proveedores = []
        for i in range(1, 5001):
            rut = generar_rut_valido()
            proveedor = Proveedor(
                rut=rut,
                razon_social=f'Proveedor Stress {i}',
                nombre_fantasia=f'Fantasia {i}',
                giro='Comercial',
                telefono=f'+569{random.randint(10000000,99999999)}',
                email=f'proveedor{i}@stress.com',
                sitio_web=f'https://proveedor{i}.cl',
                direccion=f'Calle {i}',
                comuna='Santiago',
                ciudad='Santiago',
                region='RM',
                estado='ACTIVO'
            )
            proveedores.append(proveedor)
        Proveedor.objects.bulk_create(proveedores, batch_size=1000)
        self.stdout.write(self.style.SUCCESS('Se crearon 5.000 proveedores de stress test correctamente.'))
