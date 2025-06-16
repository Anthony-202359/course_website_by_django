from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class PaymentForm(forms.Form):
    plan = forms.ChoiceField(choices=[
        ("free", "Free"),
        ("intermediate", "Intermediate ($50)"),
        ("pro", "Pro ($75)")
    ], widget=forms.RadioSelect)

class SubscriptionForm(forms.Form):
    plan = forms.ChoiceField(choices=[
        ("free", "Free"),
        ("intermediate", "Intermediate ($50)"),
        ("pro", "Pro ($75)")
    ], widget=forms.RadioSelect) 