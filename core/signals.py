from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models.usuarios import Usuario

@receiver(post_save, sender=User)
def set_must_change_password_on_create(sender, instance, created, **kwargs):
    if created:
        Usuario.objects.update_or_create(
            user=instance,
            defaults={'must_change_password': True}
        )
