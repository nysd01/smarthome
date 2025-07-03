import paho.mqtt.client as mqtt
import random

MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

def publish_message(topic, message):
    try:
        client_id = f"django-pub-{random.randint(0, 9999)}"
        client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

        client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        client.publish(topic, message)
        client.disconnect()
        print(f"[DEBUG] Publishing to {topic} with message: {message}")
    except Exception as e:
        print(f"[MQTT] Error: {e}")
