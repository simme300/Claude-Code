from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Create your models here.

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workouts")
    title = models.CharField(max_length=100)
    
    
    duration = models.DurationField(null=True, blank=True)
    
    PUSH = "Push"
    PULL = "Pull"
    LEGS = "Legs"
    
    DAY_CHOICES = [
        (PUSH, "Push"),
        (PULL, "Pull"),
        (LEGS, "Legs"),
        
    ]
    day = models.CharField(max_length=5, choices=DAY_CHOICES, null=True, blank=True)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.title



class Exercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="exercises")
    name = models.CharField(max_length=50)
    sets = models.IntegerField(default=0, validators=[MinValueValidator(0)]) 
    reps = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    LBS = "Lbs"
    KG = "Kg"
    
    WEIGHT_OPTIONS = [
        (LBS, "Lbs"),
        (KG, "Kg"),
    ]
    
    weight = models.DecimalField(max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    weight_unit = models.CharField(max_length=3, choices=WEIGHT_OPTIONS, default=LBS)
    
    def __str__(self):
        return self.name

class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meals")
    name = models.CharField(max_length=30)
    calories = models.IntegerField(validators=[MinValueValidator(0)])
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.name


class Food(models.Model):
    name = models.CharField(max_length=30)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="foods")
    grams = models.IntegerField(validators=[MinValueValidator(0)])
    
    def __str__(self):
        return self.name