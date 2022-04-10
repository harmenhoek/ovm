from django import forms
from .models import Planning, Day
# from django.forms.models import inlineformset_factory
# from bootstrap_datepicker_plus import DatePickerInput

class ModifyPlanningDashboard(forms.ModelForm):
    class Meta:
        model = Planning
        fields = ['user', 'post', 'customstart', 'customend', 'shift']

class AddDay(forms.ModelForm):
    class Meta:
        model = Day
        fields = '__all__'