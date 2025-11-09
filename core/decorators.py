from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    """Decorador que verifica si el usuario es administrador"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:login')
        
        # Verificar si tiene perfil de Usuario y es admin
        if hasattr(request.user, 'perfil'):
            if request.user.perfil.rol == 'ADMIN':
                return view_func(request, *args, **kwargs)
        
        # Si es superusuario de Django
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, '⚠️ No tienes permisos para acceder a esta sección')
        return redirect('core:dashboard')
    
    return wrapper


def vendedor_o_admin(view_func):
    """Permite acceso a vendedores y administradores"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:login')
        
        if hasattr(request.user, 'perfil'):
            if request.user.perfil.rol in ['ADMIN', 'VENDEDOR', 'SUPERVISOR']:
                return view_func(request, *args, **kwargs)
        
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, '⚠️ No tienes permisos para acceder a esta sección')
        return redirect('core:dashboard')
    
    return wrapper


def bodeguero_required(view_func):
    """Solo bodegueros y admins pueden acceder"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:login')
        
        if hasattr(request.user, 'perfil'):
            if request.user.perfil.rol in ['ADMIN', 'BODEGUERO']:
                return view_func(request, *args, **kwargs)
        
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, '⚠️ Solo bodegueros pueden realizar esta acción')
        return redirect('core:dashboard')
    
    return wrapper