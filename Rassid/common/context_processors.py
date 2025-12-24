from airports.models import SubscriptionRequest
from public.models import ContactSubmission

def pending_requests_count(request):
    if request.user.is_authenticated and request.user.is_superuser:
        count = SubscriptionRequest.objects.filter(status='pending').count()
        return {'pending_requests_count': count}
    return {}

def unresolved_messages_count(request):
    """Context processor for unresolved contact messages (super admin only)."""
    if request.user.is_authenticated and request.user.is_superuser:
        count = ContactSubmission.objects.filter(is_resolved=False).count()
        return {'unresolved_messages_count': count}
    return {}
