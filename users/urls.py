from django.urls import path, include
from .views import *

urlpatterns = [
    path('', Login.as_view(), name='login'),
    path('create_account/', Create_Account.as_view(), name='create_account'),
    path('logout/', Logout.as_view(), name='logout'),
    path('home/', Home.as_view(), name='home'),
    path('profile/', Profile.as_view(), name='profile'),
    path('edit_profile/', EditProfile.as_view(), name='edit_profile'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
    ]
