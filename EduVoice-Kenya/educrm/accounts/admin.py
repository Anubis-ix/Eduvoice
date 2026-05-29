from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'role', 'school', 'is_active']
    list_filter = ['role', 'school', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('EduVoice', {'fields': ('role', 'school', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('EduVoice', {'fields': ('role', 'school')}),
    )
