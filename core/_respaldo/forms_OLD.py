# core/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from ..models import Usuario, Producto, Proveedor, ProductoProveedor, Bodega, MovimientoInventario, Categoria, Venta, DetalleVenta
import re
from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from ..models import Usuario, Producto, Proveedor, ProductoProveedor, Bodega, MovimientoInventario, Categoria, Venta, DetalleVenta

# ===============================================
# FORMULARIO: USUARIO
# ===============================================
class UsuarioForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    nombres = forms.CharField(max_length=150, required=True)
    apellidos = forms.CharField(max_length=150, required=True)
    password = forms.CharField(required=False, widget=forms.PasswordInput)
    confirmar_password = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['telefono', 'rol', 'estado', 'mfa_habilitado', 'area', 'observaciones']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar = cleaned_data.get('confirmar_password')

        if password or confirmar:
            if password != confirmar:
                raise ValidationError("Las contraseñas no coinciden.")
            if len(password) < 12:
                raise ValidationError("La contraseña debe tener al menos 12 caracteres.")
            if not re.search(r'[A-Z]', password):
                raise ValidationError("Debe contener al menos una mayúscula.")
            if not re.search(r'[a-z]', password):
                raise ValidationError("Debe contener al menos una minúscula.")
            if not re.search(r'\d', password):
                raise ValidationError("Debe contener al menos un número.")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError("Debe contener al menos un carácter especial.")
        return cleaned_data


