from django.shortcuts import redirect
from django.urls import reverse

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            perfil = getattr(user, 'perfil', None)
            if perfil and perfil.must_change_password:
                if request.path != reverse('core:cambiar_password_inicial'):
                    return redirect('core:cambiar_password_inicial')
        return self.get_response(request)
