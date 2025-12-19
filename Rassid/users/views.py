from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import User
from airports.models import Airport, AirportUser

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password): 
                request.session['user_id'] = user.id
                request.session['role'] = user.role
                
                if user.role == 'platform_admin':
                    messages.success(request, 'Logged in successfully as Platform Admin.')
                    return redirect('platform_admin_dashboard')
                elif user.role == 'admin':
                    messages.success(request, 'Logged in successfully as Airport Admin.')
                    return redirect('airport_admin_dashboard')
                elif user.role == 'operator':
                    messages.success(request, 'Logged in successfully as Operator.')
                    return redirect('operator_dashboard')
            else:
                messages.error(request, 'Invalid password')
        except User.DoesNotExist:
            messages.error(request, 'User not found')
            
    return render(request, 'users/login.html')

def logout_view(request):
    request.session.flush()
    return redirect('home')

def signup_request(request):
    if request.method == 'POST':
        airport_id = request.POST.get('airport_id') 
        admin_name = request.POST.get('admin_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('signup_request')

        try:
            airport = Airport.objects.get(id=airport_id)
            
            user = User.objects.create(
                email=email,
                password=make_password(password),
                role='admin',
                active=False,
                airportId=airport.id
            )
            
            AirportUser.objects.create(
                name=admin_name,
                email=email,
                role='admin',
                airport=airport
            )
            
            messages.success(request, 'Account request submitted! Please wait for Platform Admin approval.')
            return redirect('login')
            
        except Airport.DoesNotExist:
            messages.error(request, "Invalid Airport selected.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    airports = Airport.objects.all().order_by('name')
    return render(request, 'users/signup.html', {'airports': airports})

def create_operator(request):
    if request.session.get('role') != 'admin':
        return redirect('home')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Operator email already exists.")
            return redirect('airport_admin_dashboard')
        
        current_user_id = request.session.get('user_id')
        current_admin = User.objects.get(id=current_user_id)
        
        try:
            airport = Airport.objects.get(id=current_admin.airportId)
            
            operator_user = User.objects.create(
                email=email,
                password=make_password(password),
                role='operator',
                active=True,
                airportId=airport.id
            )
            
            AirportUser.objects.create(
                name=name,
                email=email,
                role='operator',
                airport=airport
            )
        
            messages.success(request, f'Operator {name} created successfully.')
            
        except Exception as e:
            messages.error(request, f"Error creating operator: {e}")
            
        return redirect('airport_admin_dashboard')
        
    return redirect('airport_admin_dashboard')

def delete_operator(request, operator_id):
    if request.session.get('role') != 'admin':
        return redirect('home')
        
    try:
        operator = User.objects.get(id=operator_id)
        current_admin_id = request.session.get('user_id')
        current_admin = User.objects.get(id=current_admin_id)
        
        if operator.airportId == current_admin.airportId and operator.role == 'operator':
            operator.delete()
            messages.success(request, 'Operator deleted successfully.')
        else:
            messages.error(request, 'Unauthorized action.')
            
    except User.DoesNotExist:
        messages.error(request, 'Operator not found.')
        
    return redirect('airport_admin_dashboard')
