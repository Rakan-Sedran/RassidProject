from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse

def login_view(request):
    if request.user.is_authenticated:
        return redirect_user_based_on_role(request.user)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect_user_based_on_role(user)
            else:
                messages.error(request, "This account is inactive.")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('users:login')

def redirect_user_based_on_role(user):
    if user.role == 'superadmin':
        return redirect('public_home')

    elif user.role == 'airport_admin':
        return redirect('public_home') 

    elif user.role == 'operator':
        return redirect('operator_dashboard')

    else:
        return redirect('public_home')