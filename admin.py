from django.contrib import admin
from .models import CarbonFootprint, MLModelRun

admin.site.register(CarbonFootprint)
admin.site.register(MLModelRun)