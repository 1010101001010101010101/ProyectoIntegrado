from django.core.management.base import BaseCommand
from core.models import UnidadMedida

class Command(BaseCommand):
    help = 'Crea las unidades de medida básicas'

    def handle(self, *args, **options):
        unidades = [
            # CANTIDAD
            {'codigo': 'UN', 'nombre': 'Unidad', 'tipo': 'CANTIDAD'},
            {'codigo': 'PAR', 'nombre': 'Par', 'tipo': 'CANTIDAD'},
            {'codigo': 'DOC', 'nombre': 'Docena', 'tipo': 'CANTIDAD'},
            {'codigo': 'CAJA', 'nombre': 'Caja', 'tipo': 'CANTIDAD'},
            {'codigo': 'PACK', 'nombre': 'Pack', 'tipo': 'CANTIDAD'},
            {'codigo': 'PALLET', 'nombre': 'Pallet', 'tipo': 'CANTIDAD'},
            
            # PESO
            {'codigo': 'GR', 'nombre': 'Gramo', 'tipo': 'PESO'},
            {'codigo': 'KG', 'nombre': 'Kilogramo', 'tipo': 'PESO'},
            {'codigo': 'TON', 'nombre': 'Tonelada', 'tipo': 'PESO'},
            
            # VOLUMEN
            {'codigo': 'ML', 'nombre': 'Mililitro', 'tipo': 'VOLUMEN'},
            {'codigo': 'LT', 'nombre': 'Litro', 'tipo': 'VOLUMEN'},
            {'codigo': 'M3', 'nombre': 'Metro Cúbico', 'tipo': 'VOLUMEN'},
            
            # LONGITUD
            {'codigo': 'CM', 'nombre': 'Centímetro', 'tipo': 'LONGITUD'},
            {'codigo': 'MT', 'nombre': 'Metro', 'tipo': 'LONGITUD'},
        ]
        
        creadas = 0
        for unidad_data in unidades:
            unidad, created = UnidadMedida.objects.get_or_create(
                codigo=unidad_data['codigo'],
                defaults={
                    'nombre': unidad_data['nombre'],
                    'tipo': unidad_data['tipo']
                }
            )
            if created:
                creadas += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Creada: {unidad}'))
            else:
                self.stdout.write(f'  Ya existe: {unidad}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ {creadas} unidades creadas de {len(unidades)} totales'))