from django import forms
from .models import Review, SoftSkillRating, TeacherSelfAssessment

RATING_LABELS = {1: '😞 1', 2: '😕 2', 3: '😐 3', 4: '🙂 4', 5: '😄 5'}
RATING_WIDGET_CHOICES = [(i, RATING_LABELS[i]) for i in range(1, 6)]

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            'lesson_enjoyment', 'understanding', 'teacher_explains_well',
            'teacher_encourages', 'real_world_connection',
            'favourite_thing', 'want_to_learn_more', 'suggestion'
        ]
        widgets = {
            'lesson_enjoyment': forms.RadioSelect(choices=RATING_WIDGET_CHOICES),
            'understanding': forms.RadioSelect(choices=RATING_WIDGET_CHOICES),
            'teacher_explains_well': forms.RadioSelect(choices=RATING_WIDGET_CHOICES),
            'teacher_encourages': forms.RadioSelect(choices=RATING_WIDGET_CHOICES),
            'real_world_connection': forms.RadioSelect(choices=RATING_WIDGET_CHOICES),
            'favourite_thing': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Something cool you learned...'}),
            'want_to_learn_more': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What made you curious?'}),
            'suggestion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'One idea to make lessons better...'}),
        }

class SoftSkillRatingForm(forms.ModelForm):
    class Meta:
        model = SoftSkillRating
        fields = ['rating', 'reflection']
        widgets = {
            'rating': forms.RadioSelect(choices=RATING_WIDGET_CHOICES),
            'reflection': forms.Textarea(attrs={'rows': 2, 'placeholder': 'How did you practise this?'}),
        }

class TeacherSelfAssessmentForm(forms.ModelForm):
    class Meta:
        model = TeacherSelfAssessment
        fields = ['coverage', 'student_engagement', 'values_integration', 'highlights', 'challenges', 'next_term_goals']
        widgets = {
            'coverage': forms.RadioSelect(choices=RATING_WIDGET_CHOICES),
            'student_engagement': forms.RadioSelect(choices=RATING_WIDGET_CHOICES),
            'values_integration': forms.RadioSelect(choices=RATING_WIDGET_CHOICES),
            'highlights': forms.Textarea(attrs={'rows': 3}),
            'challenges': forms.Textarea(attrs={'rows': 3}),
            'next_term_goals': forms.Textarea(attrs={'rows': 3}),
        }
