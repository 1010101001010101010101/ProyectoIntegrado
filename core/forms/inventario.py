from django import forms
from ..models import MovimientoInventario
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404


class MovimientoPaso1Form(forms.ModelForm):
    """Paso 1: Datos básicos del movimiento"""
    
    producto_sku = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SKU del producto'})
    )
    bodega_codigo = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código de bodega'})
    )
    
    class Meta:
        model = MovimientoInventario
        fields = ['tipo_movimiento', 'cantidad', 'motivo']
        widgets = {
            'tipo_movimiento': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MovimientoPaso2Form(forms.ModelForm):
    """Paso 2: Lote y serie"""
    
    class Meta:
        model = MovimientoInventario
        fields = ['lote', 'numero_serie', 'fecha_vencimiento']
        widgets = {
            'lote': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class MovimientoPaso3Form(forms.ModelForm):
    """Paso 3: Documentos"""
    
    class Meta:
        model = MovimientoInventario
        fields = ['documento_tipo', 'documento_numero', 'motivo', 'observaciones']
        widgets = {
            'documento_tipo': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

def movimiento_create(request):
    if request.method == 'POST':
        form = MovimientoPaso1Form(request.POST)
        if form.is_valid():
            movimiento = form.save()
            messages.success(request, '✓ Paso 1 completado')
            return redirect('core:movimiento_paso2', pk=movimiento.pk)
    else:
        form = MovimientoPaso1Form()
    return render(request, 'core/movimiento_paso1.html', {'form': form})

def movimiento_paso2(request, pk):
    movimiento = get_object_or_404(MovimientoInventario, pk=pk)
    if request.method == 'POST':
        form = MovimientoPaso2Form(request.POST, instance=movimiento)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Paso 2 completado')
            return redirect('core:movimiento_paso3', pk=movimiento.pk)
    else:
        form = MovimientoPaso2Form(instance=movimiento)
    return render(request, 'core/movimiento_paso2.html', {'form': form})

def movimiento_paso3(request, pk):
    movimiento = get_object_or_404(MovimientoInventario, pk=pk)
    if request.method == 'POST':
        form = MovimientoPaso3Form(request.POST, instance=movimiento)
        if form.is_valid():
            form.save()
            del request.session['movimiento_id']
            messages.success(request, '✓ Movimiento registrado')
            return redirect('core:lista_movimientos')
    else:
        form = MovimientoPaso3Form(instance=movimiento)
    return render(request, 'core/movimiento_paso3.html', {'form': form})