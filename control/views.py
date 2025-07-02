from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login  # ✅ Added
from django.contrib import messages
from .forms import CustomUserCreationForm

@login_required
def dashboard(request):
    """
    Dashboard view showing temperature and control actions.
    """
    temperature = 26.5  # Replace with actual sensor value from Arduino
    return render(request, 'control/dashboard.html', {'temperature': temperature})

@login_required
def toggle_light(request):
    """
    View to handle light toggle request to Arduino.
    """
    # TODO: Send command to Arduino (e.g., HTTP request or MQTT publish)
    messages.success(request, "Light toggled!")
    return redirect('dashboard')

@login_required
def open_door(request):
    """
    View to handle door opening request to Arduino.
    """
    # TODO: Send command to Arduino
    messages.success(request, "Door opened!")
    return redirect('dashboard')

def register(request):
    """
    User registration view.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto login
            messages.success(request, "Registration successful. Welcome!")
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})
