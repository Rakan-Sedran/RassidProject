from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users.models import User
from airports.models import Airport, AirportUser
from users.decorators import custom_login_required

@custom_login_required
def dashboard(request):
    # Strict Role Check via Session
    if request.session.get('role') != 'platform_admin':
        messages.error(request, "Access Denied: Restricted to Platform Super Admins.")
        return redirect('home')
        
    # Fetch Pending Requests (Enriched with Profile)
    pending_users_qs = User.objects.filter(role='admin', active=False)
    pending_users = []
    for u in pending_users_qs:
        profile = AirportUser.objects.filter(email=u.email).first()
        pending_users.append({'user': u, 'profile': profile})
    
    # Fetch Active Admins (Enriched with Profile)
    active_admins_qs = User.objects.filter(role='admin', active=True)
    active_admins = []
    for u in active_admins_qs:
        profile = AirportUser.objects.filter(email=u.email).first()
        active_admins.append({'user': u, 'profile': profile})
    
    # Fetch All Airports
    airports = Airport.objects.all()

    # Search Logic
    query = request.GET.get('q')
    if query:
        # Filter Pending
        pending_users = [item for item in pending_users if query.lower() in item['user'].email.lower() or (item['profile'] and query.lower() in item['profile'].airport.name.lower())]
        
        # Filter Active
        active_admins = [item for item in active_admins if query.lower() in item['user'].email.lower() or (item['profile'] and query.lower() in item['profile'].airport.name.lower())]
        
        # Filter Airports
        airports = airports.filter(name__icontains=query) | airports.filter(code__icontains=query)
    
    context = {
        'pending_users': pending_users,
        'active_admins': active_admins,
        'airports': airports
    }
    return render(request, 'platform_admin/dashboard.html', context)

@custom_login_required
def approve_user(request, user_id):
    if request.session.get('role') != 'platform_admin':
        return redirect('home')
        
    user = get_object_or_404(User, id=user_id)
    user.active = True
    user.save()
    messages.success(request, f"Approved airport admin: {user.email}")
    return redirect('platform_admin_dashboard')

@custom_login_required
def reject_user(request, user_id):
    if request.session.get('role') != 'platform_admin':
        return redirect('home')
        
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, f"Rejected request: {user.email}")
    return redirect('platform_admin_dashboard')
