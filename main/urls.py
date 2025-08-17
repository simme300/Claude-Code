from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('homepage/', views.homepage, name='homepage'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('progress-pictures/', views.progress_pictures, name='progress_pictures'),
    path('progress-pictures/add/', views.add_progress_picture, name='add_progress_picture'),
    path('workouts/', views.my_workouts, name='my_workouts'),
    path('workout/create/', views.create_workout, name='create_workout'),
    path('workout/<int:workout_id>/', views.workout_detail, name='workout_detail'),
    path('goals/', views.manage_goals, name='manage_goals'),
    path('goals/add/', views.add_goal, name='add_goal'),
    path('goals/<int:goal_id>/edit/', views.edit_goal, name='edit_goal'),
    path('goals/<int:goal_id>/toggle/', views.toggle_goal_completion, name='toggle_goal_completion'),
    path('goals/<int:goal_id>/delete/', views.delete_goal, name='delete_goal'),
    path('meals/', views.meal_tracking, name='meal_tracking'),
    path('meals/add/', views.add_meal, name='add_meal'),
    path('meals/<int:meal_id>/', views.meal_detail, name='meal_detail'),
    path('meals/<int:meal_id>/edit/', views.edit_meal, name='edit_meal'),
    path('meals/<int:meal_id>/delete/', views.delete_meal, name='delete_meal'),
]