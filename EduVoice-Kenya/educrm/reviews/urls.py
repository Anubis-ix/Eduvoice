from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_review_home, name='student_review_home'),
    path('submit/<int:assignment_id>/', views.submit_review, name='submit_review'),
    path('softskills/', views.submit_softskills, name='submit_softskills'),
    path('teacher/', views.teacher_feedback_view, name='teacher_feedback'),
    path('teacher/self-assess/<int:classroom_id>/<int:subject_id>/', views.teacher_self_assess, name='teacher_self_assess'),
    path('parent/', views.parent_report_view, name='parent_report'),
]
