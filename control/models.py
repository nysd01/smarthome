# control/models.py
from django.db import models
from django.utils import timezone

class DeviceStatus(models.Model):
    device_name = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    updated_at = models.DateTimeField(auto_now=True)
class Room(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Device(models.Model):
    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=50)  # e.g., Light, Fan, Sensor
    status = models.BooleanField(default=False)
    room = models.ForeignKey(Room, related_name='devices', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.room.name})"
    


class Temperature(models.Model):
    value = models.FloatField()            # temperature value
    timestamp = models.DateTimeField(default=timezone.now)  # when it was recorded

    def __str__(self):
            return f"{self.value} °C at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"