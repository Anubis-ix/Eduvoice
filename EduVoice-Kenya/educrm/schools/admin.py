from django.contrib import admin
from .models import School, ClassRoom, Enrollment, TeacherAssignment, ParentStudentLink

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'county', 'subscription_plan', 'is_active', 'total_students', 'total_teachers']
    list_filter = ['subscription_plan', 'is_active', 'county']
    search_fields = ['name', 'code']

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'school', 'grade', 'stream', 'academic_year', 'class_teacher']
    list_filter = ['school', 'grade', 'academic_year']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'classroom', 'is_active', 'enrolled_at']
    list_filter = ['classroom__school', 'is_active']
    search_fields = ['student__first_name', 'student__last_name']

@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'classroom']
    list_filter = ['classroom__school', 'subject']

@admin.register(ParentStudentLink)
class ParentStudentLinkAdmin(admin.ModelAdmin):
    list_display = ['parent', 'student', 'created_at']
    search_fields = ['parent__first_name', 'student__first_name']