# ===============================================
# FORMULARIO: PRODUCTO - PASO 1
# ===============================================
class ProductoPaso1Form(forms.ModelForm):
    """Paso 1: Información básica del producto + Unidades y Precios"""
    
    costo_promedio = forms.DecimalField(
        required=False,
        disabled=True,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'value': '0',
            'placeholder': 'Calculado automáticamente',
            'title': 'Este campo se calcula automáticamente'
        }),
        label='Costo Promedio'
    )
    
    class Meta:
        model = Producto
        fields = [
            'sku', 'ean_upc', 'nombre', 'descripcion', 'categoria', 'marca', 'modelo',
            'uom_compra', 'uom_venta', 'factor_conversion',
            'costo_estandar', 'costo_promedio', 'precio_venta', 'impuesto_iva'
        ]
        widgets = {
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: PROD-001',
                'maxlength': '50'
            }),
            'ean_upc': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código de barras (opcional)',
                'maxlength': '50'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre descriptivo del producto',
                'maxlength': '200'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada (opcional)'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Samsung, Apple (opcional)',
                'maxlength': '100'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Galaxy S23 (opcional)',
                'maxlength': '100'
            }),
            'uom_compra': forms.Select(attrs={
                'class': 'form-control'
            }),
            'uom_venta': forms.Select(attrs={
                'class': 'form-control'
            }),
            'factor_conversion': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'value': '1.00',
                'placeholder': '1.00'
            }),
            'costo_estandar': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1',
                'min': '0',
                'value': '0',
                'placeholder': '1000'
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1',
                'min': '0',
                'value': '0',
                'placeholder': '1500'
            }),
            'impuesto_iva': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'value': '19.00',
                'placeholder': '19.00'
            }),
        }
        labels = {
            'sku': 'SKU',
            'ean_upc': 'EAN/UPC',
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'categoria': 'Categoría',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'uom_compra': 'Unidad de Compra',
            'uom_venta': 'Unidad de Venta',
            'factor_conversion': 'Factor de Conversión',
            'costo_estandar': 'Costo Estándar',
            'precio_venta': 'Precio de Venta',
            'impuesto_iva': 'IVA (%)',
        }
    
    def clean_sku(self):
        """Validar SKU único y formato"""
        sku = self.cleaned_data.get('sku')
        
        if not sku:
            raise forms.ValidationError('El SKU es obligatorio')
        
        sku = sku.strip().upper()
        
        if len(sku) < 3:
            raise forms.ValidationError('El SKU debe tener al menos 3 caracteres')
        
        # Verificar si ya existe
        if Producto.objects.filter(sku=sku).exists():
            raise forms.ValidationError(f'El SKU "{sku}" ya existe en el sistema')
        
        return sku
    
    def clean_nombre(self):
        """Validar nombre"""
        nombre = self.cleaned_data.get('nombre')
        
        if not nombre:
            raise forms.ValidationError('El nombre es obligatorio')
        
        nombre = nombre.strip()
        
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres')
        
        return nombre
    
    def clean_factor_conversion(self):
        """Validar factor de conversión"""
        factor = self.cleaned_data.get('factor_conversion')
        
        if factor is None:
            raise forms.ValidationError('El factor de conversión es obligatorio')
        
        if factor <= 0:
            raise forms.ValidationError('El factor de conversión debe ser mayor a 0')
        
        if factor > 10000:
            raise forms.ValidationError('El factor de conversión no puede superar 10,000')
        
        return factor
    
    def clean_costo_estandar(self):
        """Validar costo estándar - SOLO ENTEROS"""
        costo = self.cleaned_data.get('costo_estandar')
        
        if costo is None:
            return Decimal('0')
        
        # Verificar que sea entero
        if costo != int(costo):
            raise forms.ValidationError('El costo estándar debe ser un número entero (sin decimales)')
        
        if costo < 0:
            raise forms.ValidationError('El costo estándar no puede ser negativo')
        
        if costo > 10000000:
            raise forms.ValidationError('El costo estándar no puede superar $10,000,000')
        
        return int(costo)
    
    # ⚠️ ELIMINADO: clean_costo_promedio() - Ya no es necesario validarlo porque es readonly
    
    def clean_precio_venta(self):
        """Validar precio de venta - SOLO ENTEROS"""
        precio = self.cleaned_data.get('precio_venta')
        
        if precio is None:
            return Decimal('0')
        
        # Verificar que sea entero
        if precio != int(precio):
            raise forms.ValidationError('El precio de venta debe ser un número entero (sin decimales)')
        
        if precio < 0:
            raise forms.ValidationError('El precio de venta no puede ser negativo')
        
        if precio > 100000000:
            raise forms.ValidationError('El precio de venta no puede superar $100,000,000')
        
        return int(precio)
    
    def clean_impuesto_iva(self):
        """Validar IVA"""
        iva = self.cleaned_data.get('impuesto_iva')
        
        if iva is None:
            raise forms.ValidationError('El IVA es obligatorio')
        
        if iva < 0:
            raise forms.ValidationError('El IVA no puede ser negativo')
        
        if iva > 100:
            raise forms.ValidationError('El IVA no puede superar 100%')
        
        return iva
    
    def clean(self):
        """Validaciones cruzadas"""
        cleaned_data = super().clean()
        costo_estandar = cleaned_data.get('costo_estandar')
        precio_venta = cleaned_data.get('precio_venta')
        
        # ⚠️ ELIMINADO: Validaciones con costo_promedio
        
        # Validar que precio de venta sea mayor al costo
        if costo_estandar and precio_venta:
            if precio_venta < costo_estandar:
                self.add_error('precio_venta', 
                    f'El precio de venta (${precio_venta:,}) es menor al costo estándar (${costo_estandar:,}). '
                    'Esto puede generar pérdidas.'
                )
            
            # Calcular margen
            margen = ((precio_venta - costo_estandar) / costo_estandar * 100) if costo_estandar > 0 else 0
            
            # Advertencia si el margen es muy bajo
            if margen < 10 and margen >= 0:
                self.add_error('precio_venta', 
                    f'El margen de ganancia es muy bajo ({margen:.1f}%). Se recomienda al menos 10%.'
                )
        
        return cleaned_data


