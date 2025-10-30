from django.contrib import admin
from .models import PasswordResetToken

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'used', 'created_at', 'expires_at')
    list_filter = ('used',)
    search_fields = ('user__username', 'user__email', 'token')
