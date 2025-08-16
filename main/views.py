from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, WorkoutForm, CustomAuthenticationForm, ExerciseFormSet, SetFormSet, UserProfileForm
from .models import UserProfile


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
    """Homepage for logged-in users."""
    # Get or create user profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Calculate basic stats
    total_workouts = request.user.workouts.count()
    
    context = {
        'user_profile': user_profile,
        'total_workouts': total_workouts,
        'profile_incomplete': not (user_profile.age and user_profile.current_weight),
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
                
                # Save exercises that have data
                for exercise_form in valid_exercises:
                    exercise = exercise_form.save(commit=False)
                    exercise.workout = workout
                    exercise.save()
                
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
