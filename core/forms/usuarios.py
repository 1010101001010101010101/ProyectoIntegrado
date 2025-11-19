from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from ..models import Usuario

User = get_user_model()


class UsuarioForm(forms.ModelForm):
    """
    Formulario para crear nuevo usuario
    Coincide exactamente con los campos del modelo Usuario
    """
    # ===== IDENTIFICACIÓN (de User) =====
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'j.cortes',
            'autofocus': True,
        }),
        label='Username',
        help_text='Debe ser único en el sistema (sin espacios)'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'usuario@dominio.com',
        }),
        label='Email',
        help_text='Se usará para notificaciones'
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Jorge',
        }),
        label='Nombres'
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cortés',
        }),
        label='Apellidos'
    )
    
    # ===== PERFIL USUARIO =====
    # Acceso
    ROL_CHOICES = [('', 'Selecciona un rol')] + Usuario.ROL_CHOICES
    rol = forms.ChoiceField(choices=ROL_CHOICES, required=True)
    ESTADO_CHOICES = [
        ('', 'Seleccionar estado'),
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]
    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Estado'
    )
    
    telefono = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56 9 1234 5678',
        }),
        label='Teléfono (opcional)'
    )
    
    direccion = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Calle Principal #123',
        }),
        label='Dirección (opcional)'
    )
    
    # ===== CONTRASEÑA =====
    password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
        }),
        label='Contraseña',
        help_text='Mínimo 8 caracteres'
    )
    
    password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
        }),
        label='Confirmar Contraseña'
    )
    
    def clean_username(self):
        """Validar username único y sin espacios"""
        username = self.cleaned_data.get('username', '').strip()
        
        if ' ' in username:
            raise ValidationError('El username no puede contener espacios')
        
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError(f'El username "{username}" ya está registrado')
        
        return username
    
    def clean_email(self):
        """Validar email único"""
        email = self.cleaned_data.get('email', '').strip().lower()
        
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(f'El email "{email}" ya está registrado')
        
        return email
    
    def clean(self):
        """Validar que las contraseñas coincidan"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError({
                    'password_confirm': 'Las contraseñas no coinciden'
                })
        
        return cleaned_data

    def clean_rol(self):
        value = self.cleaned_data.get('rol', '').strip()
        if not value:
            raise forms.ValidationError('Debes seleccionar un rol.')
        return value

    def clean_estado(self):
        value = self.cleaned_data.get('estado', '').strip()
        if not value:
            raise forms.ValidationError('Debes seleccionar un estado.')
        return value

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = self.cleaned_data['estado'] == 'ACTIVO'
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            perfil, created = Usuario.objects.get_or_create(user=user)
            perfil.rol = self.cleaned_data['rol']
            perfil.estado = self.cleaned_data['estado']
            perfil.telefono = self.cleaned_data.get('telefono', '')
            perfil.direccion = self.cleaned_data.get('direccion', '')
            perfil.save()
        return user

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'j.cortes', 'autofocus': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@dominio.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Jorge'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cortés'}),
        }


class UsuarioEditForm(forms.ModelForm):
    telefono = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56 9 1234 5678',
        }),
        label='Teléfono'
    )

    direccion = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Calle Principal #123',
        }),
        label='Dirección'
    )

    rol = forms.ChoiceField(
        choices=Usuario.ROL_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Rol'
    )

    estado = forms.ChoiceField(
        choices=Usuario.ESTADO_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Estado'
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'email': 'Email',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
        }
    
    def clean_email(self):
        """Validar email único (excluyendo usuario actual)"""
        email = self.cleaned_data.get('email', '').lower()
        
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(f'El email "{email}" ya está en uso')
        
        return email
