from django import forms
from django.forms import formset_factory
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Workout, Exercise, Set, UserProfile, ProgressPicture, Goal, Meal, Food


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
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Exercise name'
            })
        }


class SetForm(forms.ModelForm):
    class Meta:
        model = Set
        fields = ['set_number', 'reps', 'weight', 'weight_unit']
        widgets = {
            'set_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
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

# Create a formset for sets
SetFormSet = formset_factory(SetForm, extra=1, can_delete=True)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['age', 'current_weight', 'body_fat_percentage', 'weight_unit']
        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '13',
                'max': '120',
                'placeholder': 'Enter your age'
            }),
            'current_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Enter your current weight'
            }),
            'body_fat_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.1',
                'placeholder': 'Enter body fat % (optional)'
            }),
            'weight_unit': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'current_weight': 'Current Weight',
            'body_fat_percentage': 'Body Fat Percentage (%)',
            'weight_unit': 'Weight Unit'
        }


class ProgressPictureForm(forms.ModelForm):
    class Meta:
        model = ProgressPicture
        fields = ['title', 'image', 'date_taken', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a title for this progress picture'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'date_taken': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about this progress picture'
            })
        }
        labels = {
            'date_taken': 'Date Taken',
            'notes': 'Notes (Optional)'
        }


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['title', 'description', 'goal_type', 'target_value', 'unit', 'target_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your goal (e.g., "Lose 10kgs", "Bench 100kg")'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your goal in more detail (optional)'
            }),
            'goal_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'target_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Target value (optional)'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-control'
            }),
            'target_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }
        labels = {
            'title': 'Goal Title',
            'description': 'Description (Optional)',
            'goal_type': 'Goal Type',
            'target_value': 'Target Value (Optional)',
            'unit': 'Unit',
            'target_date': 'Target Date (Optional)'
        }


class MealForm(forms.ModelForm):
    date_consumed = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Date Consumed',
        required=False
    )
    
    class Meta:
        model = Meal
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meal name (e.g., "Breakfast", "Post-workout snack")'
            })
        }
        labels = {
            'name': 'Meal Name'
        }
    
    def save(self, commit=True):
        meal = super().save(commit=False)
        if self.cleaned_data.get('date_consumed'):
            meal.date_consumed = self.cleaned_data['date_consumed']
        if commit:
            meal.save()
        return meal


class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['name', 'grams', 'calories_per_100g', 'carbs_per_100g', 'fat_per_100g', 'protein_per_100g']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter food name (e.g., "Chicken breast", "Brown rice")'
            }),
            'grams': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.1',
                'placeholder': 'Weight in grams'
            }),
            'calories_per_100g': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Calories per 100g'
            }),
            'carbs_per_100g': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Carbs per 100g'
            }),
            'fat_per_100g': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Fat per 100g'
            }),
            'protein_per_100g': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Protein per 100g'
            })
        }
        labels = {
            'name': 'Food Name',
            'grams': 'Weight (grams)',
            'calories_per_100g': 'Calories per 100g',
            'carbs_per_100g': 'Carbs per 100g',
            'fat_per_100g': 'Fat per 100g',
            'protein_per_100g': 'Protein per 100g'
        }


# Create a formset for foods in a meal
FoodFormSet = formset_factory(FoodForm, extra=1, can_delete=True)