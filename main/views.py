from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from .forms import SignUpForm, WorkoutForm, CustomAuthenticationForm, ExerciseFormSet, SetFormSet, UserProfileForm, ProgressPictureForm, GoalForm, MealForm, FoodForm, FoodFormSet
from .models import UserProfile, ProgressPicture, Goal, Meal, Food


def index(request):
    """Main index view for the application."""
    return render(request, 'main/index.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('main:login')
    else:
        form = SignUpForm()
    return render(request, 'main/signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main:homepage')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'main/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('main:login')


@login_required
def homepage(request):
    """Dashboard homepage for logged-in users."""
    # Get or create user profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get comprehensive dashboard data
    workout_stats = user_profile.get_workout_statistics()
    calorie_summary = user_profile.get_calorie_summary()
    goal_progress = user_profile.get_goal_progress_summary()
    active_goals = request.user.goals.filter(is_active=True)
    
    # Check if profile is complete
    profile_incomplete = not (user_profile.age and user_profile.current_weight)
    bmr_incomplete = not (user_profile.age and user_profile.current_weight and user_profile.gender)
    goals_incomplete = not active_goals.exists()
    
    # User information summary
    user_info = {
        'name': request.user.get_full_name() or request.user.username,
        'age': user_profile.age,
        'weight': user_profile.current_weight,
        'weight_unit': user_profile.weight_unit,
        'gender': user_profile.get_gender_display() if user_profile.gender else None,
        'body_fat': user_profile.body_fat_percentage,
        'bmr': user_profile.calculate_bmr(),
        'tdee': user_profile.calculate_tdee(),
    }
    
    context = {
        'user_profile': user_profile,
        'user_info': user_info,
        'workout_stats': workout_stats,
        'calorie_summary': calorie_summary,
        'goal_progress': goal_progress,
        'active_goals': active_goals,
        'profile_incomplete': profile_incomplete,
        'bmr_incomplete': bmr_incomplete,
        'goals_incomplete': goals_incomplete,
    }
    
    return render(request, 'main/homepage.html', context)


@login_required
def workout_detail(request, workout_id):
    """Display detailed view of a specific workout."""
    workout = request.user.workouts.get(id=workout_id)
    exercises = workout.exercises.all()
    return render(request, 'main/workout_detail.html', {
        'workout': workout,
        'exercises': exercises
    })


@login_required
def my_workouts(request):
    """Display all workouts for the logged-in user."""
    workouts = request.user.workouts.all().order_by('-created_at')
    return render(request, 'main/my_workouts.html', {'workouts': workouts})


@login_required
def create_workout(request):
    exercise_error = None
    
    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        exercise_formset = ExerciseFormSet(request.POST)
        
        if form.is_valid() and exercise_formset.is_valid():
            # Check if at least one exercise has data
            valid_exercises = []
            for exercise_form in exercise_formset:
                if exercise_form.cleaned_data and exercise_form.cleaned_data.get('name'):
                    valid_exercises.append(exercise_form)
            
            if not valid_exercises:
                exercise_error = "You must add at least one exercise to create a workout."
            else:
                workout = form.save(commit=False)
                workout.user = request.user
                # Set workout number based on user's current workout count
                user_workout_count = request.user.workouts.count()
                workout.workout_number = user_workout_count + 1
                workout.save()
                
                # Save exercises and their sets
                for exercise_index, exercise_form in enumerate(valid_exercises):
                    exercise = exercise_form.save(commit=False)
                    exercise.workout = workout
                    exercise.save()
                    
                    # Process sets for this exercise
                    set_number = 1
                    set_index = 0
                    
                    while True:
                        reps_key = f'exercise_{exercise_index}_set_{set_index}_reps'
                        weight_key = f'exercise_{exercise_index}_set_{set_index}_weight'
                        weight_unit_key = f'exercise_{exercise_index}_set_{set_index}_weight_unit'
                        
                        if reps_key not in request.POST:
                            break
                        
                        reps = request.POST.get(reps_key)
                        weight = request.POST.get(weight_key)
                        weight_unit = request.POST.get(weight_unit_key, 'Lbs')
                        
                        # Only create set if reps is provided and not empty
                        if reps and reps.strip():
                            from .models import Set
                            Set.objects.create(
                                exercise=exercise,
                                set_number=set_number,
                                reps=int(reps),
                                weight=float(weight) if weight and weight.strip() else 0,
                                weight_unit=weight_unit
                            )
                            set_number += 1
                        
                        set_index += 1
                
                return redirect('main:homepage')
    else:
        form = WorkoutForm()
        exercise_formset = ExerciseFormSet()
    
    return render(request, 'main/create_workout.html', {
        'form': form,
        'exercise_formset': exercise_formset,
        'exercise_error': exercise_error
    })


@login_required
def edit_profile(request):
    """Edit user profile information."""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('main:homepage')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'main/edit_profile.html', {'form': form})


