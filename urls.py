# from django.contrib import admin 
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), # Landing page
    path('auth/', views.auth, name='auth'), # Combined login/signup
    path('logout/', views.logout, name='logout'), # logout
    path('home/', views.home, name='home'), # Home page (after login)
    path('calculate/', views.carbon_calculator, name='carbon_calculator'),
    path('dashboard/', views.carbon_dashboard, name='carbon_dashboard'),
    path('api/dashboard-data/', views.carbon_data_api, name='carbon_data_api'),
    path("simulate_ml_run/", views.ml_tracker_view, name="ml_tracker"),
    path("api/add_ml_model/", views.add_ml_model, name="add_ml_model"),
]