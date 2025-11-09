from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal

from ..models import Producto, Categoria, UnidadMedida, Proveedor


class ProductoPaso1Form(forms.ModelForm):
    """Formulario Paso 1: Identificación y precios"""
    
    class Meta:
        model = Producto
        fields = [
            'sku',
            'ean_upc',
            'nombre',
            'descripcion',
            'categoria',
            'marca',
            'modelo',
            'uom_compra',
            'uom_venta',
            'factor_conversion',
            'costo_estandar',
            'costo_promedio',
            'precio_venta',
            'impuesto_iva',
        ]
        
        labels = {
            'sku': 'SKU/Código',
            'ean_upc': 'EAN/UPC',
            'nombre': 'Nombre del producto',
            'descripcion': 'Descripción',
            'categoria': 'Categoría',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'uom_compra': 'Unidad de compra',
            'uom_venta': 'Unidad de venta',
            'factor_conversion': 'Factor de conversión',
            'costo_estandar': 'Costo estándar',
            'costo_promedio': 'Costo promedio',
            'precio_venta': 'Precio de venta',
            'impuesto_iva': 'IVA (%)',
        }
        
        widgets = {
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: PROD-001',
                'maxlength': '50',
            }),
            'ean_upc': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '7891234567890',
                'maxlength': '13',
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Chocolate Amargo 70%',
                'maxlength': '200',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del producto...',
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control',
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: MarcaX',
                'maxlength': '100',
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: MX-200',
                'maxlength': '100',
            }),
            'uom_compra': forms.Select(attrs={
                'class': 'form-control',
            }),
            'uom_venta': forms.Select(attrs={
                'class': 'form-control',
            }),
            'factor_conversion': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'value': '1',
            }),
            'costo_estandar': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1',
                'min': '0',
                'placeholder': '0',
            }),
            'costo_promedio': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': True,
                'value': '0',
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1',
                'min': '0',
                'placeholder': '0',
            }),
            'impuesto_iva': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1',
                'min': '0',
                'max': '100',
                'value': '19',
            }),
        }
        
        help_texts = {
            'sku': 'Código único del producto',
            'ean_upc': 'Código de barras internacional (opcional)',
            'factor_conversion': 'Unidades de venta por unidad de compra',
            'costo_promedio': 'Se calcula automáticamente',
        }
    
    def clean_sku(self):
        sku = self.cleaned_data.get('sku', '').strip().upper()
        
        if not sku:
            raise ValidationError('El SKU es obligatorio')
        
        if len(sku) < 3:
            raise ValidationError('El SKU debe tener al menos 3 caracteres')
        
        # Verificar unicidad
        if self.instance.pk:
            exists = Producto.objects.filter(sku=sku).exclude(pk=self.instance.pk).exists()
        else:
            exists = Producto.objects.filter(sku=sku).exists()
        
        if exists:
            raise ValidationError(f'Ya existe un producto con el SKU "{sku}"')
        
        return sku
    
    def clean_ean_upc(self):
        ean = self.cleaned_data.get('ean_upc', '').strip()
        
        if ean:
            if not ean.isdigit():
                raise ValidationError('El EAN/UPC debe contener solo números')
            
            if len(ean) not in [8, 13]:
                raise ValidationError('El EAN/UPC debe tener 8 o 13 dígitos')
        
        return ean
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        
        if not nombre:
            raise ValidationError('El nombre es obligatorio')
        
        if len(nombre) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres')
        
        return nombre
    
    def clean_factor_conversion(self):
        factor = self.cleaned_data.get('factor_conversion')
        
        if not factor:
            return Decimal('1')
        
        if factor <= 0:
            raise ValidationError('El factor de conversión debe ser mayor a 0')
        
        if factor > 10000:
            raise ValidationError('El factor de conversión no puede superar 10,000')
        
        return factor
    
    def clean_costo_estandar(self):
        costo = self.cleaned_data.get('costo_estandar')
        
        if costo and costo < 0:
            raise ValidationError('El costo estándar no puede ser negativo')
        
        if costo and costo > 10000000:
            raise ValidationError('El costo estándar no puede superar $10,000,000')
        
        return costo or Decimal('0')
    
    def clean_precio_venta(self):
        precio = self.cleaned_data.get('precio_venta')
        
        if precio and precio < 0:
            raise ValidationError('El precio de venta no puede ser negativo')
        
        if precio and precio > 100000000:
            raise ValidationError('El precio de venta no puede superar $100,000,000')
        
        return precio or Decimal('0')
    
    def clean_impuesto_iva(self):
        iva = self.cleaned_data.get('impuesto_iva')
        
        if iva is None:
            return Decimal('19')
        
        if iva < 0 or iva > 100:
            raise ValidationError('El IVA debe estar entre 0% y 100%')
        
        return iva
    
    def clean(self):
        cleaned_data = super().clean()
        costo = cleaned_data.get('costo_estandar') or Decimal('0')
        precio = cleaned_data.get('precio_venta') or Decimal('0')
        
        # Advertencia si el precio es menor al costo (pero no error)
        if precio > 0 and costo > 0 and precio < costo:
            # No lanzamos error, solo lo notificamos en la vista
            self.add_error(None, 
                f'Advertencia: El precio de venta (${precio:,.0f}) es menor '
                f'al costo estándar (${costo:,.0f}). Esto generará pérdidas.'
            )
        
        return cleaned_data


class ProductoPaso2Form(forms.ModelForm):
    """Formulario Paso 2: Stock y Control"""
    
    class Meta:
        model = Producto
        fields = [
            'stock_actual',      # <-- Agrega este campo
            'stock_minimo',
            'stock_maximo',
            'punto_reorden',
            'es_perecedero',
            'requiere_lote',
            'requiere_serie',
        ]
        labels = {
            'stock_actual': 'Stock actual',   # <-- Etiqueta
            'stock_minimo': 'Stock mínimo',
            'stock_maximo': 'Stock máximo',
            'punto_reorden': 'Punto de reorden',
            'es_perecedero': '¿Es perecedero?',
            'requiere_lote': '¿Requiere control por lote?',
            'requiere_serie': '¿Requiere control por serie?',
        }
        widgets = {
            'stock_actual': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'step': '1',  # <-- Solo enteros
                'value': '0',
            }),
            'stock_minimo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'value': '0',
            }),
            'stock_maximo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional',
                'min': '0',
            }),
            'punto_reorden': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional',
                'min': '0',
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
            'stock_actual': 'Cantidad inicial en inventario',
            'stock_minimo': 'Cantidad mínima requerida en inventario',
            'stock_maximo': 'Cantidad máxima permitida (opcional)',
            'punto_reorden': 'Cuando llegar a este stock, reabastecer (opcional)',
            'es_perecedero': 'Producto con fecha de vencimiento',
            'requiere_lote': 'Rastrear por número de lote',
            'requiere_serie': 'Rastrear por número de serie',
        }
    
    def clean_stock_minimo(self):
        stock_min = self.cleaned_data.get('stock_minimo')
        
        if stock_min is None:
            return Decimal('0')
        
        if stock_min < 0:
            raise ValidationError('El stock mínimo no puede ser negativo')
        
        return stock_min
    
    def clean_stock_maximo(self):
        stock_max = self.cleaned_data.get('stock_maximo')
        
        if stock_max and stock_max < 0:
            raise ValidationError('El stock máximo no puede ser negativo')
        
        return stock_max
    
    def clean_punto_reorden(self):
        punto = self.cleaned_data.get('punto_reorden')
        
        if punto and punto < 0:
            raise ValidationError('El punto de reorden no puede ser negativo')
        
        return punto
    
    def clean(self):
        cleaned_data = super().clean()
        stock_min = cleaned_data.get('stock_minimo') or Decimal('0')
        stock_max = cleaned_data.get('stock_maximo')
        punto_reorden = cleaned_data.get('punto_reorden')
        
        # Validar que stock máximo sea mayor que mínimo
        if stock_max and stock_min >= stock_max:
            raise ValidationError(
                'El stock máximo debe ser mayor que el stock mínimo'
            )
        
        # Si no hay punto de reorden, usar el stock mínimo
        if not punto_reorden:
            cleaned_data['punto_reorden'] = stock_min
        else:
            # Validar que punto de reorden esté entre mínimo y máximo
            if punto_reorden < stock_min:
                raise ValidationError(
                    'El punto de reorden no puede ser menor al stock mínimo'
                )
            
            if stock_max and punto_reorden > stock_max:
                raise ValidationError(
                    'El punto de reorden no puede ser mayor al stock máximo'
                )
        
        return cleaned_data


class ProductoPaso3Form(forms.ModelForm):
    """Formulario Paso 3: Relaciones y derivados"""

    proveedor_principal = forms.ModelChoiceField(
        queryset=Proveedor.objects.filter(estado='ACTIVO').order_by('razon_social'),
        required=False,
        label='Proveedor principal',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Proveedor que abastece este producto'
    )
    
    imagen_url = forms.URLField(
        required=False,
        label='URL de Imagen',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://ejemplo.com/imagen.jpg',
        }),
        help_text='URL completa de la imagen del producto'
    )
    
    ficha_tecnica_url = forms.URLField(
        required=False,
        label='URL de Ficha Técnica',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://ejemplo.com/ficha.pdf',
        }),
        help_text='URL completa de la ficha técnica del producto'
    )
    
    class Meta:
        model = Producto
        fields = []  # Los campos URL son extras
    
    def clean_imagen_url(self):
        url = self.cleaned_data.get('imagen_url', '').strip()
        
        if url:
            # Validar que sea HTTPS preferiblemente
            if not url.startswith(('http://', 'https://')):
                raise ValidationError('La URL debe comenzar con http:// o https://')
            
            # Validar extensiones comunes de imagen
            extensiones_validas = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
            if not any(url.lower().endswith(ext) for ext in extensiones_validas):
                raise ValidationError(
                    'La URL debe apuntar a una imagen válida '
                    f'({", ".join(extensiones_validas)})'
                )
        
        return url
    
    def clean_ficha_tecnica_url(self):
        url = self.cleaned_data.get('ficha_tecnica_url', '').strip()
        
        if url:
            if not url.startswith(('http://', 'https://')):
                raise ValidationError('La URL debe comenzar con http:// o https://')
        
        return url


class ProductoEditForm(forms.ModelForm):
    """Formulario de edición rápida de producto"""
    
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'descripcion',
            'categoria',
            'precio_venta',
            'stock_minimo',
            'stock_maximo',
            'activo',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_maximo': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }