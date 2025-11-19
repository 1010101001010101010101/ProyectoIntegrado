from django import forms
from ..models import Venta, DetalleVenta


class VentaForm(forms.ModelForm):
    """Formulario de venta"""
    
    class Meta:
        model = Venta
        fields = ['cliente', 'tipo_pago', 'observaciones']
        widgets = {
            'cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_pago': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DetalleVentaForm(forms.ModelForm):
    """Formulario de detalle de venta"""
    
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }