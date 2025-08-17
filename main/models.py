from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    age = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(13), MaxValueValidator(120)])
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    body_fat_percentage = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    MALE = "M"
    FEMALE = "F"
    
    GENDER_CHOICES = [
        (MALE, "Male"),
        (FEMALE, "Female"),
    ]
    
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    
    # Weight goals
    target_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    weight_loss_rate = models.DecimalField(max_digits=3, decimal_places=1, default=0.5, validators=[MinValueValidator(0.1), MaxValueValidator(2.0)], help_text="Target weight loss per week in kg")
    
    # Activity level for TDEE calculation
    SEDENTARY = "1.2"
    LIGHT = "1.375"
    MODERATE = "1.55"
    ACTIVE = "1.725"
    VERY_ACTIVE = "1.9"
    
    ACTIVITY_LEVEL_CHOICES = [
        (SEDENTARY, "Sedentary (little/no exercise)"),
        (LIGHT, "Light (light exercise 1-3 days/week)"),
        (MODERATE, "Moderate (moderate exercise 3-5 days/week)"),
        (ACTIVE, "Active (hard exercise 6-7 days/week)"),
        (VERY_ACTIVE, "Very Active (very hard exercise, physical job)")
    ]
    
    activity_level = models.CharField(max_length=5, choices=ACTIVITY_LEVEL_CHOICES, default=SEDENTARY)
    
    LBS = "Lbs"
    KG = "Kg"
    
    WEIGHT_UNIT_CHOICES = [
        (LBS, "Lbs"),
        (KG, "Kg"),
    ]
    
    weight_unit = models.CharField(max_length=3, choices=WEIGHT_UNIT_CHOICES, default=LBS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_weight_in_kg(self):
        """Convert weight to kg for calculations."""
        if not self.current_weight:
            return None
        if self.weight_unit == self.LBS:
            return float(self.current_weight) * 0.453592  # Convert lbs to kg
        return float(self.current_weight)
    
    def calculate_bmr(self):
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation.
        Returns BMR in calories/day or None if insufficient data.
        """
        if not all([self.age, self.current_weight, self.gender]):
            return None
        
        weight_kg = self.get_weight_in_kg()
        if not weight_kg:
            return None
        
        # Mifflin-St Jeor Equation
        # Men: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(years) + 5
        # Women: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(years) - 161
        
        # Since we don't have height, we'll use a simplified version based on weight and age
        # This is an approximation - ideally height should be added later
        if self.gender == self.MALE:
            # Simplified for men: BMR ≈ 10 × weight(kg) - 5 × age + 5 + estimated height component
            bmr = (10 * weight_kg) - (5 * self.age) + 5 + 1000  # +1000 as height approximation
        else:  # Female
            # Simplified for women: BMR ≈ 10 × weight(kg) - 5 × age - 161 + estimated height component
            bmr = (10 * weight_kg) - (5 * self.age) - 161 + 1000  # +1000 as height approximation
        
        return round(bmr, 0)
    
    def get_bmr_display(self):
        """Get BMR with proper formatting."""
        bmr = self.calculate_bmr()
        if bmr:
            return f"{int(bmr)} cal/day"
        return "Incomplete data"
    
    def calculate_tdee(self):
        """
        Calculate Total Daily Energy Expenditure (TDEE).
        TDEE = BMR × Activity Level Factor
        """
        bmr = self.calculate_bmr()
        if not bmr:
            return None
        
        activity_multiplier = float(self.activity_level)
        return round(bmr * activity_multiplier, 0)
    
    def get_target_weight_in_kg(self):
        """Convert target weight to kg for calculations."""
        if not self.target_weight:
            return None
        if self.weight_unit == self.LBS:
            return float(self.target_weight) * 0.453592
        return float(self.target_weight)
    
    def calculate_daily_calorie_target(self):
        """
        Calculate daily calorie target based on weight goals.
        Returns calories per day needed to reach target weight.
        """
        tdee = self.calculate_tdee()
        if not tdee or not self.target_weight:
            return None
        
        current_weight_kg = self.get_weight_in_kg()
        target_weight_kg = self.get_target_weight_in_kg()
        
        if not current_weight_kg or not target_weight_kg:
            return None
        
        # Calculate if user wants to lose or gain weight
        weight_difference = target_weight_kg - current_weight_kg
        
        # 1 kg of body weight ≈ 7700 calories
        # Calculate weekly calorie deficit/surplus needed
        weekly_rate_kg = float(self.weight_loss_rate)
        if weight_difference < 0:  # Weight loss
            weekly_rate_kg = -abs(weekly_rate_kg)
        else:  # Weight gain
            weekly_rate_kg = abs(weekly_rate_kg)
        
        weekly_calorie_adjustment = weekly_rate_kg * 7700
        daily_calorie_adjustment = weekly_calorie_adjustment / 7
        
        daily_target = tdee + daily_calorie_adjustment
        return round(daily_target, 0)
    
    def calculate_weekly_calorie_target(self):
        """Calculate weekly calorie target."""
        daily_target = self.calculate_daily_calorie_target()
        if daily_target:
            return daily_target * 7
        return None
    
    def calculate_monthly_calorie_target(self):
        """Calculate monthly calorie target (30 days)."""
        daily_target = self.calculate_daily_calorie_target()
        if daily_target:
            return daily_target * 30
        return None
    
    def calculate_adjusted_daily_calories(self, days_back=7):
        """
        Calculate adjusted daily calories based on recent consumption.
        This method looks at recent meal consumption and adjusts daily target
        to stay on track with weekly/monthly goals.
        """
        from datetime import date, timedelta
        
        daily_target = self.calculate_daily_calorie_target()
        weekly_target = self.calculate_weekly_calorie_target()
        
        if not daily_target or not weekly_target:
            return None
        
        # Get recent meals
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back-1)
        
        recent_meals = self.user.meals.filter(date_consumed__range=[start_date, end_date])
        
        # Calculate total calories consumed in the period
        total_consumed = 0
        consumption_by_date = {}
        
        for meal in recent_meals:
            meal_date = meal.date_consumed
            if meal_date not in consumption_by_date:
                consumption_by_date[meal_date] = 0
            consumption_by_date[meal_date] += float(meal.total_calories)
        
        # Calculate total consumed and days with data
        days_with_data = len(consumption_by_date)
        total_consumed = sum(consumption_by_date.values())
        
        if days_with_data == 0:
            return daily_target  # No data, return normal target
        
        # Calculate how many calories should have been consumed
        target_consumed = float(daily_target) * days_with_data
        
        # Calculate difference
        calorie_difference = total_consumed - target_consumed
        
        # Adjust remaining days in the week to compensate
        remaining_days = 7 - days_with_data
        if remaining_days <= 0:
            remaining_days = 1  # At least adjust today
        
        adjusted_daily = float(daily_target) - (calorie_difference / remaining_days)
        
        # Don't go below 1200 calories (minimum safe level)
        adjusted_daily = max(adjusted_daily, 1200)
        
        return round(adjusted_daily, 0)
    
    def get_calorie_summary(self):
        """Get a summary of all calorie targets."""
        daily = self.calculate_daily_calorie_target()
        weekly = self.calculate_weekly_calorie_target()
        monthly = self.calculate_monthly_calorie_target()
        adjusted = self.calculate_adjusted_daily_calories()
        
        return {
            'daily_target': daily,
            'weekly_target': weekly,
            'monthly_target': monthly,
            'adjusted_daily': adjusted,
            'tdee': self.calculate_tdee(),
            'bmr': self.calculate_bmr()
        }
    
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