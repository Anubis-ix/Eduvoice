#!/usr/bin/env python
"""
Seed script: run with  python manage.py shell < seed.py
Or:  python seed.py  (from project root with DJANGO_SETTINGS_MODULE set)
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone
from datetime import date
from accounts.models import User
from schools.models import School, ClassRoom, Enrollment, TeacherAssignment, ParentStudentLink
from curriculum.models import Subject, SoftSkill
from reviews.models import Semester

print("🌱 Seeding EduVoice Kenya...")

# ── SCHOOLS ──────────────────────────────────────────────────────────────────
school, _ = School.objects.get_or_create(
    code='NRB001',
    defaults={
        'name': 'Nairobi Academy Primary School',
        'county': 'Nairobi',
        'sub_county': 'Westlands',
        'subscription_plan': 'pro',
        'is_active': True,
    }
)
school2, _ = School.objects.get_or_create(
    code='KSM001',
    defaults={
        'name': 'Kisumu Model School',
        'county': 'Kisumu',
        'subscription_plan': 'basic',
        'is_active': True,
    }
)
print(f"  ✓ Schools: {school.name}, {school2.name}")

# ── CBC SUBJECTS ─────────────────────────────────────────────────────────────
primary_subjects = [
    ('English Language Activities', 'ENG-P', '📖', True),
    ('Kiswahili Language Activities', 'KIS-P', '🗣️', True),
    ('Mathematics', 'MATH-P', '🔢', True),
    ('Environmental Activities', 'ENV-P', '🌿', True),
    ('Creative Activities', 'CRE-P', '🎨', True),
    ('Religious Education Activities', 'REL-P', '🙏', False),
    ('Science & Technology', 'SCI-P', '🔬', True),
    ('Agriculture', 'AGR-P', '🌱', False),
    ('Social Studies', 'SOC-P', '🌍', True),
    ('Home Science', 'HOME-P', '🏠', False),
    ('Physical Education', 'PE-P', '⚽', True),
]

junior_subjects = [
    ('English', 'ENG-J', '📖', True),
    ('Kiswahili / Kenya Sign Language', 'KIS-J', '🗣️', True),
    ('Mathematics', 'MATH-J', '🔢', True),
    ('Integrated Science', 'ISCI-J', '🔬', True),
    ('Pre-Technical Studies', 'TECH-J', '🔧', True),
    ('Social Studies', 'SOC-J', '🌍', True),
    ('Religious Education', 'REL-J', '🙏', False),
    ('Agriculture', 'AGR-J', '🌱', False),
    ('Creative Arts & Sports', 'ARTS-J', '🎨', True),
    ('Business Studies', 'BUS-J', '💼', False),
    ('Health Education', 'HEALTH-J', '❤️', True),
]

for name, code, icon, is_core in primary_subjects:
    Subject.objects.get_or_create(
        code=code,
        defaults={'name': name, 'level': 'primary', 'icon': icon, 'is_core': is_core}
    )

for name, code, icon, is_core in junior_subjects:
    Subject.objects.get_or_create(
        code=code,
        defaults={'name': name, 'level': 'junior', 'icon': icon, 'is_core': is_core}
    )

print(f"  ✓ Subjects: {Subject.objects.count()} CBC-aligned subjects seeded")

# ── SOFT SKILLS ───────────────────────────────────────────────────────────────
soft_skills_data = [
    ('Reading for Pleasure', 'reading', '📚',
     'Did you read books, stories, or articles for fun this term — not just for homework?'),
    ('Asking Why', 'curiosity', '🤔',
     'Did you ask questions when you did not understand, or when you were curious about something?'),
    ('Public Speaking', 'public_speaking', '🎤',
     'Did you practise speaking in front of others — in class, debate, or any group setting?'),
    ('Respecting Adults', 'adult_interaction', '🤝',
     'Did you practise polite, confident conversations with teachers, parents, or other adults?'),
    ('Working with Others', 'teamwork', '👥',
     'Did you work well with your classmates on group tasks or projects?'),
    ('Taking Care of the Environment', 'environment', '🌍',
     'Did you do anything to take care of your school, community, or natural environment?'),
]

for name, code, icon, description in soft_skills_data:
    SoftSkill.objects.get_or_create(
        code=code,
        defaults={'name': name, 'icon': icon, 'description': description}
    )

print(f"  ✓ Soft skills: {SoftSkill.objects.count()} seeded")

# ── USERS ─────────────────────────────────────────────────────────────────────
def make_user(username, first, last, role, school_obj, password='Pass1234!'):
    u, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': first, 'last_name': last,
            'role': role, 'school': school_obj,
            'email': f'{username}@eduvoice.ke'
        }
    )
    if created:
        u.set_password(password)
        u.save()
    return u

admin_user  = make_user('admin.nairobi', 'Admin', 'User', 'admin', school)
teacher1    = make_user('ms.wanjiku', 'Grace', 'Wanjiku', 'teacher', school)
teacher2    = make_user('mr.odhiambo', 'Peter', 'Odhiambo', 'teacher', school)
teacher3    = make_user('ms.akinyi', 'Akinyi', 'Otieno', 'teacher', school)
student1    = make_user('jane.mwangi', 'Jane', 'Mwangi', 'student', school)
student2    = make_user('brian.kamau', 'Brian', 'Kamau', 'student', school)
student3    = make_user('amina.hassan', 'Amina', 'Hassan', 'student', school)
student4    = make_user('kevin.njoroge', 'Kevin', 'Njoroge', 'student', school)
parent1     = make_user('parent.mwangi', 'Sarah', 'Mwangi', 'parent', school)
parent2     = make_user('parent.kamau', 'John', 'Kamau', 'parent', school)

# Superuser
if not User.objects.filter(username='superadmin').exists():
    User.objects.create_superuser('superadmin', 'superadmin@eduvoice.ke', 'Admin1234!', role='admin', school=school)

print(f"  ✓ Users created: admin, 3 teachers, 4 students, 2 parents, superadmin")

# ── CLASSROOMS ────────────────────────────────────────────────────────────────
grade5a, _ = ClassRoom.objects.get_or_create(
    school=school, grade=5, stream='A', academic_year=2025,
    defaults={'name': 'Grade 5A', 'class_teacher': teacher1}
)
grade7b, _ = ClassRoom.objects.get_or_create(
    school=school, grade=7, stream='B', academic_year=2025,
    defaults={'name': 'Grade 7B', 'class_teacher': teacher2}
)
print(f"  ✓ Classrooms: Grade 5A, Grade 7B")

# ── ENROLLMENTS ───────────────────────────────────────────────────────────────
for student in [student1, student2]:
    Enrollment.objects.get_or_create(student=student, classroom=grade5a)
for student in [student3, student4]:
    Enrollment.objects.get_or_create(student=student, classroom=grade7b)
print(f"  ✓ Enrollments: students assigned to classrooms")

# ── TEACHER ASSIGNMENTS ───────────────────────────────────────────────────────
math_p  = Subject.objects.get(code='MATH-P')
eng_p   = Subject.objects.get(code='ENG-P')
sci_p   = Subject.objects.get(code='SCI-P')
math_j  = Subject.objects.get(code='MATH-J')
eng_j   = Subject.objects.get(code='ENG-J')
isci_j  = Subject.objects.get(code='ISCI-J')

TeacherAssignment.objects.get_or_create(teacher=teacher1, classroom=grade5a, subject=math_p)
TeacherAssignment.objects.get_or_create(teacher=teacher1, classroom=grade5a, subject=sci_p)
TeacherAssignment.objects.get_or_create(teacher=teacher2, classroom=grade5a, subject=eng_p)
TeacherAssignment.objects.get_or_create(teacher=teacher2, classroom=grade7b, subject=eng_j)
TeacherAssignment.objects.get_or_create(teacher=teacher3, classroom=grade7b, subject=math_j)
TeacherAssignment.objects.get_or_create(teacher=teacher3, classroom=grade7b, subject=isci_j)
print(f"  ✓ Teacher assignments: 6 subject/class assignments")

# ── PARENT LINKS ──────────────────────────────────────────────────────────────
ParentStudentLink.objects.get_or_create(parent=parent1, student=student1)
ParentStudentLink.objects.get_or_create(parent=parent2, student=student2)
print(f"  ✓ Parent-student links created")

# ── SEMESTER ──────────────────────────────────────────────────────────────────
semester, _ = Semester.objects.get_or_create(
    school=school, academic_year=2025, term=2,
    defaults={
        'name': 'Term 2 — 2025',
        'start_date': date(2025, 5, 6),
        'end_date': date(2025, 7, 25),
        'review_open': True,
        'review_deadline': date(2025, 7, 30),
    }
)
print(f"  ✓ Semester: {semester.name} (reviews open: {semester.review_open})")

print()
print("✅ Seed complete! Login credentials:")
print("   Superadmin  → superadmin / Admin1234!")
print("   School admin → admin.nairobi / Pass1234!")
print("   Teacher 1   → ms.wanjiku / Pass1234!")
print("   Teacher 2   → mr.odhiambo / Pass1234!")
print("   Student 1   → jane.mwangi / Pass1234!")
print("   Student 2   → brian.kamau / Pass1234!")
print("   Student 3   → amina.hassan / Pass1234! (Grade 7B)")
print("   Parent 1    → parent.mwangi / Pass1234!")
print()
print("   Run: python manage.py runserver")
