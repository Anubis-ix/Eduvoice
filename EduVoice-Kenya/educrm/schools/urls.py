from django.urls import path
from . import views
urlpatterns = [
    path('', views.school_list, name='school_list'),
]
