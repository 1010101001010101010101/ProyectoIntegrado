from django import forms
from ..models import MovimientoInventario


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
        fields = ['documento_tipo', 'documento_numero', 'observaciones']
        widgets = {
            'documento_tipo': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }