from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('members/', views.members, name='members'),
    path('classes/', views.classes, name='classes'),
    path('instructors/', views.instructors, name='instructors'),
    path('register/', views.register, name='register'),
    path('plans/', views.plans, name='plans'),
]