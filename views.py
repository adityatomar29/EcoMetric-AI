from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import CarbonFootprint, MLModelRun
# from .forms import MLPipelineForm
from django.http import JsonResponse
from django.db.models import Avg, Sum
from django.utils import timezone
from datetime import timedelta
# from codecarbon import EmissionsTracker
import random, time
import json
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    return render(request, 'landing.html')

def auth(request):
    """
    Handles both login and signup from a single template (login.html)
    """
    if request.method == 'POST':
        action = request.POST.get('action')  # identifies which button was clicked

        username = request.POST.get('username')
        password = request.POST.get('password')

        # ---------- SIGNUP ----------
        if action == 'signup':
            email = request.POST.get('email')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists. Please choose another.")
                return redirect('auth')

            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('auth')

        # ---------- LOGIN ----------
        elif action == 'login':
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home')
            else:
                if not User.objects.filter(username=username).exists():
                    messages.error(request, "User not registered. Please sign up first.")
                else:
                    messages.error(request, "Invalid credentials. Try again.")
                return redirect('auth')

    return render(request, 'login.html')


@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')

def logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('')


def carbon_calculator(request):
    total = None
    if request.method == 'POST':
        data = request.POST

        # Get all values safely
        def get_val(name):
            try:
                return float(data.get(name, 0))
            except ValueError:
                return 0

        # Basic footprint calculation (example formula)
        car_emission = get_val('car_distance') * 0.2
        flight_emission = get_val('flight_hours') * 90
        public_emission = get_val('public_trips') * 1.5
        energy_emission = get_val('electricity') * 0.5 + get_val('gas') * 2.3
        food_emission = get_val('meat_meals') * 7 - get_val('local_food') * 0.05
        waste_emission = get_val('waste_kg') * 1.2 - get_val('recycling') * 0.1
        water_emission = get_val('water_liters') * 0.002 + get_val('showers') * 0.5
        shopping_emission = get_val('online_orders') * 4 + get_val('clothing') * 5

        total = round(sum([car_emission, flight_emission, public_emission, energy_emission,
                           food_emission, waste_emission, water_emission, shopping_emission]), 2)

        # Save daily record to DB
        CarbonFootprint.objects.create(
            car_distance=get_val('car_distance'),
            flight_hours=get_val('flight_hours'),
            public_trips=get_val('public_trips'),
            electricity=get_val('electricity'),
            gas=get_val('gas'),
            meat_meals=get_val('meat_meals'),
            local_food=get_val('local_food'),
            waste_kg=get_val('waste_kg'),
            recycling=get_val('recycling'),
            water_liters=get_val('water_liters'),
            showers=get_val('showers'),
            online_orders=get_val('online_orders'),
            clothing=get_val('clothing'),
            total_footprint=total
        )

    return render(request, 'calculate.html', {'total_footprint': total})



def carbon_dashboard(request):
    return render(request, 'dashboard.html')

def carbon_data_api(request):
    """API endpoint for live dashboard data"""
    data = CarbonFootprint.get_dashboard_data()
    return JsonResponse(data)


def ml_tracker_view(request):
    return render(request, "MLCalculator.html")

@csrf_exempt
def add_ml_model(request):
    if request.method == "POST":
        data = json.loads(request.body)
        model = MLModelRun.objects.create(
            model_name=data.get("model_name"),
            training_time=data.get("training_time"),
            hardware=data.get("hardware"),
            energy_consumed=data.get("energy")
        )

        models = MLModelRun.objects.order_by("-created_at")
        total = sum(m.emission for m in models)
        average = total / models.count() if models.exists() else 0

        return JsonResponse({
            "total": total,
            "average": average,
            "models": [
                {
                    "name": m.model_name,
                    "emission": m.emission,
                    "date": m.created_at.strftime("%b %d, %Y %H:%M")
                } for m in models
            ]
        })
    return JsonResponse({"error": "Invalid request"}, status=400)