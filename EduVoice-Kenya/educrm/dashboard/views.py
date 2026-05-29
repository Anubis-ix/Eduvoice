from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from reviews.models import Review, Semester, SoftSkillRating, TeacherSelfAssessment
from schools.models import ClassRoom, Enrollment, TeacherAssignment, School
from accounts.models import User


@login_required
def dashboard(request):
    """Route to correct dashboard based on user role."""
    user = request.user
    if user.is_student:
        return student_dashboard(request)
    elif user.is_teacher:
        return teacher_dashboard(request)
    elif user.is_parent:
        return parent_dashboard(request)
    elif user.is_school_admin:
        return admin_dashboard(request)
    return render(request, 'dashboard/base_dashboard.html')


@login_required
def student_dashboard(request):
    user = request.user
    school = user.school
    semester = Semester.objects.filter(school=school, review_open=True).first()
    enrollment = Enrollment.objects.filter(student=user, is_active=True).first()

    completed_reviews = 0
    total_reviews = 0
    if enrollment and semester:
        assignments = TeacherAssignment.objects.filter(classroom=enrollment.classroom)
        total_reviews = assignments.count()
        completed_reviews = Review.objects.filter(student=user, semester=semester).count()

    past_reviews = Review.objects.filter(student=user).select_related(
        'semester', 'assignment__subject'
    ).order_by('-submitted_at')[:5]

    return render(request, 'dashboard/student.html', {
        'semester': semester,
        'enrollment': enrollment,
        'completed_reviews': completed_reviews,
        'total_reviews': total_reviews,
        'progress_pct': int((completed_reviews / total_reviews * 100) if total_reviews else 0),
        'past_reviews': past_reviews,
    })


@login_required
def teacher_dashboard(request):
    user = request.user
    school = user.school
    semester = Semester.objects.filter(school=school, review_open=True).first()

    assignments = TeacherAssignment.objects.filter(teacher=user).select_related('subject', 'classroom')

    subject_summaries = []
    for a in assignments:
        reviews = Review.objects.filter(assignment=a)
        agg = reviews.aggregate(
            avg=Avg('lesson_enjoyment'),
            count=Count('id'),
        )
        subject_summaries.append({
            'assignment': a,
            'avg_rating': round(agg['avg'] or 0, 1),
            'review_count': agg['count'],
        })

    total_students = Enrollment.objects.filter(
        classroom__in=assignments.values('classroom'), is_active=True
    ).count()

    return render(request, 'dashboard/teacher.html', {
        'semester': semester,
        'subject_summaries': subject_summaries,
        'total_students': total_students,
        'assignments': assignments,
    })


@login_required
def parent_dashboard(request):
    from schools.models import ParentStudentLink
    user = request.user
    links = ParentStudentLink.objects.filter(parent=user).select_related('student')
    children = [link.student for link in links]

    children_data = []
    for child in children:
        enrollment = Enrollment.objects.filter(student=child, is_active=True).first()
        latest_reviews = Review.objects.filter(student=child).order_by('-submitted_at')[:3]
        children_data.append({
            'child': child,
            'enrollment': enrollment,
            'latest_reviews': latest_reviews,
        })

    return render(request, 'dashboard/parent.html', {
        'children_data': children_data,
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_school_admin:
        return redirect('dashboard')

    school = request.user.school
    semester = Semester.objects.filter(school=school, review_open=True).first()

    # CRM Analytics
    total_students = User.objects.filter(school=school, role='student').count()
    total_teachers = User.objects.filter(school=school, role='teacher').count()
    total_parents = User.objects.filter(school=school, role='parent').count()
    total_classrooms = ClassRoom.objects.filter(school=school).count()

    if semester:
        reviews_submitted = Review.objects.filter(semester=semester).count()
        # Unique students who submitted at least one review
        students_reviewed = Review.objects.filter(
            semester=semester
        ).values('student').distinct().count()
        participation_rate = int((students_reviewed / total_students * 100) if total_students else 0)

        # Per-subject averages
        subject_averages = Review.objects.filter(semester=semester).values(
            'assignment__subject__name'
        ).annotate(
            avg_enjoyment=Avg('lesson_enjoyment'),
            avg_understanding=Avg('understanding'),
            avg_teacher=Avg('teacher_explains_well'),
            count=Count('id'),
        ).order_by('-avg_enjoyment')

        # Soft skill averages
        skill_averages = SoftSkillRating.objects.filter(semester=semester).values(
            'soft_skill__name', 'soft_skill__icon'
        ).annotate(avg=Avg('rating'), count=Count('id')).order_by('-avg')

        # Teacher leaderboard (anonymous-safe for admin only)
        teacher_ratings = Review.objects.filter(semester=semester).values(
            'assignment__teacher__first_name',
            'assignment__teacher__last_name',
        ).annotate(
            avg=Avg('teacher_explains_well'),
            count=Count('id'),
        ).order_by('-avg')

    else:
        reviews_submitted = students_reviewed = participation_rate = 0
        subject_averages = skill_averages = teacher_ratings = []

    # All semesters for this school
    all_semesters = Semester.objects.filter(school=school).order_by('-academic_year', '-term')

    return render(request, 'dashboard/admin.html', {
        'school': school,
        'semester': semester,
        'all_semesters': all_semesters,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_parents': total_parents,
        'total_classrooms': total_classrooms,
        'reviews_submitted': reviews_submitted,
        'students_reviewed': students_reviewed,
        'participation_rate': participation_rate,
        'subject_averages': subject_averages,
        'skill_averages': skill_averages,
        'teacher_ratings': teacher_ratings,
    })
