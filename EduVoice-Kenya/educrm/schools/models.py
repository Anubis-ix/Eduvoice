from django.db import models


class School(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    county = models.CharField(max_length=100)
    sub_county = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    subscription_plan = models.CharField(
        max_length=20,
        choices=[('free', 'Free'), ('basic', 'Basic'), ('pro', 'Pro')],
        default='free'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def total_students(self):
        return self.users.filter(role='student').count()

    @property
    def total_teachers(self):
        return self.users.filter(role='teacher').count()


class ClassRoom(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classrooms')
    name = models.CharField(max_length=50)  # e.g. "Grade 4A"
    grade = models.IntegerField()  # 1-9
    stream = models.CharField(max_length=10, default='A')
    academic_year = models.IntegerField()
    class_teacher = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='class_teacher_of'
    )

    class Meta:
        unique_together = ['school', 'grade', 'stream', 'academic_year']

    def __str__(self):
        return f"{self.school.name} - Grade {self.grade}{self.stream} ({self.academic_year})"

    @property
    def level(self):
        if self.grade <= 6:
            return 'primary'
        return 'junior'


class Enrollment(models.Model):
    student = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='enrollments'
    )
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['student', 'classroom']

    def __str__(self):
        return f"{self.student.get_full_name()} in {self.classroom}"


class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='assignments'
    )
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(
        'curriculum.Subject', on_delete=models.CASCADE, related_name='assignments'
    )

    class Meta:
        unique_together = ['teacher', 'classroom', 'subject']

    def __str__(self):
        return f"{self.teacher.get_full_name()} teaches {self.subject.name} in {self.classroom}"


class ParentStudentLink(models.Model):
    """Links a parent user to their child (student user)."""
    parent = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='children_links'
    )
    student = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='parent_links'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['parent', 'student']

    def __str__(self):
        return f"{self.parent.get_full_name()} → {self.student.get_full_name()}"
