"""
Modelos modularizados
Expone todos los modelos para importaciones simplificadas
"""

# Base
from .base import TimeStampedModel

# Usuarios
from .usuarios import Usuario

# Productos
from .productos import Categoria, UnidadMedida, Producto

# Proveedores
from .proveedores import Proveedor, ProveedorProducto

# Inventario
from .inventario import Bodega, MovimientoInventario, Lote

# Ventas
from .ventas import Cliente, Venta, DetalleVenta

# Auditoria
from .auditoria import EventoAuditoria

__all__ = [
    # Base
    'TimeStampedModel',
    
    # Usuarios
    'Usuario',
    
    # Productos
    'Categoria',
    'UnidadMedida',
    'Producto',
    
    # Proveedores
    'Proveedor',
    'ProveedorProducto',
    
    # Inventario
    'Bodega',
    'MovimientoInventario',
    'Lote',
    
    # Ventas
    'Cliente',
    'Venta',
    'DetalleVenta',
    
    # Auditoria
    'EventoAuditoria',
]