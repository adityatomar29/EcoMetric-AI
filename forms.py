from django import forms
from .models import MLPipelineRun

class MLPipelineForm(forms.ModelForm):
    class Meta:
        model = MLPipelineRun
        fields = ['model_name', 'dataset_name', 'hardware_type', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
