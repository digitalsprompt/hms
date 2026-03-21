from django import forms
from django.contrib.auth import get_user_model

from .models import Profile


User = get_user_model()


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image", "phone_number", "address", "bio"]
        widgets = {
            "address": forms.TextInput(attrs={"class": "w-full rounded-lg border border-gray-300 p-3"}),
            "bio": forms.Textarea(attrs={"rows": 4, "class": "w-full rounded-lg border border-gray-300 p-3"}),
            "phone_number": forms.TextInput(attrs={"class": "w-full rounded-lg border border-gray-300 p-3"}),
        }
