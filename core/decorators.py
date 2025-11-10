"""
Decoradores de permisos para vistas
ROLES: ADMIN (full), EDITOR/BODEGA (crear/editar), LECTOR (solo ver)
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    """Solo ADMIN puede acceder"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:login')
        
        # Verificar perfil
        perfil = getattr(request.user, 'perfil', None)
        if perfil and perfil.rol == 'ADMIN':
            return view_func(request, *args, **kwargs)
        
        # Superusuario Django
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, '⚠️ Solo administradores pueden acceder a esta sección')
        return redirect('core:dashboard')
    
    return wrapper


def editor_o_admin_required(view_func):
    """ADMIN, EDITOR y BODEGA pueden acceder (crear/editar)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:login')
        
        perfil = getattr(request.user, 'perfil', None)
        if perfil and perfil.rol in ['ADMIN', 'EDITOR', 'BODEGA']:
            return view_func(request, *args, **kwargs)
        
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, '⚠️ No tienes permisos para realizar esta acción')
        return redirect('core:dashboard')
    
    return wrapper


def lector_o_superior(view_func):
    """Todos los roles autenticados pueden ver (ADMIN, EDITOR, BODEGA, LECTOR)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:login')
        
        perfil = getattr(request.user, 'perfil', None)
        if perfil and perfil.rol in ['ADMIN', 'EDITOR', 'BODEGA', 'LECTOR', 'VENDEDOR', 'SUPERVISOR']:
            return view_func(request, *args, **kwargs)
        
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, '⚠️ Debes tener un rol asignado')
        return redirect('core:dashboard')
    
    return wrapper


# Alias para compatibilidad
bodeguero_o_admin_required = editor_o_admin_required
vendedor_o_admin = lector_o_superior
bodeguero_required = editor_o_admin_required