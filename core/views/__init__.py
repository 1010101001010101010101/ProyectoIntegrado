"""
Módulo de vistas modularizadas
Expone todas las vistas para facilitar importaciones en urls.py
"""

# Auth
from .auth import (
    login_view,
    logout_view,
    dashboard,
    recuperar_password,
    cambiar_password_inicial,
    validar_token,
    nueva_password,
)

# Usuarios
from .usuarios import (
    lista_usuarios,
    crear_usuario,
    editar_usuario,
    eliminar_usuario,
)

# Productos
from .productos import (
    lista_productos,
    crear_producto,
    producto_paso1,
    producto_paso2,
    producto_paso3,
    editar_producto,
    eliminar_producto,
    exportar_productos_excel,
)

# Proveedores
from .proveedores import (
    lista_proveedores,
    exportar_proveedores_excel,
    buscar_proveedores_ajax,
    crear_proveedor,
    editar_proveedor,
    eliminar_proveedor,
    cambiar_estado_proveedor,
    proveedor_paso1,
    proveedor_paso2,
    proveedor_paso3,
)

# Inventario
from .inventario import (
    lista_movimientos,
    crear_movimiento,
    movimiento_paso1,
    movimiento_paso2,
    movimiento_paso3,
)

# Ventas
from .ventas import (
    lista_ventas,
    crear_venta,
    detalle_venta,
)

__all__ = [
    # Auth
    'login_view', 'logout_view', 'dashboard', 'recuperar_password',
    'cambiar_password_inicial', 'validar_token', 'nueva_password',
    
    # Usuarios
    'lista_usuarios', 'crear_usuario', 'editar_usuario', 'eliminar_usuario',
    
    # Productos
    'lista_productos', 'crear_producto', 'producto_paso1', 'producto_paso2',
    'producto_paso3', 'editar_producto', 'eliminar_producto', 'exportar_productos_excel',
    
    # Proveedores
    'lista_proveedores', 'crear_proveedor', 'proveedor_paso1', 'proveedor_paso2',
    'proveedor_paso3', 'editar_proveedor', 'eliminar_proveedor', 'exportar_proveedores_excel',
    
    # Inventario
    'lista_movimientos', 'crear_movimiento', 'movimiento_paso1',
    'movimiento_paso2', 'movimiento_paso3',
    
    # Ventas
    'lista_ventas', 'crear_venta', 'detalle_venta',
]