import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Rassid.settings')
django.setup()

from airports.models import Airport, SubscriptionRequest
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

def check_system_state():
    print("--- DIAGNOSTIC START ---")
    
    # Check Pending Requests
    requests = SubscriptionRequest.objects.filter(status='pending')
    print(f"Pending Requests: {requests.count()}")
    
    for req in requests:
        print(f"\nRequest ID: {req.id}")
        print(f"Airport Name: {req.airport_name}")
        print(f"Airport Code: {req.airport_code}")
        print(f"Admin Email: {req.admin_email}")
        
        # Check if Airport exists
        airport_exists = Airport.objects.filter(code=req.airport_code).exists()
        print(f"-> Airport with code '{req.airport_code}' exists? {airport_exists}")
        
        if airport_exists:
            existing_airport = Airport.objects.get(code=req.airport_code)
            print(f"   Existing Airport ID: {existing_airport.id}")
            print(f"   Created At: {existing_airport.created_at}")
            
        # Check if User exists
        user_exists = User.objects.filter(email=req.admin_email).exists()
        print(f"-> User with email '{req.admin_email}' exists? {user_exists}")

    # Test Email Cfg
    print("\n--- EMAIL TEST ---")
    try:
        print(f"Sending test email from {settings.DEFAULT_FROM_EMAIL}...")
        # valid_email = requests.first().admin_email if requests.exists() else 'test@example.com'
        # just dry run
        # send_mail('Test', 'Test', settings.DEFAULT_FROM_EMAIL, [valid_email], fail_silently=False)
        print("Skipping actual send to avoid spam, but config looks loaded.")
        print(f"Host: {settings.EMAIL_HOST}")
        print(f"Port: {settings.EMAIL_PORT}")
        print(f"User: {settings.EMAIL_HOST_USER}")
    except Exception as e:
        print(f"Email Config Error: {e}")

    print("--- DIAGNOSTIC END ---")

if __name__ == "__main__":
    check_system_state()