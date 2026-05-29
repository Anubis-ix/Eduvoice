from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Semester(models.Model):
    TERM_1 = 1
    TERM_2 = 2
    TERM_3 = 3
    TERM_CHOICES = [(1, 'Term 1'), (2, 'Term 2'), (3, 'Term 3')]

    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='semesters')
    academic_year = models.IntegerField()
    term = models.IntegerField(choices=TERM_CHOICES)
    name = models.CharField(max_length=100)  # e.g. "Term 1 - 2025"
    start_date = models.DateField()
    end_date = models.DateField()
    review_open = models.BooleanField(default=False)  # admin toggles this to open reviews
    review_deadline = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ['school', 'academic_year', 'term']
        ordering = ['-academic_year', '-term']

    def __str__(self):
        return f"{self.school.name} - {self.name}"


class Review(models.Model):
    """A student's end-of-term review for a teacher + subject combination."""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    student = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE,
        related_name='reviews_given', limit_choices_to={'role': 'student'}
    )
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='reviews')
    classroom = models.ForeignKey('schools.ClassRoom', on_delete=models.CASCADE, related_name='reviews')
    assignment = models.ForeignKey(
        'schools.TeacherAssignment', on_delete=models.CASCADE, related_name='reviews'
    )

    # Core reflective questions (positive CBC framing)
    lesson_enjoyment = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="How much did you enjoy this subject this term? (1=Not much, 5=Loved it)"
    )
    understanding = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="How well did you understand what was taught? (1=Very confused, 5=Understood everything)"
    )
    teacher_explains_well = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="How clearly did your teacher explain things? (1=Hard to follow, 5=Very clear)"
    )
    teacher_encourages = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="How much did your teacher encourage you to ask questions? (1=Never, 5=Always)"
    )
    real_world_connection = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="Did the lessons show you how this subject matters in real life? (1=Not really, 5=Yes, clearly)"
    )

    # Open text — what the student found meaningful
    favourite_thing = models.TextField(
        blank=True,
        help_text="What was your favourite thing you learned this term?"
    )
    want_to_learn_more = models.TextField(
        blank=True,
        help_text="What would you love to learn more about?"
    )
    suggestion = models.TextField(
        blank=True,
        help_text="One thing that would make this subject even better for you?"
    )

    submitted_at = models.DateTimeField(auto_now_add=True)
    is_draft = models.BooleanField(default=False)

    class Meta:
        unique_together = ['student', 'semester', 'assignment']

    def __str__(self):
        return f"Review by {self.student} for {self.assignment.subject} ({self.semester})"

    @property
    def average_rating(self):
        scores = [
            self.lesson_enjoyment, self.understanding,
            self.teacher_explains_well, self.teacher_encourages,
            self.real_world_connection
        ]
        return round(sum(scores) / len(scores), 1)


class SoftSkillRating(models.Model):
    """Student rates themselves on the values Sean cares about."""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    student = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='softskill_ratings'
    )
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='softskill_ratings')
    soft_skill = models.ForeignKey(
        'curriculum.SoftSkill', on_delete=models.CASCADE, related_name='ratings'
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    reflection = models.TextField(
        blank=True,
        help_text="How did you practise this skill this term?"
    )

    class Meta:
        unique_together = ['student', 'semester', 'soft_skill']

    def __str__(self):
        return f"{self.student} - {self.soft_skill} ({self.semester})"


class TeacherSelfAssessment(models.Model):
    """Teacher reflects on their own teaching each term."""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    teacher = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='self_assessments'
    )
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='teacher_assessments')
    classroom = models.ForeignKey('schools.ClassRoom', on_delete=models.CASCADE)
    subject = models.ForeignKey('curriculum.Subject', on_delete=models.CASCADE)

    coverage = models.IntegerField(choices=RATING_CHOICES, help_text="How much of the syllabus did you cover?")
    student_engagement = models.IntegerField(choices=RATING_CHOICES, help_text="How engaged were students?")
    values_integration = models.IntegerField(choices=RATING_CHOICES, help_text="How well did you integrate life values?")

    highlights = models.TextField(blank=True, help_text="What went really well this term?")
    challenges = models.TextField(blank=True, help_text="What was challenging?")
    next_term_goals = models.TextField(blank=True, help_text="What will you do differently next term?")

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['teacher', 'semester', 'classroom', 'subject']

    def __str__(self):
        return f"{self.teacher} self-assessment: {self.subject} ({self.semester})"


class ParentAcknowledgement(models.Model):
    """Parent views and acknowledges their child's review report."""
    parent = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='acknowledgements'
    )
    student = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='parent_acknowledgements'
    )
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    acknowledged_at = models.DateTimeField(auto_now_add=True)
    parent_comment = models.TextField(blank=True)

    class Meta:
        unique_together = ['parent', 'student', 'semester']
