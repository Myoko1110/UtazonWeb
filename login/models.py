from django.db import models
from django.utils import timezone


class Session(models.Model):
    user_id = models.CharField(max_length=100)
    logged_date = models.DateTimeField(default=timezone.now)
    expires = models.DateTimeField(default=timezone.now)
    session_id = models.CharField(max_length=100)
    session_value = models.CharField(max_length=100)
