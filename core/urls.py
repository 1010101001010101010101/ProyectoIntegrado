# core/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import usuarios as user_views
from .views import productos as product_views
from .views import inventario as inventario_views
from core.views.inventario import exportar_movimientos_excel, eliminar_movimiento, productos_por_proveedor, proveedor_por_producto, proveedores_por_producto
from core.views.usuarios import exportar_usuarios_excel
from core.views.bodegas import crear_bodega_ajax
 # ...existing code...

app_name = 'core'

urlpatterns = [
    # ===== AUTENTICACIÓN =====
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cambiar-password-inicial/', views.cambiar_password_inicial, name='cambiar_password_inicial'),
    path('recuperar-password/', views.recuperar_password, name='recuperar_password'),
    path('validar-token/<str:token>/', views.validar_token, name='validar_token'),
    path('nueva-password/', views.nueva_password, name='nueva_password'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),

    # ===== REPORTES =====
    path('reportes/', views.reportes_view, name='reportes'),
    # ===== USUARIOS =====
    path('usuarios/', user_views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', user_views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:id>/editar/', user_views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:id>/eliminar/', user_views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/<int:id>/reactivar/', user_views.reactivar_usuario, name='reactivar_usuario'),
    path('usuarios/exportar-excel/', exportar_usuarios_excel, name='exportar_usuarios_excel'),  # <-- aquí, dentro de urlpatterns

    # ===== PRODUCTOS =====
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/crear/paso1/', views.producto_paso1, name='producto_paso1'),
    path('productos/crear/paso2/', views.producto_paso2, name='producto_paso2'),
    path('productos/crear/paso3/', views.producto_paso3, name='producto_paso3'),
    path('productos/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto_compat'),  # compat
    path('productos/exportar-excel/', views.exportar_productos_excel, name='exportar_productos_excel'),
    path('productos/buscar-ajax/', product_views.buscar_productos_ajax, name='buscar_productos_ajax'),  # ← aquí

    # ===== PROVEEDORES =====
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedores/paso1/', views.proveedor_paso1, name='proveedor_paso1'),
    path('proveedores/paso2/', views.proveedor_paso2, name='proveedor_paso2'),  
    path('proveedores/paso3/', views.proveedor_paso3, name='proveedor_paso3'),
    path('proveedores/<int:pk>/editar/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/<int:pk>/eliminar/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('proveedores/<int:pk>/estado/', views.cambiar_estado_proveedor, name='cambiar_estado_proveedor'),
    path('proveedores/exportar/', views.exportar_proveedores_excel, name='exportar_proveedores_excel'),
    path('proveedores/buscar-ajax/', views.buscar_proveedores_ajax, name='buscar_proveedores_ajax'),

    # ===== INVENTARIO =====
    path('movimientos/', inventario_views.lista_movimientos, name='lista_movimientos'),
    path('movimientos/<int:pk>/editar/', inventario_views.editar_movimiento, name='editar_movimiento'),
    path('movimientos/crear/', inventario_views.crear_movimiento, name='crear_movimiento'),
    path('movimientos/crear/paso1/', inventario_views.movimiento_paso1, name='movimiento_paso1'),
    path('movimientos/crear/paso2/', inventario_views.movimiento_paso2, name='movimiento_paso2'),
    path('movimientos/crear/paso3/', inventario_views.movimiento_paso3, name='movimiento_paso3'),
    path('movimientos/exportar/', exportar_movimientos_excel, name='exportar_movimientos_excel'),
    path('movimientos/eliminar/<int:pk>/', eliminar_movimiento, name='eliminar_movimiento'),
    path('ajax/productos_por_proveedor/', productos_por_proveedor, name='productos_por_proveedor'),
    path('ajax/proveedor_por_producto/', proveedor_por_producto, name='proveedor_por_producto'),
    path('ajax/proveedores_por_producto/', proveedores_por_producto, name='proveedores_por_producto'),
    path('movimientos/buscar-ajax/', inventario_views.buscar_movimientos_ajax, name='buscar_movimientos_ajax'),

    # ===== VENTAS =====
    path('ventas/', views.lista_ventas, name='lista_ventas'),
    path('ventas/crear/', views.crear_venta, name='crear_venta'),
    path('ventas/<int:pk>/', views.detalle_venta, name='detalle_venta'),
    path('bodegas/crear/', crear_bodega_ajax, name='crear_bodega_ajax'),

    # ===== USUARIOS AJAX =====
    path('usuarios/buscar-ajax/', user_views.buscar_usuarios_ajax, name='buscar_usuarios_ajax'),

    # ...existing code...
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)