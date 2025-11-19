from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from ..forms.auth import PasswordInicialForm
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError

from ..models import Usuario, Producto, Proveedor, MovimientoInventario
from ..models.reset import PasswordResetToken
from ..utils import validate_password_policy

def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember')

        if not email or not password:
            messages.error(request, 'Debes ingresar correo y contraseña.')
            return render(request, 'auth/login.html', {'username': email})

        UserModel = get_user_model()
        user_obj = UserModel.objects.filter(email__iexact=email).first()

        perfil = getattr(user_obj, 'perfil', None)
        if perfil and perfil.bloqueado:
            messages.error(request, 'Tu cuenta está bloqueada por múltiples intentos fallidos. Contacta al administrador.')
            return render(request, 'auth/login.html', {'username': email})

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
        else:
            user = None

        if user is not None:
            # Login exitoso: resetear intentos fallidos
            if perfil:
                perfil.intentos_fallidos = 0
                perfil.save()
            login(request, user)
            request.session.set_expiry(1209600 if remember else 0)

            if perfil:
                perfil.ultimo_acceso = timezone.now()
                perfil.save()
                if perfil.must_change_password:
                    request.session['force_password_change'] = user.id
                    messages.warning(request, 'Por seguridad, cambia tu contraseña antes de continuar.')
                    return redirect('core:cambiar_password_inicial')

            messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.email}!')
            return redirect('core:dashboard')
        else:
            # Fallo: aumentar intentos y bloquear si supera el límite
            if perfil:
                perfil.intentos_fallidos += 1
                if perfil.intentos_fallidos >= 5:
                    perfil.bloqueado = True
                    messages.error(request, 'Tu cuenta ha sido bloqueada por demasiados intentos fallidos.')
                else:
                    messages.error(request, f'Correo o contraseña incorrectos. Intentos fallidos: {perfil.intentos_fallidos}/5')
                perfil.save()
            else:
                messages.error(request, 'Correo o contraseña incorrectos')
            return render(request, 'auth/login.html', {'username': email})

    return render(request, 'auth/login.html')


@require_POST
@login_required
def logout_view(request):
    """Cerrar sesión"""
    logout(request)
    request.session.flush()
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('core:login')


@login_required
def dashboard(request):
    """Dashboard principal"""
    perfil = getattr(request.user, 'perfil', None)
    rol = getattr(perfil, 'rol', 'ADMIN').upper() if perfil else 'ADMIN'

    permisos_por_rol = {
        'ADMIN':     {'usuarios': True,  'productos': True,  'proveedores': True,  'movimientos': True},
        'BODEGA':    {'usuarios': False, 'productos': True,  'proveedores': True,  'movimientos': True},
        'CONSULTA':  {'usuarios': False, 'productos': False, 'proveedores': False, 'movimientos': True},
    }
    permisos_dashboard = permisos_por_rol.get(rol, permisos_por_rol['ADMIN'])

    context = {
        'total_usuarios': Usuario.objects.filter(user__is_active=True).count(),
        'total_productos': Producto.objects.filter(activo=True).count(),
        'total_proveedores': Proveedor.objects.filter(estado='ACTIVO').count(),
        'total_movimientos': MovimientoInventario.objects.count(),
        'productos_bajo_stock': Producto.objects.filter(alerta_bajo_stock=True).count(),
        'permisos_dashboard': permisos_dashboard,
        'rol_usuario': rol,
    }
    return render(request, 'dashboard.html', context)


def recuperar_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Ingresa tu correo electrónico.')
            return redirect('core:recuperar_password')

        user_model = get_user_model()
        user = user_model.objects.filter(email__iexact=email).first()

        if user:
            token = PasswordResetToken.objects.create(user=user)
            reset_url = request.build_absolute_uri(
                reverse('core:validar_token', args=[token.token])
            )
            send_mail(
                'Recupera tu contraseña',
                f'Hola, usa este enlace para crear una nueva contraseña: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )

        messages.success(request, 'Si el correo está registrado recibirás un enlace de recuperación.')
        return redirect('core:recuperar_password')

    return render(request, 'auth/recuperar_password.html')


def validar_token(request, token):
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'El enlace no es válido.')
        return redirect('core:recuperar_password')

    if not token_obj.is_valid():
        token_obj.delete()
        messages.error(request, 'El enlace expiró.')
        return redirect('core:recuperar_password')

    request.session['password_reset_user'] = token_obj.user_id
    request.session['password_reset_token'] = str(token_obj.token)
    return redirect('core:nueva_password')