# ===============================================
# FORMULARIO: PRODUCTO - PASO 2 (ÚNICA VERSIÓN)
# ===============================================
class ProductoPaso2Form(forms.ModelForm):
    """Formulario Paso 2: Stock y Control (según PDF)"""
    
    class Meta:
        model = Producto
        fields = [
            'stock_minimo',
            'stock_maximo',
            'punto_reorden',
            'es_perecedero',      # perishable en el PDF
            'requiere_lote',      # control_por_lote
            'requiere_serie',     # control_por_serie
        ]
        
        labels = {
            'stock_minimo': 'stock_minimo',
            'stock_maximo': 'stock_maximo',
            'punto_reorden': 'punto_reorden',
            'es_perecedero': 'perishable',
            'requiere_lote': 'control_por_lote',
            'requiere_serie': 'control_por_serie',
        }
        
        widgets = {
            'stock_minimo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'value': '0',
                'required': True,
            }),
            'stock_maximo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '',
            }),
            'punto_reorden': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '—',
            }),
            'es_perecedero': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'requiere_lote': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'requiere_serie': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        
        help_texts = {
            'stock_minimo': '(requerido; default 0)',
            'stock_maximo': '(opcional)',
            'punto_reorden': '(opcional; si no, usar mínimo)',
            'es_perecedero': '(requerido; default 0)',
            'requiere_lote': '(requerido; default 0)',
            'requiere_serie': '(requerido; default 0)',
        }
    
    def clean_stock_minimo(self):
        stock_min = self.cleaned_data.get('stock_minimo')
        if stock_min is None:
            return Decimal('0')
        return stock_min
    
    def clean(self):
        cleaned_data = super().clean()
        stock_min = cleaned_data.get('stock_minimo') or Decimal('0')
        stock_max = cleaned_data.get('stock_maximo')
        punto_reorden = cleaned_data.get('punto_reorden')
        
        # Validar que stock_minimo < stock_maximo (si existe)
        if stock_max and stock_min >= stock_max:
            raise ValidationError('El stock máximo debe ser mayor que el stock mínimo')
        
        # Si no hay punto_reorden, usar stock_minimo
        if not punto_reorden:
            cleaned_data['punto_reorden'] = stock_min
        
        return cleaned_data


# ===============================================
# FORMULARIO: PRODUCTO - PASO 3
# ===============================================
class ProductoPaso3Form(forms.ModelForm):
    """Paso 3: Archivos y URLs opcionales"""
    
    class Meta:
        model = Producto
        fields = ['imagen_url', 'ficha_tecnica_url']
        widgets = {
            'imagen_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://ejemplo.com/imagen.jpg (opcional)'
            }),
            'ficha_tecnica_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://ejemplo.com/ficha.pdf (opcional)'
            }),
        }
        labels = {
            'imagen_url': 'URL de Imagen del Producto',
            'ficha_tecnica_url': 'URL de Ficha Técnica',
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


# ===============================================
# FORMULARIOS DE VENTAS
# ===============================================
class VentaForm(forms.ModelForm):
    """Formulario para crear/editar ventas"""
    
    class Meta:
        model = Venta
        fields = [
            'tipo_comprobante', 'cliente_nombre', 'cliente_rut',
            'cliente_email', 'cliente_telefono', 'metodo_pago',
            'descuento', 'observaciones'
        ]
        widgets = {
            'tipo_comprobante': forms.Select(attrs={'class': 'form-control'}),
            'cliente_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'cliente_rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678-9'}),
            'cliente_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'cliente_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56912345678'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': '0'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones opcionales'}),
        }


class DetalleVentaForm(forms.ModelForm):
    """Formulario para agregar productos a la venta"""
    
    producto_sku = forms.CharField(
        max_length=50,
        label='SKU del Producto',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el SKU del producto',
            'autofocus': True
        })
    )
    
    class Meta:
        model = DetalleVenta
        fields = ['cantidad', 'descuento_porcentaje']
        labels = {
            'cantidad': 'Cantidad',
            'descuento_porcentaje': 'Descuento (%)'
        }
        widgets = {
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'value': '1'
            }),
            'descuento_porcentaje': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'value': '0'
            }),
        }
    
    def clean_producto_sku(self):
        sku = self.cleaned_data['producto_sku']
        try:
            Producto.objects.get(sku=sku, activo=True)
        except Producto.DoesNotExist:
            raise forms.ValidationError(f'No existe un producto activo con SKU: {sku}')
        return sku