@login_required
def progress_pictures(request):
    """Display all progress pictures for the logged-in user."""
    pictures = request.user.progress_pictures.all()
    return render(request, 'main/progress_pictures.html', {'pictures': pictures})


@login_required
def add_progress_picture(request):
    """Add a new progress picture."""
    if request.method == 'POST':
        form = ProgressPictureForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.save(commit=False)
            picture.user = request.user
            picture.save()
            return redirect('main:progress_pictures')
    else:
        form = ProgressPictureForm()
    
    return render(request, 'main/add_progress_picture.html', {'form': form})


@login_required
def add_goal(request):
    """Add a new goal."""
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('main:homepage')
    else:
        form = GoalForm()
    
    return render(request, 'main/add_goal.html', {'form': form})


@login_required
def manage_goals(request):
    """Display and manage all goals for the logged-in user."""
    goals = request.user.goals.all()
    return render(request, 'main/manage_goals.html', {'goals': goals})


@login_required
def edit_goal(request, goal_id):
    """Edit an existing goal."""
    goal = request.user.goals.get(id=goal_id)
    
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('main:manage_goals')
    else:
        form = GoalForm(instance=goal)
    
    return render(request, 'main/edit_goal.html', {'form': form, 'goal': goal})


@login_required
def toggle_goal_completion(request, goal_id):
    """Toggle goal completion status."""
    goal = request.user.goals.get(id=goal_id)
    goal.is_completed = not goal.is_completed
    if goal.is_completed:
        from django.utils import timezone
        goal.completed_date = timezone.now().date()
    else:
        goal.completed_date = None
    goal.save()
    return redirect('main:manage_goals')


@login_required
def delete_goal(request, goal_id):
    """Delete a goal."""
    goal = request.user.goals.get(id=goal_id)
    goal.delete()
    return redirect('main:manage_goals')


@login_required
def meal_tracking(request):
    """Display all meals for the logged-in user with date filtering."""
    from datetime import datetime, timedelta
    import datetime as dt
    
    # Get date parameter from request, default to today
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = dt.date.today()
    else:
        selected_date = dt.date.today()
    
    # Calculate previous and next dates
    prev_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)
    
    # Get view mode - 'day' for single day, 'all' for all days
    view_mode = request.GET.get('view', 'day')
    
    if view_mode == 'day':
        # Show only selected day
        meals = request.user.meals.filter(date_consumed=selected_date)
        
        # Calculate totals for the selected day
        daily_total = {
            'calories': 0,
            'carbs': 0,
            'fat': 0,
            'protein': 0,
            'meals': []
        }
        
        for meal in meals:
            daily_total['calories'] += meal.total_calories
            daily_total['carbs'] += meal.total_carbs
            daily_total['fat'] += meal.total_fat
            daily_total['protein'] += meal.total_protein
            daily_total['meals'].append(meal)
        
        # Check if user has meals on previous/next days for navigation
        has_prev_meals = request.user.meals.filter(date_consumed=prev_date).exists()
        has_next_meals = request.user.meals.filter(date_consumed=next_date).exists()
        
        context = {
            'view_mode': 'day',
            'selected_date': selected_date,
            'today': dt.date.today(),
            'prev_date': prev_date,
            'next_date': next_date,
            'has_prev_meals': has_prev_meals,
            'has_next_meals': has_next_meals,
            'daily_total': daily_total,
            'meals': meals,
        }
    else:
        # Show all days (original view)
        meals = request.user.meals.all()
        
        # Calculate daily totals
        daily_totals = {}
        for meal in meals:
            date = meal.date_consumed
            if date not in daily_totals:
                daily_totals[date] = {
                    'calories': 0,
                    'carbs': 0,
                    'fat': 0,
                    'protein': 0,
                    'meals': []
                }
            daily_totals[date]['calories'] += meal.total_calories
            daily_totals[date]['carbs'] += meal.total_carbs
            daily_totals[date]['fat'] += meal.total_fat
            daily_totals[date]['protein'] += meal.total_protein
            daily_totals[date]['meals'].append(meal)
        
        # Sort by date (newest first)
        sorted_daily_totals = dict(sorted(daily_totals.items(), reverse=True))
        
        context = {
            'view_mode': 'all',
            'selected_date': selected_date,
            'today': dt.date.today(),
            'daily_totals': sorted_daily_totals,
            'meals': meals,
        }
    
    return render(request, 'main/meal_tracking.html', context)


@login_required
def add_meal(request):
    """Add a new meal with foods."""
    if request.method == 'POST':
        meal_form = MealForm(request.POST)
        food_formset = FoodFormSet(request.POST)
        
        if meal_form.is_valid() and food_formset.is_valid():
            # Check if at least one food has data
            valid_foods = []
            for food_form in food_formset:
                if food_form.cleaned_data and food_form.cleaned_data.get('name'):
                    valid_foods.append(food_form)
            
            if not valid_foods:
                food_error = "You must add at least one food item to create a meal."
                return render(request, 'main/add_meal.html', {
                    'meal_form': meal_form,
                    'food_formset': food_formset,
                    'food_error': food_error
                })
            
            # Save the meal
            meal = meal_form.save(commit=False)
            meal.user = request.user
            meal.save()
            
            # Save the foods
            for food_form in valid_foods:
                food = food_form.save(commit=False)
                food.meal = meal
                food.save()
            
            return redirect('main:meal_tracking')
    else:
        meal_form = MealForm()
        food_formset = FoodFormSet()
    
    return render(request, 'main/add_meal.html', {
        'meal_form': meal_form,
        'food_formset': food_formset
    })


@login_required
def meal_detail(request, meal_id):
    """Display detailed view of a specific meal."""
    meal = request.user.meals.get(id=meal_id)
    foods = meal.foods.all()
    
    context = {
        'meal': meal,
        'foods': foods,
    }
    
    return render(request, 'main/meal_detail.html', context)


@login_required
def edit_meal(request, meal_id):
    """Edit an existing meal."""
    meal = request.user.meals.get(id=meal_id)
    
    if request.method == 'POST':
        meal_form = MealForm(request.POST, instance=meal)
        
        # Create formset with existing foods
        FoodFormSetWithExtra = formset_factory(FoodForm, extra=1, can_delete=True)
        food_formset = FoodFormSetWithExtra(request.POST, initial=[{
            'name': food.name,
            'grams': food.grams,
            'calories_per_100g': food.calories_per_100g,
            'carbs_per_100g': food.carbs_per_100g,
            'fat_per_100g': food.fat_per_100g,
            'protein_per_100g': food.protein_per_100g,
        } for food in meal.foods.all()])
        
        if meal_form.is_valid() and food_formset.is_valid():
            # Update the meal
            meal_form.save()
            
            # Delete existing foods and create new ones
            meal.foods.all().delete()
            
            # Save new foods
            for food_form in food_formset:
                if food_form.cleaned_data and food_form.cleaned_data.get('name') and not food_form.cleaned_data.get('DELETE'):
                    food = food_form.save(commit=False)
                    food.meal = meal
                    food.save()
            
            return redirect('main:meal_detail', meal_id=meal.id)
    else:
        meal_form = MealForm(instance=meal)
        
        # Create formset with existing foods
        FoodFormSetWithExtra = formset_factory(FoodForm, extra=1, can_delete=True)
        food_formset = FoodFormSetWithExtra(initial=[{
            'name': food.name,
            'grams': food.grams,
            'calories_per_100g': food.calories_per_100g,
            'carbs_per_100g': food.carbs_per_100g,
            'fat_per_100g': food.fat_per_100g,
            'protein_per_100g': food.protein_per_100g,
        } for food in meal.foods.all()])
    
    return render(request, 'main/edit_meal.html', {
        'meal_form': meal_form,
        'food_formset': food_formset,
        'meal': meal
    })


@login_required
def delete_meal(request, meal_id):
    """Delete a meal."""
    meal = request.user.meals.get(id=meal_id)
    meal.delete()
    return redirect('main:meal_tracking')
