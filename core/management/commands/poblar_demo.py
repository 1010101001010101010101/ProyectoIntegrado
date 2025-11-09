# poblar_demo.py
from core.models import Categoria, UnidadMedida, Producto
from core.models.proveedores import Proveedor, ProveedorProducto
from decimal import Decimal
import random

# Categorías
categorias_info = [
    ("Alfajores", "Alfajores artesanales de diferentes sabores"),
    ("Galletas", "Galletas caseras y decoradas"),
    ("Chocolatería", "Bombones y chocolates artesanales"),
    ("Cajas y canastos de regalo", "Presentaciones para regalo"),
    ("Temporada", "Productos especiales para Halloween, Navidad, etc."),
]
categorias = []
for nombre, desc in categorias_info:
    cat, _ = Categoria.objects.get_or_create(nombre=nombre, defaults={"descripcion": desc, "activo": True})
    categorias.append(cat)

# Unidad de medida
uom, _ = UnidadMedida.objects.get_or_create(codigo="UN", defaults={"nombre": "Unidad", "descripcion": "Unidad", "activo": True})

# Proveedores
proveedores_info = [
    ("76.123.456-1", "DulcesSur SPA", "DulcesSur", "dulcessur@proveedor.cl"),
    ("76.234.567-2", "ChocoArte Ltda", "ChocoArte", "contacto@chocoarte.cl"),
    ("76.345.678-3", "Galletas del Sur", "GalletasSur", "ventas@galletassur.cl"),
    ("76.456.789-4", "Regalos Dulces", "RegalosDulces", "info@regalosdulces.cl"),
    ("76.567.890-5", "Bombonería Fina", "BombonFina", "bomboneria@fina.cl"),
    ("76.678.901-6", "Alfajores Premium", "AlfaPremium", "contacto@alfapremium.cl"),
    ("76.789.012-7", "Dulce Navidad", "DulceNavidad", "navidad@dulce.cl"),
    ("76.890.123-8", "ChocoManía", "ChocoMania", "ventas@chocomania.cl"),
    ("76.901.234-9", "Canastos y Cajas", "CanastosCajas", "info@canastoscajas.cl"),
    ("76.012.345-K", "Temporada Festiva", "TemporadaFestiva", "temporada@festiva.cl"),
]
proveedores = []
for rut, razon, fantasia, email in proveedores_info:
    prov, _ = Proveedor.objects.get_or_create(
        rut=rut,
        razon_social=razon,
        nombre_fantasia=fantasia,
        giro="Pastelería y confitería",
        telefono="+56912345678",
        email=email,
        sitio_web=f"https://{fantasia.lower()}.cl",
        direccion="Calle Falsa 123",
        comuna="Santiago",
        ciudad="Santiago",
        region="RM",
        estado="ACTIVO",
    )
    proveedores.append(prov)

# Productos de pastelería y confitería
productos_info = [
    # Alfajores
    ("Alfajor clásico", "Alfajor relleno de dulce de leche, bañado en chocolate semi amargo", categorias[0]),
    ("Alfajor de nuez", "Alfajor relleno de crema de nuez y cubierto con chocolate blanco", categorias[0]),
    ("Alfajor vegano", "Alfajor sin ingredientes de origen animal, relleno de manjar vegano", categorias[0]),
    ("Alfajor triple", "Alfajor de tres capas con dulce de leche y baño de chocolate", categorias[0]),
    ("Alfajor frambuesa", "Alfajor relleno de mermelada de frambuesa y chocolate", categorias[0]),
    ("Alfajor coco", "Alfajor con coco rallado y dulce de leche", categorias[0]),
    # Galletas
    ("Galleta decorada navideña", "Galleta de mantequilla decorada con motivos de Navidad", categorias[1]),
    ("Galleta de avena y pasas", "Galleta casera con avena, pasas y un toque de canela", categorias[1]),
    ("Galleta de chocolate chips", "Galleta crocante con chips de chocolate belga", categorias[1]),
    ("Galleta integral", "Galleta saludable con harina integral y semillas", categorias[1]),
    ("Galleta glaseada", "Galleta decorada con glaseado de colores", categorias[1]),
    ("Galleta de limón", "Galleta suave con sabor a limón natural", categorias[1]),
    # Chocolatería
    ("Caja de bombones surtidos", "Caja con selección de bombones artesanales rellenos", categorias[2]),
    ("Trufas de chocolate", "Trufas artesanales de chocolate amargo y cacao", categorias[2]),
    ("Chocolate relleno de frambuesa", "Chocolate artesanal relleno de crema de frambuesa", categorias[2]),
    ("Bombón de almendra", "Bombón relleno de pasta de almendra y chocolate", categorias[2]),
    ("Chocolate blanco con pistacho", "Chocolate blanco con trozos de pistacho", categorias[2]),
    ("Bombón corazón", "Bombón en forma de corazón relleno de frutos rojos", categorias[2]),
    # Cajas y canastos de regalo
    ("Canasto de regalo dulce", "Canasto con alfajores, galletas y chocolates surtidos", categorias[3]),
    ("Caja premium de alfajores", "Caja de regalo con alfajores gourmet variados", categorias[3]),
    ("Set de galletas decoradas", "Caja con galletas decoradas para regalo", categorias[3]),
    ("Caja de bombones festivos", "Caja especial de bombones para regalo", categorias[3]),
    ("Canasto navideño", "Canasto con productos navideños artesanales", categorias[3]),
    ("Caja sorpresa dulce", "Caja con selección sorpresa de productos dulces", categorias[3]),
    # Temporada
    ("Alfajor Halloween", "Alfajor decorado especial para Halloween", categorias[4]),
    ("Galleta de Navidad", "Galleta decorada con motivos navideños", categorias[4]),
    ("Bombón San Valentín", "Bombón artesanal en forma de corazón para San Valentín", categorias[4]),
    ("Caja especial Pascua", "Caja con productos especiales para Pascua", categorias[4]),
    ("Alfajor Pascua", "Alfajor decorado para Pascua de Resurrección", categorias[4]),
    ("Galleta de Halloween", "Galleta decorada con motivos de Halloween", categorias[4]),
]

productos = []
for nombre, desc, cat in productos_info:
    prod, _ = Producto.objects.get_or_create(
        sku=nombre[:10].upper(),
        nombre=nombre,
        descripcion=desc,
        categoria=cat,
        marca=random.choice(["DulcesSur", "ChocoArte", "GalletasSur", "BombonFina"]),
        modelo=None,
        uom_compra=uom,
        uom_venta=uom,
        factor_conversion=Decimal("1.00"),
        costo_estandar=Decimal(random.randint(800, 2500)),
        costo_promedio=Decimal(random.randint(800, 2500)),
        precio_venta=Decimal(random.randint(1200, 3500)),
        impuesto_iva=Decimal("19.00"),
        stock_actual=random.randint(10, 80),
        stock_minimo=Decimal(random.randint(5, 15)),
        stock_maximo=Decimal(random.randint(50, 200)),
        punto_reorden=Decimal(random.randint(10, 30)),
        es_perecedero=random.choice([True, False]),
        requiere_lote=random.choice([True, False]),
        requiere_serie=False,
        activo=True,
    )
    productos.append(prod)

# Asignar productos a proveedores (cada producto a 1-2 proveedores)
for prod in productos:
    provs = random.sample(proveedores, k=random.randint(1, 2))
    for prov in provs:
        ProveedorProducto.objects.get_or_create(
            proveedor=prov,
            producto=prod,
            defaults={
                "costo": prod.costo_estandar,
                "lead_time": random.randint(3, 10),
                "pedido_minimo": Decimal(random.randint(5000, 20000)),
                "es_proveedor_preferente": random.choice([True, False]),
                "activo": True,
            }
        )

print("¡Datos de proveedores y productos de pastelería creados y conectados!")