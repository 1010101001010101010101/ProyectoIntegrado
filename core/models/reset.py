from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
import uuid

class PasswordResetToken(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() - self.created_at <= timezone.timedelta(hours=1)