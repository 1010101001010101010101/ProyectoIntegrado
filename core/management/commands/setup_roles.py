from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps

# Modelos del ERP (ajusta los nombres si cambian)
MODELOS = {
    'auth.User': ['add', 'change', 'delete', 'view'],
    'core.Usuario': ['add', 'change', 'delete', 'view'],
    'core.Producto': ['add', 'change', 'delete', 'view'],
    'core.Proveedor': ['add', 'change', 'delete', 'view'],
    'core.MovimientoInventario': ['add', 'change', 'delete', 'view'],
    'core.Compra': ['add', 'change', 'delete', 'view'],
    'core.RecepcionCompra': ['add', 'change', 'delete', 'view'],
    'core.DevolucionCompra': ['add', 'change', 'delete', 'view'],
    'core.Bodega': ['add', 'change', 'delete', 'view'],
    'core.Receta': ['add', 'change', 'delete', 'view'],
    'core.OrdenProduccion': ['add', 'change', 'delete', 'view'],
    'core.Cliente': ['add', 'change', 'delete', 'view'],
    'core.Cotizacion': ['add', 'change', 'delete', 'view'],
    'core.PedidoVenta': ['add', 'change', 'delete', 'view'],
    'core.Factura': ['add', 'change', 'delete', 'view'],
    'core.NotaCredito': ['add', 'change', 'delete', 'view'],
    'core.ListaPrecio': ['add', 'change', 'delete', 'view'],
    'core.ReporteFinanciero': ['view'],
    # Agrega otros modelos si los necesitas
}

# Permisos por grupo/rol
GRUPOS_PERMISOS = {
    'ADMIN': {
        'auth.User': ['add', 'change', 'delete', 'view'],
        'core.Usuario': ['add', 'change', 'delete', 'view'],
        'core.Producto': ['add', 'change', 'delete', 'view'],
        'core.Proveedor': ['add', 'change', 'delete', 'view'],
        'core.MovimientoInventario': ['add', 'change', 'delete', 'view'],
        'core.Bodega': ['add', 'change', 'delete', 'view'],
    },
    'BODEGA': {
        'core.MovimientoInventario': ['add', 'change', 'delete', 'view'],
        'core.Bodega': ['add', 'change', 'delete', 'view'],
        'core.Producto': ['view'],
    },
    'CONSULTA': {
        'core.Producto': ['view'],
        'core.Proveedor': ['view'],
        'core.MovimientoInventario': ['view'],
        'core.Bodega': ['view'],
        'core.Usuario': ['view'],
    },
}

class Command(BaseCommand):
    help = 'Configura los grupos de roles y asigna permisos según GRUPOS_PERMISOS.'

    def handle(self, *args, **options):
        for grupo, modelos in GRUPOS_PERMISOS.items():
            group_obj, _ = Group.objects.get_or_create(name=grupo)
            perms_to_set = []
            for modelo, acciones in modelos.items():
                try:
                    app_label, model_name = modelo.split('.')
                    model = apps.get_model(app_label, model_name)
                except LookupError:
                    self.stdout.write(self.style.WARNING(
                        f"Modelo no encontrado: {modelo} (grupo {grupo})"
                    ))
                    continue

                for accion in acciones:
                    codename = f"{accion}_{model._meta.model_name}"
                    try:
                        perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
                        perms_to_set.append(perm)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f"Permiso no encontrado: {app_label}.{codename} (modelo {model_name})"
                        ))

            group_obj.permissions.set(perms_to_set)
            self.stdout.write(self.style.SUCCESS(
                f"Permisos asignados correctamente al grupo {grupo} ({len(perms_to_set)} permisos)"
            ))

        self.stdout.write(self.style.SUCCESS("Configuración de roles y permisos completada."))
