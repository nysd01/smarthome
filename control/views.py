from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from .models import Room, Device, Temperature  # ✅ Added Temperature
from .forms import CustomUserCreationForm, RoomUpdateForm
from .mqtt_client import publish_message

from django.views.decorators.csrf import csrf_exempt
from .mqtt_client import publish_message
# 🔒 Authentication views

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Registration failed. Please fix the errors.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# 🏠 Dashboard and Room Views

@login_required
def dashboard(request):
    rooms = Room.objects.prefetch_related('devices').all()

    # ✅ Get the latest temperature from the database
    latest_temp = Temperature.objects.last()
    temperature = latest_temp.value if latest_temp else 0.0

    fire_alert = temperature > 30  # fire condition threshold

    return render(request, 'control/dashboard.html', {
        'rooms': rooms,
        'temperature': temperature,
        'fire_alert': fire_alert,
    })


@login_required
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'control/room_detail.html', {'room': room})


@login_required
def add_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Room.objects.create(name=name)
            messages.success(request, "Room added.")
        return redirect('dashboard')
    return render(request, 'control/add_room.html')


@login_required
def update_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomUpdateForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Room updated.")
            return redirect('dashboard')
    else:
        form = RoomUpdateForm(instance=room)
    return render(request, 'control/update_room.html', {'form': form, 'room': room})


# 💡 Device Views

@login_required
def add_device(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        device_type = request.POST.get('type')
        if name and device_type:
            Device.objects.create(name=name, device_type=device_type, room=room)
            messages.success(request, "Device added.")
        return redirect('dashboard')
    return render(request, 'control/add_device.html', {'room': room})


@login_required
def delete_device(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    device.delete()
    messages.success(request, "Device deleted.")
    return redirect('dashboard')


@login_required
def toggle_device(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    device.status = not device.status
    device.save()

    payload = "on" if device.status else "off"
    topic = f"nysd/derek/led/{device.id}/control"  # ✅ Matches MQTT topic

    publish_message(topic, payload)  # Send MQTT message

    return redirect('room_detail', room_id=device.room.id)


@login_required
def toggle_all_leds(request):
    leds = Device.objects.filter(device_type__iexact='LED')

    # Determine ON/OFF based on current LED status
    turn_on = not all(led.status for led in leds)

    for led in leds:
        led.status = turn_on
        led.save()

        payload = "on" if turn_on else "off"
        topic = f"nysd/home123/led/{led.id}/control"
        publish_message(topic, payload)

    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def open_door(request):
    # Placeholder for sending command to hardware
    messages.success(request, "Door opened!")
    return redirect('dashboard')



@login_required
def set_led_brightness(request, device_id):
    if request.method == "POST":
        brightness = int(request.POST.get("brightness", 128))
        device = get_object_or_404(Device, id=device_id)
        device.brightness = brightness
        device.save()

        topic = f"nysd/derek/led/{device.id}/brightness"
        publish_message(topic, str(brightness))
    return redirect("dashboard")
