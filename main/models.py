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
    name = models.CharField(max_length=50)
    date_consumed = models.DateField(auto_now_add=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_calories(self):
        """Calculate total calories from all foods in this meal."""
        return sum(food.total_calories for food in self.foods.all())
    
    @property
    def total_carbs(self):
        """Calculate total carbs from all foods in this meal."""
        return sum(food.total_carbs for food in self.foods.all())
    
    @property
    def total_fat(self):
        """Calculate total fat from all foods in this meal."""
        return sum(food.total_fat for food in self.foods.all())
    
    @property
    def total_protein(self):
        """Calculate total protein from all foods in this meal."""
        return sum(food.total_protein for food in self.foods.all())
    
    class Meta:
        ordering = ['-date_consumed', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.date_consumed}"


class Food(models.Model):
    name = models.CharField(max_length=50)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="foods")
    grams = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
    
    # Nutritional values per 100g
    calories_per_100g = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    carbs_per_100g = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    fat_per_100g = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    protein_per_100g = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    
    @property
    def total_calories(self):
        """Calculate total calories for this food item based on grams."""
        return (self.calories_per_100g * self.grams) / 100
    
    @property
    def total_carbs(self):
        """Calculate total carbs for this food item based on grams."""
        return (self.carbs_per_100g * self.grams) / 100
    
    @property
    def total_fat(self):
        """Calculate total fat for this food item based on grams."""
        return (self.fat_per_100g * self.grams) / 100
    
    @property
    def total_protein(self):
        """Calculate total protein for this food item based on grams."""
        return (self.protein_per_100g * self.grams) / 100
    
    def __str__(self):
        return f"{self.name} ({self.grams}g)"


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