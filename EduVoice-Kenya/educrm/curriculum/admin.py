from django.contrib import admin
from .models import Subject, SoftSkill

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'level', 'icon', 'is_core', 'is_active']
    list_filter = ['level', 'is_core', 'is_active']

@admin.register(SoftSkill)
class SoftSkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'icon', 'is_active']
