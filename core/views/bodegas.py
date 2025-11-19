from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from core.models import Bodega

@csrf_exempt
@require_POST
def crear_bodega_ajax(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        codigo = data.get('codigo', '').strip().upper()
        nombre = data.get('nombre', '').strip()
        if not codigo or len(codigo) < 3:
            return JsonResponse({'ok': False, 'error': 'Código inválido'})
        if not nombre or len(nombre) < 3:
            return JsonResponse({'ok': False, 'error': 'Nombre inválido'})
        if Bodega.objects.filter(codigo=codigo).exists():
            return JsonResponse({'ok': False, 'error': 'Ya existe una bodega con ese código'})
        bodega = Bodega.objects.create(codigo=codigo, nombre=nombre)
        return JsonResponse({'ok': True, 'codigo': bodega.codigo, 'nombre': bodega.nombre})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})
