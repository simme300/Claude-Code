from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    age = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(13), MaxValueValidator(120)])
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    body_fat_percentage = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    LBS = "Lbs"
    KG = "Kg"
    
    WEIGHT_UNIT_CHOICES = [
        (LBS, "Lbs"),
        (KG, "Kg"),
    ]
    
    weight_unit = models.CharField(max_length=3, choices=WEIGHT_UNIT_CHOICES, default=LBS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workouts")
    title = models.CharField(max_length=100)
    workout_number = models.PositiveIntegerField(default=1)
    
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
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title



class Exercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="exercises")
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name


class Set(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="sets")
    set_number = models.PositiveIntegerField()
    reps = models.IntegerField(validators=[MinValueValidator(0)])
    
    LBS = "Lbs"
    KG = "Kg"
    
    WEIGHT_OPTIONS = [
        (LBS, "Lbs"),
        (KG, "Kg"),
    ]
    
    weight = models.DecimalField(max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    weight_unit = models.CharField(max_length=3, choices=WEIGHT_OPTIONS, default=LBS)
    
    class Meta:
        ordering = ['set_number']
        unique_together = ['exercise', 'set_number']
    
    def __str__(self):
        return f"{self.exercise.name} - Set {self.set_number}"

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


class ProgressPicture(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progress_pictures")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='progress_pictures/')
    date_taken = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_taken', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.date_taken})"


class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    target_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    BODY_FAT = "body_fat"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    GENERAL = "general"
    
    GOAL_TYPE_CHOICES = [
        (WEIGHT_LOSS, "Weight Loss"),
        (WEIGHT_GAIN, "Weight Gain"),
        (BODY_FAT, "Body Fat Percentage"),
        (STRENGTH, "Strength Goal"),
        (ENDURANCE, "Endurance Goal"),
        (GENERAL, "General Goal"),
    ]
    
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES, default=GENERAL)
    
    LBS = "Lbs"
    KG = "Kg"
    PERCENTAGE = "%"
    REPS = "reps"
    CUSTOM = "custom"
    
    UNIT_CHOICES = [
        (LBS, "Lbs"),
        (KG, "Kg"),
        (PERCENTAGE, "%"),
        (REPS, "Reps"),
        (CUSTOM, "Custom"),
    ]
    
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default=CUSTOM)
    target_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_active', '-created_at']
    
    def __str__(self):
        return self.title