from django import forms
from core.models.proveedores import Proveedor
from django.forms import formset_factory
from core.models.productos import Producto
from decimal import Decimal

def _normaliza_rut(value: str) -> str:
    if not value:
        return ''
    return value.replace('.', '').replace('-', '').upper()

def _valida_rut(rut: str) -> bool:
    if len(rut) < 2 or not rut[:-1].isdigit():
        return False
    cuerpo, dv = rut[:-1], rut[-1]
    factor, total = 2, 0
    for digit in reversed(cuerpo):
        total += int(digit) * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - (total % 11)
    dv_esperado = '0' if resto == 11 else 'K' if resto == 10 else str(resto)
    return dv_esperado == dv

def _formatea_rut(rut: str) -> str:
    cuerpo, dv = rut[:-1], rut[-1]
    cuerpo_formateado = f"{int(cuerpo):,}".replace(',', '.')
    return f"{cuerpo_formateado}-{dv}"

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'rut', 'razon_social', 'nombre_fantasia', 'email', 'telefono', 'sitio_web',
            'direccion', 'comuna', 'ciudad', 'region',
            'observaciones', 'estado', 'lead_time', 'pedido_minimo', 'es_proveedor_preferente',
        ]
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 4}),
            'estado': forms.Select(),
        }

    def clean_rut(self):
        rut = _normaliza_rut(self.cleaned_data['rut'])
        if not _valida_rut(rut):
            raise forms.ValidationError('El RUT ingresado no es válido.')
        return _formatea_rut(rut)


class ProveedorPaso1Form(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        label='email',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'contacto@proveedor.cl',
            'autocomplete': 'email',
        })
    )

    class Meta:
        model = Proveedor
        fields = ['rut', 'razon_social', 'nombre_fantasia', 'email', 'telefono', 'sitio_web']
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '76.543.210-5',
                'autocomplete': 'off',
                'maxlength': 12,
            }),
            'razon_social': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Distribuidora DulcesSur',
            }),
            'nombre_fantasia': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'DulceSur',
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+56 9 1234 5678',
            }),
            'sitio_web': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://proveedor.cl',
            }),
        }
        labels = {
            'rut': 'rut_nif',
            'razon_social': 'razon_social',
            'nombre_fantasia': 'nombre_fantasia',
            'telefono': 'telefono',
            'sitio_web': 'sitio_web',
        }

    def clean_rut(self):
        rut = _normaliza_rut(self.cleaned_data['rut'])
        if not _valida_rut(rut):
            raise forms.ValidationError('El RUT ingresado no es válido.')
        return _formatea_rut(rut)

    def clean_razon_social(self):
        valor = self.cleaned_data['razon_social'].strip()
        if not valor:
            raise forms.ValidationError('Este campo es obligatorio.')
        return valor


class ProveedorPaso2Form(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['direccion', 'comuna', 'ciudad', 'region']
        widgets = {
            'direccion': forms.TextInput(attrs={'placeholder': 'Calle 123, Oficina 456'}),
        }


class ProveedorPaso3Form(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['observaciones', 'estado', 'lead_time', 'pedido_minimo', 'es_proveedor_preferente']
        widgets = {
            'observaciones': forms.Textarea(attrs={
                'rows': 5,
                'id': 'observaciones',
                'placeholder': 'Notas adicionales sobre el proveedor, acuerdos especiales, historial, etc.'
            }),
            'estado': forms.Select(attrs={'id': 'estado'}),
            'lead_time': forms.NumberInput(attrs={'min': 0, 'id': 'lead_time', 'placeholder': '7'}),
            'pedido_minimo': forms.NumberInput(attrs={'min': 0, 'step': 0.01, 'id': 'pedido_minimo', 'placeholder': '10000'}),
            'es_proveedor_preferente': forms.CheckboxInput(attrs={'id': 'es_proveedor_preferente'}),
        }
        labels = {
            'observaciones': 'Observaciones generales (opcional)',
            'estado': 'Estado (requerido)',
            'lead_time': 'Lead Time (días) (opcional)',
            'pedido_minimo': 'Pedido mínimo (opcional)',
            'es_proveedor_preferente': 'Marcar como proveedor preferente (opcional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lead_time'].required = False
        self.fields['pedido_minimo'].required = False
        self.fields['es_proveedor_preferente'].required = False

class ProveedorProductoForm(forms.Form):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(activo=True),
        label='Producto',
        required=False,
        empty_label='Selecciona un producto'
    )
    costo = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        label='Costo',
        required=False
    )
    lead_time = forms.IntegerField(
        min_value=0,
        label='Lead Time (días)',
        required=False
    )
    activo = forms.BooleanField(
        required=False,
        initial=False,
        label='Activo'
    )

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        costo = cleaned_data.get('costo')
        lead_time = cleaned_data.get('lead_time')
        activo = cleaned_data.get('activo')

        if not producto:
            if not self.has_changed():
                cleaned_data['__omit__'] = True
                return cleaned_data
            if all(value in (None, '', 0, Decimal('0')) for value in (costo, lead_time)) and not activo:
                cleaned_data['__omit__'] = True
                return cleaned_data
            self.add_error('producto', 'Selecciona un producto.')
            return cleaned_data

        if costo in (None, ''):
            self.add_error('costo', 'Ingresa un costo.')

        if lead_time in (None, ''):
            cleaned_data['lead_time'] = 0

        return cleaned_data

ProveedorProductoFormSet = formset_factory(
    ProveedorProductoForm,
    extra=1,
    can_delete=True
)