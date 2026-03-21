from django import forms

class AvailabilityForm(forms.Form):
    check_in = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'room-reserve-input',
                'placeholder': 'Select check-in',
            }
        ),
    )
    check_out = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'room-reserve-input',
                'placeholder': 'Select check-out',
            }
        ),
    )
