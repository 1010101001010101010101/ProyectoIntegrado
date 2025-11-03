# core/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Usuario, Producto, Proveedor, ProductoProveedor, Bodega, MovimientoInventario, Categoria
from django.core.exceptions import ValidationError
import re

# ===============================================
# FORMULARIO: USUARIO
# ===============================================
class UsuarioForm(forms.ModelForm):
    # Campos del modelo User
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'usuario123'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@ejemplo.com'})
    )
    nombres = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Juan'})
    )
    apellidos = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pérez'})
    )
    password = forms.CharField(
        max_length=128,
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
    confirmar_password = forms.CharField(
        max_length=128,
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )

    class Meta:
        model = Usuario
        fields = ['telefono', 'rol', 'estado', 'mfa_habilitado', 'area', 'observaciones']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'mfa_habilitado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Administración'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            if not self.instance.pk or self.instance.user.username != username:
                raise ValidationError('Este username ya está en uso')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            if not self.instance.pk or self.instance.user.email != email:
                raise ValidationError('Este email ya está en uso')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar = cleaned_data.get('confirmar_password')

        # Solo validar contraseñas si se está creando un nuevo usuario o si se proporcionó una contraseña
        if password or confirmar:
            if password != confirmar:
                raise ValidationError('Las contraseñas no coinciden')
            
            if len(password) < 12:
                raise ValidationError('La contraseña debe tener al menos 12 caracteres')
            
            # Validar complejidad
            if not re.search(r'[A-Z]', password):
                raise ValidationError('La contraseña debe contener al menos una mayúscula')
            if not re.search(r'[a-z]', password):
                raise ValidationError('La contraseña debe contener al menos una minúscula')
            if not re.search(r'[0-9]', password):
                raise ValidationError('La contraseña debe contener al menos un número')
            if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/]', password):
                raise ValidationError('La contraseña debe contener al menos un carácter especial')

        return cleaned_data


# ===============================================
# FORMULARIO: PRODUCTO - PASO 1
# ===============================================
class ProductoPaso1Form(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'sku', 'ean_upc', 'nombre', 'descripcion', 'categoria',
            'marca', 'modelo', 'uom_compra', 'uom_venta', 'factor_conversion',
            'costo_estandar', 'precio_venta', 'impuesto_iva'
        ]
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SKU-0001'}),
            'ean_upc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '7891234567890'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Marca'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Modelo'}),
            'uom_compra': forms.Select(attrs={'class': 'form-control'}),
            'uom_venta': forms.Select(attrs={'class': 'form-control'}),
            'factor_conversion': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'costo_estandar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'impuesto_iva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def clean_sku(self):
        sku = self.cleaned_data.get('sku').upper()
        if Producto.objects.filter(sku=sku).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este SKU ya existe')
        return sku


# ===============================================
# FORMULARIO: PRODUCTO - PASO 2
# ===============================================
class ProductoPaso2Form(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'stock_minimo', 'stock_maximo', 'punto_reorden',
            'perishable', 'control_por_lote', 'control_por_serie'
        ]
        widgets = {
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_maximo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'punto_reorden': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'perishable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'control_por_lote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'control_por_serie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ===============================================
# FORMULARIO: PRODUCTO - PASO 3
# ===============================================
class ProductoPaso3Form(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['imagen_url', 'ficha_tecnica_url']
        widgets = {
            'imagen_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'ficha_tecnica_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }


# ===============================================
# FORMULARIO: PROVEEDOR - PASO 1
# ===============================================
class ProveedorPaso1Form(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'rut_nif', 'razon_social', 'nombre_fantasia',
            'email', 'telefono', 'sitio_web'
        ]
        widgets = {
            'rut_nif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '76.543.210-5'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razón Social'}),
            'nombre_fantasia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre Fantasía'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contacto@proveedor.cl'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 2 1234 5678'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }

    def clean_rut_nif(self):
        rut = self.cleaned_data.get('rut_nif')
        if Proveedor.objects.filter(rut_nif=rut).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este RUT ya está registrado')
        return rut


# ===============================================
# FORMULARIO: PROVEEDOR - PASO 2
# ===============================================
class ProveedorPaso2Form(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'direccion', 'ciudad', 'region', 'codigo_postal', 'pais',
            'condiciones_pago', 'moneda', 'contacto_principal_nombre',
            'contacto_principal_email', 'contacto_principal_telefono'
        ]
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.Select(attrs={'class': 'form-control'}),
            'condiciones_pago': forms.TextInput(attrs={'class': 'form-control'}),
            'moneda': forms.Select(attrs={'class': 'form-control'}),
            'contacto_principal_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_principal_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contacto_principal_telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ===============================================
# FORMULARIO: PROVEEDOR - PASO 3
# ===============================================
class ProveedorPaso3Form(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['observaciones', 'estado']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }


# ===============================================
# FORMULARIO: MOVIMIENTO - PASO 1
# ===============================================
class MovimientoPaso1Form(forms.ModelForm):
    producto_sku = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SKU-0001'})
    )
    bodega_codigo = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'BOD-CENTRAL'})
    )
    proveedor_rut = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '76.123.456-7'})
    )

    class Meta:
        model = MovimientoInventario
        fields = ['fecha', 'tipo', 'cantidad']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


# ===============================================
# FORMULARIO: MOVIMIENTO - PASO 2
# ===============================================
class MovimientoPaso2Form(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ['lote', 'serie', 'fecha_vencimiento']
        widgets = {
            'lote': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'L-2025-001'}),
            'serie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SN123456789'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


# ===============================================
# FORMULARIO: MOVIMIENTO - PASO 3
# ===============================================
class MovimientoPaso3Form(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ['doc_referencia', 'motivo', 'observaciones']
        widgets = {
            'doc_referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OC-123'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }