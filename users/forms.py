from django import forms
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm, UsernameField

class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label='Gebruikersnaam',
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    password = forms.CharField(
        label='Wachtwoord',
        widget=forms.PasswordInput(),
    )


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phonenumber', 'dateofbirth', 'image',
                  'verkeersregelaar', 'centralist', 'description']
        widgets = {
            'dateofbirth': forms.DateInput(
                attrs={'class': 'form-control',
                       'placeholder': 'Selecteer een datum',
                       'type': 'date'
                       }
            ),
        }
        labels = {
            "first_name": "Voornaam",
            "last_name": "Achternaam",
            "email": "E-mailadres",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['verkeersregelaar'].initial = True
        self.fields['phonenumber'].initial = "+316"

