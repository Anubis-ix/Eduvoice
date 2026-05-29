from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from .models import Review, SoftSkillRating, TeacherSelfAssessment, Semester, ParentAcknowledgement
from .forms import ReviewForm, SoftSkillRatingForm, TeacherSelfAssessmentForm
from schools.models import ClassRoom, Enrollment, TeacherAssignment
from curriculum.models import SoftSkill
from accounts.models import User


@login_required
def student_review_home(request):
    """Student sees all subjects they need to review this semester."""
    if not request.user.is_student:
        return redirect('dashboard')

    school = request.user.school
    semester = Semester.objects.filter(school=school, review_open=True).first()
    if not semester:
        return render(request, 'reviews/no_semester.html')

    enrollment = Enrollment.objects.filter(student=request.user, is_active=True).first()
    if not enrollment:
        return render(request, 'reviews/no_enrollment.html')

    classroom = enrollment.classroom
    assignments = TeacherAssignment.objects.filter(classroom=classroom).select_related('teacher', 'subject')

    # Which reviews has this student already submitted?
    submitted_ids = Review.objects.filter(
        student=request.user, semester=semester
    ).values_list('assignment_id', flat=True)

    # Soft skills status
    soft_skills = SoftSkill.objects.filter(is_active=True)
    rated_skill_ids = SoftSkillRating.objects.filter(
        student=request.user, semester=semester
    ).values_list('soft_skill_id', flat=True)

    review_items = []
    for assignment in assignments:
        review_items.append({
            'assignment': assignment,
            'submitted': assignment.id in submitted_ids,
        })

    all_done = len(submitted_ids) == assignments.count() and set(soft_skills.values_list('id', flat=True)) == set(rated_skill_ids)

    return render(request, 'reviews/student_home.html', {
        'semester': semester,
        'classroom': classroom,
        'review_items': review_items,
        'soft_skills': soft_skills,
        'rated_skill_ids': list(rated_skill_ids),
        'all_done': all_done,
    })


@login_required
def submit_review(request, assignment_id):
    """Student submits a review for one subject/teacher."""
    if not request.user.is_student:
        return redirect('dashboard')

    assignment = get_object_or_404(TeacherAssignment, id=assignment_id)
    school = request.user.school
    semester = get_object_or_404(Semester, school=school, review_open=True)

    existing = Review.objects.filter(student=request.user, semester=semester, assignment=assignment).first()
    if existing:
        messages.info(request, 'You already submitted this review.')
        return redirect('student_review_home')

    enrollment = get_object_or_404(Enrollment, student=request.user, is_active=True)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.student = request.user
            review.semester = semester
            review.classroom = enrollment.classroom
            review.assignment = assignment
            review.save()
            messages.success(request, f'Review for {assignment.subject.name} submitted! 🎉')
            return redirect('student_review_home')
    else:
        form = ReviewForm()

    return render(request, 'reviews/submit_review.html', {
        'form': form,
        'assignment': assignment,
        'semester': semester,
    })


@login_required
def submit_softskills(request):
    """Student rates their own soft skills for the semester."""
    if not request.user.is_student:
        return redirect('dashboard')

    school = request.user.school
    semester = get_object_or_404(Semester, school=school, review_open=True)
    soft_skills = SoftSkill.objects.filter(is_active=True)

    existing_ratings = {r.soft_skill_id: r for r in SoftSkillRating.objects.filter(
        student=request.user, semester=semester
    )}

    if request.method == 'POST':
        all_saved = True
        for skill in soft_skills:
            rating_val = request.POST.get(f'rating_{skill.id}')
            reflection_val = request.POST.get(f'reflection_{skill.id}', '')
            if rating_val:
                SoftSkillRating.objects.update_or_create(
                    student=request.user, semester=semester, soft_skill=skill,
                    defaults={'rating': int(rating_val), 'reflection': reflection_val}
                )
            else:
                all_saved = False
        if all_saved:
            messages.success(request, 'Your skills reflection has been saved! 🌟')
            return redirect('student_review_home')
        else:
            messages.warning(request, 'Please rate all skills before submitting.')

    return render(request, 'reviews/submit_softskills.html', {
        'semester': semester,
        'soft_skills': soft_skills,
        'existing_ratings': existing_ratings,
    })


