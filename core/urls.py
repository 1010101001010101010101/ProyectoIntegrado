from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
# Autenticación
    path('recuperar-password/', views.recuperar_password, name='recuperar_password'),
    path('validar-token/', views.validar_token, name='validar_token'),
    path('validar-token/<str:token>/', views.validar_token, name='validar_token_param'),
    path('nueva-password/', views.nueva_password, name='nueva_password'),

    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    
    # Productos - Con pasos separados
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/crear/paso1/', views.producto_paso1, name='producto_paso1'),
    path('productos/crear/paso2/', views.producto_paso2, name='producto_paso2'),
    path('productos/crear/paso3/', views.producto_paso3, name='producto_paso3'),
    path('productos/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    
    # Proveedores
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/editar/<int:id>/', views.editar_proveedor, name='editar_proveedor'),
    
    # Inventario - Movimientos con pasos separados
    path('inventario/', views.lista_movimientos, name='lista_movimientos'),
    path('inventario/crear/', views.crear_movimiento, name='crear_movimiento'),
    path('inventario/crear/paso1/', views.movimiento_paso1, name='movimiento_paso1'),
    path('inventario/crear/paso2/', views.movimiento_paso2, name='movimiento_paso2'),
    path('inventario/crear/paso3/', views.movimiento_paso3, name='movimiento_paso3'),
    path('inventario/editar/<int:id>/', views.editar_movimiento, name='editar_movimiento'),
    

    # Agregar estas rutas al archivo urls.py existente, dentro de urlpatterns

# Proveedores - Con pasos separados
path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
path('proveedores/crear/paso1/', views.proveedor_paso1, name='proveedor_paso1'),
path('proveedores/crear/paso2/', views.proveedor_paso2, name='proveedor_paso2'),
path('proveedores/crear/paso3/', views.proveedor_paso3, name='proveedor_paso3'),

path('proveedores/editar/<int:id>/', views.editar_proveedor, name='editar_proveedor'),
]