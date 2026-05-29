from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_STUDENT = 'student'
    ROLE_TEACHER = 'teacher'
    ROLE_PARENT = 'parent'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_TEACHER, 'Teacher'),
        (ROLE_PARENT, 'Parent'),
        (ROLE_ADMIN, 'School Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    school = models.ForeignKey(
        'schools.School', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='users'
    )
    phone = models.CharField(max_length=20, blank=True)

    @property
    def is_student(self): return self.role == self.ROLE_STUDENT
    @property
    def is_teacher(self): return self.role == self.ROLE_TEACHER
    @property
    def is_parent(self): return self.role == self.ROLE_PARENT
    @property
    def is_school_admin(self): return self.role == self.ROLE_ADMIN

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
