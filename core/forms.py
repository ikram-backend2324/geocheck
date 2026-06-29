from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Zone


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "field-input", "autocomplete": "off"})
        self.fields["username"].widget.attrs.update({"placeholder": "Choose a username"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Create a password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Repeat the password"})


class LoginStyledForm(forms.Form):
    """Just used to share the same CSS classes; actual auth handled by Django's AuthenticationForm."""
    pass


class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ["name", "description", "center_lat", "center_lng", "radius_m", "color", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "field-input", "placeholder": "e.g. Main Campus"}),
            "description": forms.TextInput(attrs={"class": "field-input", "placeholder": "Optional note"}),
            "center_lat": forms.NumberInput(attrs={"class": "field-input", "step": "any", "placeholder": "e.g. 42.453100"}),
            "center_lng": forms.NumberInput(attrs={"class": "field-input", "step": "any", "placeholder": "e.g. 59.610300"}),
            "radius_m": forms.NumberInput(attrs={"class": "field-input", "min": 20, "max": 20000}),
            "color": forms.TextInput(attrs={"class": "field-input color-input", "type": "color"}),
            "is_active": forms.CheckboxInput(attrs={"class": "field-checkbox"}),
        }