# control/models.py
from django.db import models

class DeviceStatus(models.Model):
    device_name = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    updated_at = models.DateTimeField(auto_now=True)
