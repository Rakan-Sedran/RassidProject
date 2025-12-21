import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Rassid.settings')
django.setup()

from airports.models import Airport, SubscriptionRequest
from django.contrib.auth import get_user_model

User = get_user_model()

def fix_zombie_airports():
    print("--- ZOMBIE CLEANUP STARTED ---")
    requests = SubscriptionRequest.objects.filter(status='pending')

    for req in requests:
        print(f"Checking Request: {req.airport_name} ({req.airport_code})")


        try:
            airport = Airport.objects.get(code=req.airport_code)
            print(f"   [!] Conflict: Airport '{airport.name}' ({airport.code}) exists. ID: {airport.id}")
            airport.delete()
            print("   -> DELETED conflicting Airport.")
        except Airport.DoesNotExist:
            print("   [OK] No airport conflict.")

        try:
            user = User.objects.get(email=req.admin_email)
            print(f"   [!] Conflict: User '{user.email}' exists. ID: {user.id}")
            user.delete()
            print("   -> DELETED conflicting User.")
        except User.DoesNotExist:
            print("   [OK] No user conflict.")

        print("   Status: CLEAN for approval.\n")

    print("--- ZOMBIE CLEANUP FINISHED ---")


if __name__ == "__main__":
    fix_zombie_airports()