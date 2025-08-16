from django import forms
from django.forms import formset_factory
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Workout, Exercise


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['title', 'day', 'duration']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter workout title'
            }),
            'day': forms.Select(attrs={
                'class': 'form-control'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'HH:MM:SS (e.g., 01:30:00)'
            })
        }


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'sets', 'reps', 'weight', 'weight_unit']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Exercise name'
            }),
            'sets': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'reps': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'weight_unit': forms.Select(attrs={
                'class': 'form-control'
            })
        }


# Create a formset for exercises
ExerciseFormSet = formset_factory(ExerciseForm, extra=1, can_delete=True)