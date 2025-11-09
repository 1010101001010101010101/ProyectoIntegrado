"""
CRUD completo de Usuarios - EVA Sumativa 3
CORREGIDO: Paginación, Ordenamiento y Búsqueda funcionando correctamente
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q

from ..decorators import admin_required
from ..models import Usuario, Producto
from ..forms import UsuarioForm, UsuarioEditForm

User = get_user_model()

PAGE_SIZE_CHOICES = [5, 15, 30]

def _resolve_page_size(request, session_key, default=15):
    if 'page_size' in request.GET:
        try:
            value = int(request.GET['page_size'])
            if value in PAGE_SIZE_CHOICES:
                request.session[session_key] = value
        except (TypeError, ValueError):
            pass
    return request.session.get(session_key, default)

@login_required
@admin_required
def lista_usuarios(request):
    """
    Lista de usuarios con búsqueda, filtros, orden y paginación configurable
    MEJORADO: Preserva filtros y maneja paginación correctamente
    """
    # ========================================
    # 1. CAPTURAR PARÁMETROS DE FILTROS
    # ========================================
    buscar = request.GET.get('buscar', '').strip()
    rol_filtro = request.GET.get('rol', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()

    # ========================================
    # 2. PAGINADOR CONFIGURABLE
    # ========================================
    page_size_options = [5, 15, 30]
    if 'page_size' in request.GET:
        try:
            page_size = int(request.GET.get('page_size', 15))
        except ValueError:
            page_size = 15
        if page_size not in page_size_options:
            page_size = 15
        request.session['usuarios_page_size'] = page_size
    else:
        page_size = int(request.session.get('usuarios_page_size', 15))

    # ========================================
    # 3. ORDENAMIENTO (con preservación de filtros)
    # ========================================
    orden = request.GET.get('orden', 'creado').lower()
    direccion = request.GET.get('dir', 'desc').lower()
    
    # Validar dirección
    if direccion not in ['asc', 'desc']:
        direccion = 'asc'
    
    # Prefijo para ordenamiento descendente
    dir_prefix = '' if direccion == 'asc' else '-'
    
    # Mapeo de campos para ordenamiento
    orden_map = {
        'username': 'user__username',
        'nombre': 'user__first_name',
        'email': 'user__email',
        'rol': 'rol',
        'estado': 'user__is_active',
        'creado': 'user__date_joined',
    }
    
    # Campo de ordenamiento (default: fecha de creación)
    orden_field = orden_map.get(orden, 'user__date_joined')

    # ========================================
    # 4. QUERY BASE
    # ========================================
    usuarios = Usuario.objects.select_related('user').all()

    # ========================================
    # 5. APLICAR FILTROS DE BÚSQUEDA
    # ========================================
    if buscar:
        usuarios = usuarios.filter(
            Q(user__username__icontains=buscar) |
            Q(user__email__icontains=buscar) |
            Q(user__first_name__icontains=buscar) |
            Q(user__last_name__icontains=buscar) |
            Q(telefono__icontains=buscar)
        )
    
    if rol_filtro:
        usuarios = usuarios.filter(rol=rol_filtro)
    
    if estado_filtro:
        if estado_filtro == 'ACTIVO':
            usuarios = usuarios.filter(user__is_active=True)
        elif estado_filtro == 'INACTIVO':
            usuarios = usuarios.filter(user__is_active=False)

    # ========================================
    # 6. APLICAR ORDENAMIENTO
    # ========================================
    if orden == 'nombre':
        # Caso especial: ordenar por nombre completo
        usuarios = usuarios.order_by(
            f'{dir_prefix}user__first_name',
            f'{dir_prefix}user__last_name',
            '-user__date_joined'
        )
    else:
        # Ordenamiento normal con fallback a fecha
        usuarios = usuarios.order_by(
            f'{dir_prefix}{orden_field}',
            '-user__date_joined'
        )

    # ========================================
    # 7. PAGINACIÓN
    # ========================================
    paginator = Paginator(usuarios, page_size)
    page_number = request.GET.get('page', 1)
    
    # Obtener página (maneja errores automáticamente)
    page_obj = paginator.get_page(page_number)

    # ========================================
    # 8. CONSTRUIR QUERYSTRING BASE (sin 'page')
    # Para preservar filtros en paginación
    # ========================================
    params = request.GET.copy()
    params.pop('page', None)  # Remover 'page' para no duplicar
    base_qs = params.urlencode()

    # ========================================
    # 9. RANGO DE PAGINACIÓN CON ELIPSIS
    # ========================================
    # Django 3.2+ tiene get_elided_page_range
    try:
        elided_range = list(paginator.get_elided_page_range(
            page_obj.number,
            on_each_side=2,
            on_ends=1
        ))
        ellipsis_const = paginator.ELLIPSIS
    except AttributeError:
        # Fallback para versiones antiguas de Django
        elided_range = list(range(1, paginator.num_pages + 1))
        ellipsis_const = '…'

    # ========================================
    # 10. CONTEXTO PARA EL TEMPLATE
    # ========================================
    context = {
        # Paginación
        'page_obj': page_obj,
        'usuarios': page_obj.object_list,
        'total_usuarios': paginator.count,
        'page_size': page_size,
        'page_size_options': page_size_options,
        
        # Filtros aplicados
        'buscar': buscar,
        'rol_filtro': rol_filtro,
        'estado_filtro': estado_filtro,
        'roles_choices': Usuario.ROL_CHOICES,
        
        # Ordenamiento
        'orden': orden,
        'dir': direccion,
        
        # Querystring base (para preservar filtros)
        'base_qs': base_qs,
        
        # Rango de páginas con elipsis
        'elided_range': elided_range,
        'ELLIPSIS': ellipsis_const,
    }
    
    return render(request, 'usuarios/lista_usuarios.html', context)


@login_required
@admin_required
def crear_usuario(request):
    """
    Crear nuevo usuario con validaciones
    """
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = form.cleaned_data['estado'] == 'ACTIVO'
                user.set_password(form.cleaned_data['password'])
                user.save()

                Usuario.objects.create(
                    user=user,
                    rol=form.cleaned_data['rol'],
                    estado=form.cleaned_data['estado'],
                    telefono=form.cleaned_data.get('telefono', ''),
                    direccion=form.cleaned_data.get('direccion', '')
                )

                messages.success(request, f'Usuario {user.username} creado exitosamente.')
                return redirect('core:lista_usuarios')
                
            except Exception as e:
                messages.error(
                    request,
                    f'❌ Error al crear usuario: {str(e)}',
                    extra_tags='error'
                )
        else:
            error_items = []
            for field, errors in form.errors.get_json_data().items():
                label = form.fields.get(field, None)
                name = label.label if label else field.replace('_', ' ').title()
                error_items.append(f'{name}: {errors[0]["message"]}')
            messages.error(
                request,
                '⚠️ Corrige los errores:<br><ul>' + ''.join(f'<li>{item}</li>' for item in error_items) + '</ul>',
                extra_tags='error safe'
            )
    else:
        form = UsuarioForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Usuario',
        'accion': 'Crear',
    }
    
    return render(request, 'usuarios/crear_usuario.html', context)


@login_required
@admin_required
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario.user)
        if form.is_valid():
            try:
                user = form.save()
                usuario.telefono = form.cleaned_data.get('telefono', '')
                usuario.direccion = form.cleaned_data.get('direccion', '')
                usuario.rol = form.cleaned_data.get('rol', usuario.rol)
                usuario.estado = form.cleaned_data.get('estado', usuario.estado)
                user.is_active = usuario.estado == 'ACTIVO'
                user.save()
                usuario.save()

                messages.success(
                    request,
                    f'✅ Usuario <strong>{user.username}</strong> actualizado correctamente',
                    extra_tags='success safe'
                )
                return redirect('core:lista_usuarios')
            except Exception as e:
                messages.error(request, f'❌ Error al actualizar: {e}', extra_tags='error safe')
        else:
            error_items = []
            for field, errors in form.errors.get_json_data().items():
                label = form.fields.get(field, None)
                name = label.label if label else field.replace('_', ' ').title()
                error_items.append(f'{name}: {errors[0]["message"]}')
            messages.error(
                request,
                '⚠️ Corrige los errores:<br><ul>' + ''.join(f'<li>{item}</li>' for item in error_items) + '</ul>',
                extra_tags='error safe'
            )
    else:
        form = UsuarioEditForm(
            instance=usuario.user,
            initial={
                'telefono': usuario.telefono,
                'direccion': usuario.direccion,
                'rol': usuario.rol,
                'estado': usuario.estado,
            }
        )
    
    context = {
        'form': form,
        'usuario': usuario,
        'titulo': f'Editar Usuario: {usuario.user.username}',
        'accion': 'Guardar cambios',
    }
    
    return render(request, 'usuarios/editar_usuario.html', context)


@login_required
@admin_required
@require_POST
def eliminar_usuario(request, id):
    """
    Eliminar usuario con validaciones:
    - Eliminación lógica si tiene registros asociados
    - Eliminación física si no tiene registros
    """
    usuario = get_object_or_404(Usuario, id=id)
    
    # Validación 1: No puede eliminarse a sí mismo
    if usuario.user == request.user:
        messages.error(
            request,
            '❌ No puedes eliminar tu propio usuario',
            extra_tags='error safe'
        )
        return redirect('core:lista_usuarios')
    
    # Validación 2: No puede eliminar superusuarios
    if usuario.user.is_superuser:
        messages.error(
            request,
            '❌ No se puede eliminar al superusuario',
            extra_tags='error safe'
        )
        return redirect('core:lista_usuarios')
    
    try:
        # Verificar registros asociados
        tiene_movimientos = hasattr(usuario, 'movimientos') and usuario.movimientos.exists()
        tiene_ventas = hasattr(usuario, 'ventas') and usuario.ventas.exists()
        
        if tiene_movimientos or tiene_ventas:
            # ELIMINACIÓN LÓGICA
            usuario.user.is_active = False
            usuario.user.save()
            usuario.estado = 'INACTIVO'
            usuario.save()
            
            count_mov = usuario.movimientos.count() if tiene_movimientos else 0
            count_ventas = usuario.ventas.count() if tiene_ventas else 0
            
            messages.warning(
                request,
                f'⚠️ Usuario <strong>{usuario.user.username}</strong> desactivado '
                f'(tiene {count_mov} movimientos y {count_ventas} ventas asociadas). '
                f'No se puede eliminar permanentemente.',
                extra_tags='warning safe'
            )
        else:
            # ELIMINACIÓN FÍSICA
            username = usuario.user.username
            usuario.user.delete()
            
            messages.success(
                request,
                f'✅ Usuario <strong>{username}</strong> eliminado permanentemente del sistema',
                extra_tags='success safe'
            )
    
    except Exception as e:
        messages.error(
            request,
            f' Error al eliminar usuario: {str(e)}',
            extra_tags='error safe'
        )
    
    return redirect('core:lista_usuarios')


@login_required
@admin_required
def reactivar_usuario(request, id):
    """
    Reactivar un usuario previamente desactivado
    """
    usuario = get_object_or_404(Usuario, id=id)
    
    if usuario.user.is_active:
        messages.info(
            request,
            f'ℹ️ El usuario {usuario.user.username} ya está activo',
            extra_tags='info'
        )
    else:
        usuario.user.is_active = True
        usuario.user.save()
        usuario.estado = 'ACTIVO'
        usuario.save()
        
        messages.success(
            request,
            f'✅ Usuario <strong>{usuario.user.username}</strong> reactivado exitosamente',
            extra_tags='success safe'
        )
    
    return redirect('core:lista_usuarios')

