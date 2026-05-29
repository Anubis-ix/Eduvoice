from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from schools.models import School


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    schools = School.objects.filter(is_active=True)
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        school_id = request.POST.get('school')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'accounts/register.html', {'schools': schools})

        school = School.objects.filter(id=school_id).first()
        user = User.objects.create_user(
            username=username, first_name=first_name, last_name=last_name,
            email=email, password=password, role=role, school=school
        )
        login(request, user)
        messages.success(request, f'Welcome, {user.get_full_name()}!')
        return redirect('dashboard')
    return render(request, 'accounts/register.html', {'schools': schools})


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})
