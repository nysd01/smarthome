from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from .models import Room, Device
from .forms import CustomUserCreationForm, RoomUpdateForm

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

# views.py
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
    temperature = 26.5  # Replace with actual sensor value
    fire_alert = False  # Replace with actual condition
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
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': device.status})
    return redirect(request.GET.get('next') or request.META.get('HTTP_REFERER') or 'dashboard')

@login_required
def toggle_all_leds(request):
    leds = Device.objects.filter(device_type__iexact='LED')
    for led in leds:
        led.status = not led.status
        led.save()
    return redirect('dashboard')

@login_required
def open_door(request):
    # Placeholder for sending command to hardware
    messages.success(request, "Door opened!")
    return redirect('dashboard')
