"""
WSGI config for smarthome project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarthome.settings')

application = get_wsgi_application()

# ✅ Start MQTT listener here
import threading
def start_mqtt():
    import control.mqtt_client
threading.Thread(target=start_mqtt, daemon=True).start()