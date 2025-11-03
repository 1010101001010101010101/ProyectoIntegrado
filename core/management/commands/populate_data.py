# core/management/commands/populate_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from core.models import (
    Usuario, Categoria, Producto, Proveedor, 
    ProductoProveedor, Bodega, MovimientoInventario
)
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos iniciales de prueba'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando población de datos...'))
        self.stdout.write('')

        # ===============================================
        # 1. CREAR SUPERUSUARIO Y USUARIOS DE PRUEBA
        # ===============================================
        self.stdout.write('👤 Creando usuarios...')
        
        # Superusuario
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@lilis.cl',
                password='Admin123!@#',
                first_name='Administrador',
                last_name='Sistema'
            )
            Usuario.objects.create(
                user=admin_user,
                telefono='+56 9 1234 5678',
                rol='admin',
                estado='ACTIVO',
                area='Administración',
                ultimo_acceso=timezone.now()
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Superusuario "admin" creado'))
        
        # Usuarios adicionales
        usuarios_data = [
            ('kfigueroa', 'Keyla', 'Figueroa', 'keyla.figueroa@lilis.cl', 'admin', '+56 9 8765 4321'),
            ('mlopez', 'María', 'López', 'maria.lopez@lilis.cl', 'vendedor', '+56 9 7654 3210'),
            ('pfernandez', 'Pedro', 'Fernández', 'pedro.fernandez@lilis.cl', 'almacen', '+56 9 6543 2109'),
        ]
        
        for username, first_name, last_name, email, rol, telefono in usuarios_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='Password123!',
                    first_name=first_name,
                    last_name=last_name
                )
                Usuario.objects.create(
                    user=user,
                    telefono=telefono,
                    rol=rol,
                    estado='ACTIVO'
                )
                self.stdout.write(f'  ✓ Usuario "{username}" creado')
        
        self.stdout.write('')

        # ===============================================
        # 2. CREAR CATEGORÍAS
        # ===============================================
        self.stdout.write('📂 Creando categorías...')
        
        categorias_data = [
            ('Dulces', 'Dulces variados y surtidos'),
            ('Chocolates', 'Chocolates y productos derivados del cacao'),
            ('Chicles', 'Chicles y gomas de mascar'),
            ('Caramelos', 'Caramelos duros y blandos'),
            ('Gomitas', 'Gomitas y gelatinas'),
            ('Galletas', 'Galletas dulces y saladas'),
            ('Snacks', 'Snacks y bocadillos'),
        ]
        
        categorias_creadas = {}
        for nombre, descripcion in categorias_data:
            categoria, created = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion, 'activo': True}
            )
            categorias_creadas[nombre] = categoria
            if created:
                self.stdout.write(f'  ✓ Categoría "{nombre}" creada')
        
        self.stdout.write('')

        # ===============================================
        # 3. CREAR BODEGAS
        # ===============================================
        self.stdout.write('🏢 Creando bodegas...')
        
        bodegas_data = [
            ('BOD-CENTRAL', 'Bodega Central', 'Av. Principal 123', 'La Serena', 500.00),
            ('BOD-SUC-1', 'Sucursal 1', 'Calle Comercio 456', 'Coquimbo', 200.00),
            ('BOD-SUC-2', 'Sucursal 2', 'Av. Centro 789', 'Ovalle', 150.00),
        ]
        
        bodegas_creadas = {}
        for codigo, nombre, direccion, ciudad, capacidad in bodegas_data:
            bodega, created = Bodega.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'direccion': direccion,
                    'ciudad': ciudad,
                    'capacidad_m3': Decimal(str(capacidad)),
                    'activo': True
                }
            )
            bodegas_creadas[codigo] = bodega
            if created:
                self.stdout.write(f'  ✓ Bodega "{codigo}" creada')
        
        self.stdout.write('')

        # ===============================================
        # 4. CREAR PROVEEDORES
        # ===============================================
        self.stdout.write('🏭 Creando proveedores...')
        
        proveedores_data = [
            {
                'rut_nif': '76.543.210-5',
                'razon_social': 'Distribuidora Dulces del Sur S.A.',
                'nombre_fantasia': 'Dulces Sur',
                'email': 'ventas@dulcessur.cl',
                'telefono': '+56 2 2345 6789',
                'ciudad': 'Santiago',
                'region': 'Región Metropolitana',
                'pais': 'Chile',
                'condiciones_pago': '30 días',
                'moneda': 'CLP',
            },
            {
                'rut_nif': '77.123.456-K',
                'razon_social': 'Chocolates Andinos Ltda.',
                'nombre_fantasia': 'Choco Andino',
                'email': 'contacto@chocoandino.cl',
                'telefono': '+56 2 3456 7890',
                'ciudad': 'Valparaíso',
                'region': 'Región de Valparaíso',
                'pais': 'Chile',
                'condiciones_pago': '45 días',
                'moneda': 'CLP',
            },
            {
                'rut_nif': '78.987.654-3',
                'razon_social': 'Importadora Global Snacks S.A.',
                'nombre_fantasia': 'Global Snacks',
                'email': 'ventas@globalsnacks.cl',
                'telefono': '+56 2 4567 8901',
                'ciudad': 'Concepción',
                'region': 'Región del Biobío',
                'pais': 'Chile',
                'condiciones_pago': '60 días',
                'moneda': 'CLP',
            },
        ]
        
        proveedores_creados = {}
        for prov_data in proveedores_data:
            proveedor, created = Proveedor.objects.get_or_create(
                rut_nif=prov_data['rut_nif'],
                defaults=prov_data
            )
            proveedores_creados[prov_data['rut_nif']] = proveedor
            if created:
                self.stdout.write(f'  ✓ Proveedor "{prov_data["razon_social"]}" creado')
        
        self.stdout.write('')

        # ===============================================
        # 5. CREAR PRODUCTOS
        # ===============================================
        self.stdout.write('📦 Creando productos...')
        
        productos_data = [
            {
                'sku': 'CAR-001',
                'nombre': 'Caramelos Surtidos Premium',
                'descripcion': 'Bolsa de caramelos surtidos 500g',
                'categoria': categorias_creadas['Caramelos'],
                'marca': 'Ambrosoli',
                'uom_compra': 'CAJA',
                'uom_venta': 'UN',
                'factor_conversion': Decimal('12'),
                'costo_estandar': Decimal('2000.00'),
                'precio_venta': Decimal('2990.00'),
                'impuesto_iva': Decimal('19.00'),
                'stock_minimo': Decimal('50.00'),
                'stock_maximo': Decimal('500.00'),
                'punto_reorden': Decimal('100.00'),
                'perishable': False,
            },
            {
                'sku': 'CHO-025',
                'nombre': 'Chocolate Milka Tableta',
                'descripcion': 'Chocolate con leche 100g',
                'categoria': categorias_creadas['Chocolates'],
                'marca': 'Milka',
                'uom_compra': 'CAJA',
                'uom_venta': 'UN',
                'factor_conversion': Decimal('24'),
                'costo_estandar': Decimal('2500.00'),
                'precio_venta': Decimal('3490.00'),
                'impuesto_iva': Decimal('19.00'),
                'stock_minimo': Decimal('30.00'),
                'stock_maximo': Decimal('300.00'),
                'punto_reorden': Decimal('75.00'),
                'perishable': True,
                'control_por_lote': True,
            },
            {
                'sku': 'DUL-010',
                'nombre': 'Dulces Surtidos Mix Premium',
                'descripcion': 'Mix premium de dulces variados 1kg',
                'categoria': categorias_creadas['Dulces'],
                'marca': 'Lilis',
                'uom_compra': 'KG',
                'uom_venta': 'UN',
                'factor_conversion': Decimal('1.00'),
                'costo_estandar': Decimal('3500.00'),
                'precio_venta': Decimal('4990.00'),
                'impuesto_iva': Decimal('19.00'),
                'stock_minimo': Decimal('20.00'),
                'stock_maximo': Decimal('200.00'),
                'punto_reorden': Decimal('50.00'),
                'perishable': True,
                'control_por_lote': True,
            },
            {
                'sku': 'CHI-077',
                'nombre': 'Chicles Adams Variedad',
                'descripcion': 'Paquete de chicles surtidos 150g',
                'categoria': categorias_creadas['Chicles'],
                'marca': 'Adams',
                'uom_compra': 'PACK',
                'uom_venta': 'UN',
                'factor_conversion': Decimal('10'),
                'costo_estandar': Decimal('1500.00'),
                'precio_venta': Decimal('1990.00'),
                'impuesto_iva': Decimal('19.00'),
                'stock_minimo': Decimal('40.00'),
                'stock_maximo': Decimal('400.00'),
                'punto_reorden': Decimal('80.00'),
                'perishable': False,
            },
            {
                'sku': 'GOM-033',
                'nombre': 'Gomitas Mogul Ositos',
                'descripcion': 'Gomitas con forma de ositos 200g',
                'categoria': categorias_creadas['Gomitas'],
                'marca': 'Mogul',
                'uom_compra': 'CAJA',
                'uom_venta': 'UN',
                'factor_conversion': Decimal('20'),
                'costo_estandar': Decimal('1800.00'),
                'precio_venta': Decimal('2490.00'),
                'impuesto_iva': Decimal('19.00'),
                'stock_minimo': Decimal('35.00'),
                'stock_maximo': Decimal('350.00'),
                'punto_reorden': Decimal('70.00'),
                'perishable': True,
            },
        ]
        
        productos_creados = []
        for prod_data in productos_data:
            producto, created = Producto.objects.get_or_create(
                sku=prod_data['sku'],
                defaults=prod_data
            )
            productos_creados.append(producto)
            if created:
                self.stdout.write(f'  ✓ Producto "{prod_data["sku"]}" creado')
        
        self.stdout.write('')

        # ===============================================
        # 6. CREAR RELACIONES PRODUCTO-PROVEEDOR
        # ===============================================
        self.stdout.write('🔗 Creando relaciones producto-proveedor...')
        
        # Asignar proveedores a productos aleatoriamente
        count = 0
        for producto in productos_creados:
            # Elegir 1-2 proveedores por producto
            num_proveedores = random.randint(1, 2)
            proveedores_elegidos = random.sample(list(proveedores_creados.values()), num_proveedores)
            
            for i, proveedor in enumerate(proveedores_elegidos):
                costo_base = float(producto.costo_estandar or 0)
                variacion = random.uniform(0.9, 1.1)
                costo_proveedor = Decimal(str(costo_base * variacion))
                
                ProductoProveedor.objects.get_or_create(
                    producto=producto,
                    proveedor=proveedor,
                    defaults={
                        'costo': costo_proveedor,
                        'lead_time_dias': random.choice([7, 10, 15, 20]),
                        'min_lote': Decimal(str(random.choice([1, 5, 10, 20]))),
                        'descuento_pct': Decimal(str(random.choice([0, 2, 5, 10]))),
                        'preferente': (i == 0),  # El primero es preferente
                    }
                )
                count += 1
        
        self.stdout.write(f'  ✓ {count} relaciones producto-proveedor creadas')
        self.stdout.write('')

        # ===============================================
        # 7. CREAR MOVIMIENTOS DE INVENTARIO
        # ===============================================
        self.stdout.write('📊 Creando movimientos de inventario...')
        
        usuario_admin = Usuario.objects.filter(user__username='admin').first()
        bodega_central = bodegas_creadas['BOD-CENTRAL']
        proveedor_default = list(proveedores_creados.values())[0]
        
        movimientos_count = 0
        for producto in productos_creados:
            # Ingreso inicial
            cantidad_ingreso = random.randint(100, 300)
            MovimientoInventario.objects.create(
                fecha=timezone.now(),
                tipo='INGRESO',
                cantidad=Decimal(str(cantidad_ingreso)),
                producto=producto,
                proveedor=proveedor_default,
                bodega=bodega_central,
                usuario=usuario_admin,
                lote=f'L-2025-{random.randint(100, 999)}' if producto.control_por_lote else '',
                doc_referencia=f'OC-{random.randint(1000, 9999)}',
                motivo='Ingreso inicial de inventario'
            )
            movimientos_count += 1
            
            # Algunas salidas aleatorias
            if random.random() > 0.5:
                cantidad_salida = random.randint(10, 50)
                MovimientoInventario.objects.create(
                    fecha=timezone.now(),
                    tipo='SALIDA',
                    cantidad=Decimal(str(cantidad_salida)),
                    producto=producto,
                    bodega=bodega_central,
                    usuario=usuario_admin,
                    doc_referencia=f'FAC-{random.randint(1000, 9999)}',
                    motivo='Venta a cliente'
                )
                movimientos_count += 1
        
        self.stdout.write(f'  ✓ {movimientos_count} movimientos de inventario creados')
        self.stdout.write('')

        # ===============================================
        # RESUMEN FINAL
        # ===============================================
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('✅ ¡BASE DE DATOS POBLADA EXITOSAMENTE!'))
        self.stdout.write(self.style.SUCCESS('========================================'))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('📋 RESUMEN:'))
        self.stdout.write(f'   • Usuarios: {User.objects.count()}')
        self.stdout.write(f'   • Categorías: {Categoria.objects.count()}')
        self.stdout.write(f'   • Productos: {Producto.objects.count()}')
        self.stdout.write(f'   • Proveedores: {Proveedor.objects.count()}')
        self.stdout.write(f'   • Bodegas: {Bodega.objects.count()}')
        self.stdout.write(f'   • Movimientos: {MovimientoInventario.objects.count()}')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('🔐 CREDENCIALES DE ACCESO:'))
        self.stdout.write('   Username: admin')
        self.stdout.write('   Password: Admin123!@#')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🚀 ¡Listo para usar!'))