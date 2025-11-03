from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """Solo administradores pueden acceder"""
    def check_admin(user):
        if user.is_authenticated:
            if hasattr(user, 'perfil'):
                return user.perfil.rol == 'admin'
            return user.is_superuser
        return False
    
    decorated_view = user_passes_test(check_admin, login_url='core:dashboard')(view_func)
    return decorated_view

def vendedor_o_admin(view_func):
    """Vendedores y administradores pueden acceder"""
    def check_rol(user):
        if user.is_authenticated:
            if hasattr(user, 'perfil'):
                return user.perfil.rol in ['admin', 'vendedor']
            return user.is_superuser
        return False
    
    decorated_view = user_passes_test(check_rol, login_url='core:dashboard')(view_func)
    return decorated_view