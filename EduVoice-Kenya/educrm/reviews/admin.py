from django.contrib import admin
from .models import Semester, Review, SoftSkillRating, TeacherSelfAssessment, ParentAcknowledgement

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'academic_year', 'term', 'review_open', 'review_deadline']
    list_filter = ['school', 'academic_year', 'review_open']
    list_editable = ['review_open']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'semester', 'average_rating', 'submitted_at']
    list_filter = ['semester', 'assignment__subject']
    search_fields = ['student__first_name', 'student__last_name']

@admin.register(SoftSkillRating)
class SoftSkillRatingAdmin(admin.ModelAdmin):
    list_display = ['student', 'soft_skill', 'rating', 'semester']
    list_filter = ['soft_skill', 'semester']

@admin.register(TeacherSelfAssessment)
class TeacherSelfAssessmentAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'classroom', 'semester', 'submitted_at']

@admin.register(ParentAcknowledgement)
class ParentAcknowledgementAdmin(admin.ModelAdmin):
    list_display = ['parent', 'student', 'semester', 'acknowledged_at']