@login_required
def teacher_feedback_view(request):
    """Teacher sees aggregated (anonymous) feedback on their teaching."""
    if not request.user.is_teacher:
        return redirect('dashboard')

    school = request.user.school
    semesters = Semester.objects.filter(school=school).order_by('-academic_year', '-term')
    selected_semester_id = request.GET.get('semester')

    if selected_semester_id:
        semester = get_object_or_404(Semester, id=selected_semester_id, school=school)
    else:
        semester = semesters.first()

    assignments = TeacherAssignment.objects.filter(teacher=request.user).select_related('subject', 'classroom')

    feedback_data = []
    for assignment in assignments:
        reviews = Review.objects.filter(assignment=assignment, semester=semester)
        if reviews.exists():
            aggregated = reviews.aggregate(
                avg_enjoyment=Avg('lesson_enjoyment'),
                avg_understanding=Avg('understanding'),
                avg_explains=Avg('teacher_explains_well'),
                avg_encourages=Avg('teacher_encourages'),
                avg_realworld=Avg('real_world_connection'),
                count=Count('id'),
            )
            # Collect open text (anonymised - no student names)
            favourites = list(reviews.exclude(favourite_thing='').values_list('favourite_thing', flat=True))
            suggestions = list(reviews.exclude(suggestion='').values_list('suggestion', flat=True))
            feedback_data.append({
                'assignment': assignment,
                'aggregated': aggregated,
                'favourites': favourites,
                'suggestions': suggestions,
            })

    # Teacher's own self-assessment
    self_assessment = TeacherSelfAssessment.objects.filter(
        teacher=request.user, semester=semester
    ).first() if semester else None

    return render(request, 'reviews/teacher_feedback.html', {
        'semester': semester,
        'semesters': semesters,
        'feedback_data': feedback_data,
        'self_assessment': self_assessment,
    })


@login_required
def teacher_self_assess(request, classroom_id, subject_id):
    """Teacher submits self-assessment for a class+subject."""
    if not request.user.is_teacher:
        return redirect('dashboard')

    from curriculum.models import Subject
    classroom = get_object_or_404(ClassRoom, id=classroom_id)
    subject = get_object_or_404(Subject, id=subject_id)
    school = request.user.school
    semester = get_object_or_404(Semester, school=school, review_open=True)

    existing = TeacherSelfAssessment.objects.filter(
        teacher=request.user, semester=semester, classroom=classroom, subject=subject
    ).first()

    if request.method == 'POST':
        form = TeacherSelfAssessmentForm(request.POST, instance=existing)
        if form.is_valid():
            sa = form.save(commit=False)
            sa.teacher = request.user
            sa.semester = semester
            sa.classroom = classroom
            sa.subject = subject
            sa.save()
            messages.success(request, 'Self-assessment saved.')
            return redirect('teacher_feedback')
    else:
        form = TeacherSelfAssessmentForm(instance=existing)

    return render(request, 'reviews/teacher_self_assess.html', {
        'form': form, 'classroom': classroom, 'subject': subject, 'semester': semester,
    })


@login_required
def parent_report_view(request):
    """Parent views their child's submitted reviews."""
    if not request.user.is_parent:
        return redirect('dashboard')

    # Parent is linked to children via ParentLink
    from schools.models import ParentStudentLink
    links = ParentStudentLink.objects.filter(parent=request.user).select_related('student')
    children = [link.student for link in links]

    school = request.user.school
    semesters = Semester.objects.filter(school=school).order_by('-academic_year', '-term')
    selected_semester_id = request.GET.get('semester')
    semester = Semester.objects.filter(id=selected_semester_id).first() if selected_semester_id else semesters.first()

    selected_child_id = request.GET.get('child')
    child = None
    reviews = []
    softskill_ratings = []

    if selected_child_id:
        child = next((c for c in children if str(c.id) == selected_child_id), None)
    elif children:
        child = children[0]

    if child and semester:
        reviews = Review.objects.filter(
            student=child, semester=semester
        ).select_related('assignment__subject', 'assignment__teacher')
        softskill_ratings = SoftSkillRating.objects.filter(
            student=child, semester=semester
        ).select_related('soft_skill')

        # Mark parent acknowledgement
        ack, created = ParentAcknowledgement.objects.get_or_create(
            parent=request.user, student=child, semester=semester
        )
        if created:
            ack.save()

    return render(request, 'reviews/parent_report.html', {
        'children': children,
        'child': child,
        'semesters': semesters,
        'semester': semester,
        'reviews': reviews,
        'softskill_ratings': softskill_ratings,
    })
