from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phonenumber', 'dateofbirth', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'is_staff', 'is_active', 'phonenumber', 'dateofbirth', 'image',
                  'verkeersregelaar', 'centralist', 'description']
        widgets = {
            'dateofbirth': forms.DateInput(
                attrs={'class': 'form-control',
                       'placeholder': 'Selecteer een datum',
                       'type': 'date'
                       }
            ),
        }


