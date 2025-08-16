from django.contrib import admin
from .models import Workout, Exercise, Set, Meal, Food, UserProfile

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Workout)
admin.site.register(Exercise)
admin.site.register(Set)
admin.site.register(Meal)
admin.site.register(Food)