def nueva_password(request):
    user_id = request.session.get('password_reset_user')
    token_value = request.session.get('password_reset_token')
    if not user_id or not token_value:
        return redirect('core:recuperar_password')

    token_qs = PasswordResetToken.objects.filter(token=token_value, user_id=user_id)
    if not token_qs.exists():
        return redirect('core:recuperar_password')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')
        try:
            validate_password_policy(password)
        except ValidationError as exc:
            messages.error(request, exc.message)
            return redirect('core:nueva_password')
        if password != confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('core:nueva_password')

        user = get_user_model().objects.get(pk=user_id)
        user.set_password(password)
        user.save()
        token_qs.delete()
        request.session.pop('password_reset_user', None)
        request.session.pop('password_reset_token', None)
        messages.success(request, 'Contraseña actualizada. Inicia sesión.')
        return redirect('core:login')

    return render(request, 'auth/nueva_password.html')

@login_required
def cambiar_password_inicial(request):
    """Cambiar contraseña inicial"""
    if request.session.get('force_password_change') != request.user.id:
        return redirect('core:dashboard')

    import datetime
    from django.utils import timezone
    perfil = request.user.perfil
    dias_restriccion = 15  # Plazo ajustado a 15 días
    puede_cambiar = True
    if perfil.ultima_modificacion_password:
        diferencia = timezone.now() - perfil.ultima_modificacion_password
        if diferencia.days < dias_restriccion:
            puede_cambiar = False
    if request.method == 'POST':
        form = PasswordInicialForm(request.POST)
        if not puede_cambiar:
            messages.error(request, f'Solo puedes cambiar tu contraseña cada {dias_restriccion} días. Último cambio: {perfil.ultima_modificacion_password.strftime("%d/%m/%Y")}')
        elif form.is_valid():
            new_password = form.cleaned_data['password1']
            user = request.user
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)

            perfil.must_change_password = False
            perfil.ultima_modificacion_password = timezone.now()
            perfil.save()

            request.session.pop('force_password_change', None)
            messages.success(request, 'Contraseña actualizada correctamente.')
            return redirect('core:dashboard')
    else:
        form = PasswordInicialForm()

    return render(request, 'auth/cambiar_password_inicial.html', {'form': form})

@login_required
def cambiar_password(request):
    """Cambiar contraseña"""
    # Permitir acceso a cualquier usuario autenticado
    import datetime
    from django.utils import timezone
    perfil = Usuario.objects.get(user=request.user)
    dias_restriccion = 15  # Plazo ajustado a 15 días
    puede_cambiar = True
    if perfil.ultima_modificacion_password:
        diferencia = timezone.now() - perfil.ultima_modificacion_password
        if diferencia.days < dias_restriccion:
            puede_cambiar = False
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if not puede_cambiar:
            messages.error(request, f'Solo puedes cambiar tu contraseña cada {dias_restriccion} días. Último cambio: {perfil.ultima_modificacion_password.strftime("%d/%m/%Y")}')
        elif form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            perfil.ultima_modificacion_password = timezone.now()
            if perfil.must_change_password:
                messages.warning(request, 'Por seguridad, cambia tu contraseña antes de continuar.')
                perfil.save()
                request.session['force_password_change'] = user.id
                return redirect('core:cambiar_password_inicial')
            perfil.must_change_password = False
            perfil.save()
            request.session.pop('force_password_change', None)
            messages.success(request, 'Contraseña actualizada.')
            return redirect('core:dashboard')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'auth/cambiar_password.html', {'form': form})

def crear_usuario_view(request):
    """Vista para crear un nuevo usuario"""
    from core.forms.usuarios import UsuarioForm
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            perfil, created = Usuario.objects.get_or_create(user=user)
            perfil.rol = form.cleaned_data['rol']  # ← Asigna el rol seleccionado
            perfil.estado = form.cleaned_data['estado']
            perfil.telefono = form.cleaned_data.get('telefono', '')
            perfil.direccion = form.cleaned_data.get('direccion', '')
            perfil.must_change_password = True
            perfil.save()
            messages.success(request, 'Usuario creado exitosamente. Ahora puedes iniciar sesión.')
            return redirect('core:login')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/crear_usuario.html', {'form': form})