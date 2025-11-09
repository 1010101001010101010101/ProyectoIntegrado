"""
Formularios modularizados
Expone todos los forms para importaciones simplificadas
"""

# Auth
from .auth import (
    LoginForm,
    RecuperarPasswordForm,
    NuevaPasswordForm,
)

# Usuarios
from .usuarios import (
    UsuarioForm,
    UsuarioEditForm,
)

# Productos
from .productos import (
    ProductoPaso1Form,
    ProductoPaso2Form,
    ProductoPaso3Form,
    ProductoEditForm,
)

# Proveedores
from .proveedores import (
    ProveedorForm,
    ProveedorPaso1Form,
    ProveedorPaso2Form,
    ProveedorPaso3Form,
)

# Inventario
from .inventario import (
    MovimientoPaso1Form,
    MovimientoPaso2Form,
    MovimientoPaso3Form,
)

# Ventas
from .ventas import (
    VentaForm,
    DetalleVentaForm,
)

# vacío
__all__ = [
    # Auth
    'LoginForm', 'RecuperarPasswordForm', 'NuevaPasswordForm',
    
    # Usuarios
    'UsuarioForm', 'UsuarioEditForm',
    
    # Productos
    'ProductoPaso1Form', 'ProductoPaso2Form', 'ProductoPaso3Form', 'ProductoEditForm',
    
    # Proveedores
    'ProveedorForm', 'ProveedorPaso1Form', 'ProveedorPaso2Form', 'ProveedorPaso3Form',
    
    # Inventario
    'MovimientoPaso1Form', 'MovimientoPaso2Form', 'MovimientoPaso3Form',
    
    # Ventas
    'VentaForm', 'DetalleVentaForm',
]