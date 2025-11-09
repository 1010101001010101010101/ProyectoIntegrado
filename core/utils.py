import re
from django.core.exceptions import ValidationError

PASSWORD_POLICY_MESSAGE = (
    'La contraseña debe tener al menos 8 caracteres e incluir letras y números.'
)

def validate_password_policy(password: str):
    if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
        raise ValidationError(PASSWORD_POLICY_MESSAGE)