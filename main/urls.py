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
    path('workouts/', views.my_workouts, name='my_workouts'),
    path('workout/create/', views.create_workout, name='create_workout'),
    path('workout/<int:workout_id>/', views.workout_detail, name='workout_detail'),
]