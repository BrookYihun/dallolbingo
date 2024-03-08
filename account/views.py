from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib import messages

from account.models import Account

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_authenticated:
            login(request, user)
            return redirect('index')  # Redirect to the user's dashboard

        else:
            error_message = "Invalid username or password."
    else:
        error_message = None

    return render(request, 'account/login.html', {'error_message': error_message})

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('index')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if username and email and password:
            # Create new user instance
            new_user = User.objects.create_user(username=username, email=email, password=password)
            
            # Optionally, you can perform additional actions like login the user after signup
            # For example: login(request, new_user)
            
            messages.success(request, 'Your account has been created successfully. You can now log in.')
            if new_user is not None and new_user.is_authenticated:
                login(request, new_user)
                return redirect('index')  # Redirect to the user's dashboard

            else:
                error_message = "Invalid username or password."  # Redirect to login page after successful signup
        else:
            messages.error(request, 'Please fill out all the fields.')
    return render(request, 'account/signup.html')
