from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
import base64

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

def login_tel_view(request,data):
    decoded_custom_token = base64.b64decode(data).decode("utf-8")
    parts = decoded_custom_token.split(':')

    if len(parts)!=2:
        return HttpResponseForbidden('Invalid User')
        
    user = authenticate(request, username=parts[0], password=parts[1])
    if user is not None and user.is_authenticated:
        login(request, user)
        return
    else:
        return HttpResponseForbidden('Invalid User')

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('index')

def register_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if phone_number and email and password:
            # Create new user instance
            from django.contrib.auth.models import User

            new_user = User.objects.create_user(username=phone_number, email=email, password=password)
            
            # Optionally, you can perform additional actions like login the user after signup
            # For example: login(request, new_user)
            
            messages.success(request, 'Your account has been created successfully. You can now log in.')
            print("hello")
            if new_user is not None and new_user.is_authenticated:
                from .models import Account
                acc = Account.objects.get(user=new_user)
                acc.phone_number = phone_number
                acc.save()
                login(request, new_user)
                return redirect('index')  # Redirect to the user's dashboard

            else:
                error_message = "Invalid username or password."  # Redirect to login page after successful signup
        else:
            messages.error(request, 'Please fill out all the fields.')
    return render(request, 'account/signup.html')

def register_tel_view(request):
    username = request.GET.get('phone_number')
    password = request.GET.get('chat_id')

    if username and password:
        email = username + "@dalolbingo.com"
        # Create new user instance
        from django.contrib.auth.models import User

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            input_string = username+":"+password
            encoded_bytes = base64.b64encode(input_string.encode("utf-8"))
            responseJson = {
                'token': str(encoded_bytes)
            }
            return JsonResponse(responseJson)

        new_user = User.objects.create_user(username=username, email=email, password=password)
        
        # Optionally, you can perform additional actions like login the user after signup
        # For example: login(request, new_user)
        
        messages.success(request, 'Your account has been created successfully. You can now log in.')
        if new_user is not None and new_user.is_authenticated:
            login(request, new_user)
            input_string = username+":"+password
            encoded_bytes = base64.b64encode(input_string.encode("utf-8"))
            responseJson = {
                'token': str(encoded_bytes)
            }
            return JsonResponse(responseJson)# Redirect to the user's dashboard
    responseJson = {
        'token': None
    }
    return JsonResponse(responseJson)

def custom_csrf_protect(view_func):
    """
    Decorator for views that checks the request for a custom CSRF token.
    """
    def _wrapped_view(request, *args, **kwargs):
        # Retrieve the custom token from the request
        custom_token = request.META.get('HTTP_X_CUSTOM_CSRF_TOKEN')

        if not custom_token:
            # Handle missing token
            return HttpResponseForbidden('CSRF token missing')

        # Retrieve the user based on authentication (assuming user is authenticated)
        user = request.user

        if not user.is_authenticated:
            # Handle unauthenticated users
            return HttpResponseForbidden('User is not authenticated')

        # Retrieve the expected token from the database or wherever it's stored

        decoded_custom_token = base64.b64decode(custom_token)

        parts = decoded_custom_token.split(':')

        if len(parts)!=2:
            return HttpResponseForbidden('Invalid CSRF token')
        
        check_user = authenticate(request, username=parts[0], password=parts[1])

        if check_user is None or check_user.is_authenticated is False:
            # Handle invalid token
            return HttpResponseForbidden('Invalid CSRF token')

        # Call the actual view function if the token is valid
        return view_func(request, *args, **kwargs)

    return _wrapped_view