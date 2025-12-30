from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'updated_on']

admin.site.register(User, UserAdmin)
