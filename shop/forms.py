from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Order


# ================= REGISTER =================
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# ================= UPDATE USER =================
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


# ================= UPDATE PROFILE =================
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'phone', 'gender', 'birthday']
        widgets = {
            'birthday': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            })
        }


# ================= CHECKOUT =================
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'address', 'phone', 'payment_method']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-white border-0'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-white border-0',
                'rows': 3
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-white border-0'
            }),
            'payment_method': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            })
        }