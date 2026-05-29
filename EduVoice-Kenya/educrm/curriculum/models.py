from django.db import models


class Subject(models.Model):
    LEVEL_PRIMARY = 'primary'
    LEVEL_JUNIOR = 'junior'
    LEVEL_CHOICES = [
        (LEVEL_PRIMARY, 'Primary (Grades 1-6)'),
        (LEVEL_JUNIOR, 'Junior School (Grades 7-9)'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='📚')  # emoji icon
    is_core = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['level', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"


class SoftSkill(models.Model):
    """The values-based skills Sean wants to track — curiosity, reading, etc."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=10, default='⭐')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
