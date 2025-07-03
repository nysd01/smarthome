import os
import sys
import django
import time
import paho.mqtt.client as mqtt

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smarthome.settings")
django.setup()

from django.utils import timezone
from control.models import Device, Temperature  # ✅ Move here after setup()

# MQTT Config
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] ✅ Connected successfully")
        client.subscribe("nysd/derek/led/+/status")
        client.subscribe("nysd/derek/temperature")
    else:
        print(f"[MQTT] ❌ Connection failed with code {rc}")


def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode()
        print(f"[MQTT] 📩 {topic} = {payload}")

        parts = topic.split("/")

        # 🔌 LED Status
        if len(parts) == 5 and parts[2] == "led" and parts[4] == "status":
            device_id = int(parts[3])
            try:
                device = Device.objects.get(id=device_id)
                device.status = payload.lower() == "on"
                device.save()
                print(f"[DB] ✅ Updated device {device_id} to {'ON' if device.status else 'OFF'}")
            except Device.DoesNotExist:
                print(f"[ERROR] Device ID {device_id} not found.")

        # 🌡️ Temperature
        elif topic == "nysd/derek/temperature":
            try:
                temp_value = float(payload)
                Temperature.objects.create(value=temp_value, timestamp=timezone.now())
                print("[DB] ✅ Temperature saved:", temp_value)
            except ValueError:
                print(f"[ERROR] Invalid temperature value: {payload}")

        else:
            print(f"[MQTT] ⚠️ Unhandled topic: {topic}")

    except Exception as e:
        print(f"[ERROR] ❌ Failed to process message: {e}")


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print(f"[MQTT] Connecting to {MQTT_BROKER}:{MQTT_PORT}")
        client.connect(MQTT_BROKER, MQTT_PORT, 100)
        client.loop_forever()
    except Exception as e:
        print(f"[MQTT] ❌ Connection error: {e}")
        time.sleep(5)

if __name__ == "__main__":
    main()
