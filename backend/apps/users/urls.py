"""
URL patterns for user authentication.
"""
from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    UserRegistrationView,
    UserProfileView,
    PasswordChangeView,
    LogoutView,
    UserListView,
)

app_name = 'users'

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', UserListView.as_view(), name='user_list'),
]
