from django.db import models
from django.utils import timezone
from django.db.models import Sum, Avg

class CarbonFootprint(models.Model):
    date = models.DateField(default=timezone.now)
    car_distance = models.FloatField(default=0)
    flight_hours = models.FloatField(default=0)
    public_trips = models.FloatField(default=0)
    electricity = models.FloatField(default=0)
    gas = models.FloatField(default=0)
    meat_meals = models.FloatField(default=0)
    local_food = models.FloatField(default=0)
    waste_kg = models.FloatField(default=0)
    recycling = models.FloatField(default=0)
    water_liters = models.FloatField(default=0)
    showers = models.FloatField(default=0)
    online_orders = models.FloatField(default=0)
    clothing = models.FloatField(default=0)
    total_footprint = models.FloatField(default=0)

    def __str__(self):
        return f"{self.date} - {self.total_footprint:.2f} kg CO₂"
    
    @classmethod
    def get_dashboard_data(cls):
        qs = cls.objects.all().order_by('date')
        monthly = list(qs.values('date', 'total_footprint'))
        avg_total = qs.aggregate(total=Avg('total_footprint'))['total']
        latest = qs.last()
        return {
            'monthly': monthly,
            'avg_total': round(avg_total or 0, 2),
            'latest_total': round(latest.total_footprint if latest else 0, 2)
        }
    
class MLModelRun(models.Model):
    HARDWARE_CHOICES = [
        ('cpu', 'CPU'),
        ('gpu', 'GPU'),
        ('tpu', 'TPU'),
    ]

    model_name = models.CharField(max_length=100)
    training_time = models.FloatField(help_text="Training time in hours")
    hardware = models.CharField(max_length=10, choices=HARDWARE_CHOICES)
    energy_consumed = models.FloatField(help_text="Energy consumption in kWh")
    emission = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Simple emission estimation formula (kg CO₂)
        # Based on an average emission factor per kWh:
        # CPU: 0.4, GPU: 0.7, TPU: 0.6 kg CO₂/kWh
        factors = {'cpu': 0.4, 'gpu': 0.7, 'tpu': 0.6}
        self.emission = self.energy_consumed * factors.get(self.hardware, 0.5)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.model_name} ({self.emission:.4f} kg CO₂)"