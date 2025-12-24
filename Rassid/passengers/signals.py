from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from flights.models import FlightStatusHistory, GateAssignment
from passengers.models import PassengerFlight

def send_update_email_to_passengers(flight, title_en, desc_en, title_ar, desc_ar):
    bookings = PassengerFlight.objects.filter(flight=flight).select_related('passenger')
    
    for booking in bookings:
        passenger = booking.passenger
        lang = passenger.preferredLanguage
        
        token = booking.access_token
        # Hardcoding domain for now as we don't have request object in signal
        # Ideally use sites framework or settings.SITE_URL
        tracking_url = f"http://127.0.0.1:8000/passengers/track/booking/{token}/"
        
        if lang == 'ar':
            subject = f"تحديث الرحلة {flight.flightNumber}"
            template = 'emails/flight_update_ar.html'
            context = {
                'passenger_name': passenger.fullName,
                'flight_number': flight.flightNumber,
                'update_title': title_ar,
                'update_description': desc_ar,
                'tracking_url': tracking_url
            }
        else:
            subject = f"Flight Update {flight.flightNumber}"
            template = 'emails/flight_update_en.html'
            context = {
                'passenger_name': passenger.fullName,
                'flight_number': flight.flightNumber,
                'update_title': title_en,
                'update_description': desc_en,
                'tracking_url': tracking_url
            }

        html_message = render_to_string(template, context)
        plain_message = strip_tags(html_message)
        
        try:
            print(f"Sending email to {passenger.email}...")
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [passenger.email],
                html_message=html_message,
                fail_silently=False
            )
            print("Email sent.")
        except Exception as e:
            print(f"Failed to send email to {passenger.email}: {e}")

@receiver(post_save, sender=FlightStatusHistory)
def flight_status_changed(sender, instance, created, **kwargs):
    if created:
        flight = instance.flight
        # Example Statuses: scheduled, boarding, departed, delayed, cancelled
        
        new_status = instance.newStatus.lower()
        
        if new_status == 'boarding':
            send_update_email_to_passengers(
                flight,
                title_en="Boarding Now Open",
                desc_en=f"Boarding for flight {flight.flightNumber} is now open. Please proceed to your gate.",
                title_ar="بدء صعود الطائرة",
                desc_ar=f"بدأ صعود الطائرة للرحلة {flight.flightNumber}. يرجى التوجه إلى البوابة."
            )
        elif new_status == 'cancelled':
             send_update_email_to_passengers(
                flight,
                title_en="Flight Cancelled",
                desc_en=f"We regret to inform you that flight {flight.flightNumber} has been cancelled. Please contact support.",
                title_ar="تم إلغاء الرحلة",
                desc_ar=f"نأسف لإبلاغكم بإلغاء الرحلة {flight.flightNumber}. يرجى التواصل مع الدعم."
            )
        else:
            # Generic Update
            send_update_email_to_passengers(
                flight,
                title_en=f"Status Changed to {instance.newStatus}",
                desc_en=f"The flight status has been updated to {instance.newStatus}.",
                title_ar=f"تغيرت الحالة إلى {instance.newStatus}",
                desc_ar=f"تم تحديث حالة الرحلة إلى {instance.newStatus}."
            )

@receiver(post_save, sender=GateAssignment)
def gate_assigned(sender, instance, created, **kwargs):
    # This signal triggers on create OR update (save)
    flight = instance.flight
    
    boarding_time = instance.boardingOpenTime
    if hasattr(boarding_time, 'strftime'):
        boarding_time_str = boarding_time.strftime('%H:%M')
    else:
        boarding_time_str = str(boarding_time).split('T')[-1][:5]

    send_update_email_to_passengers(
        flight,
        title_en=f"Gate Information Updated",
        desc_en=f"Gate: {instance.gateCode}, Terminal: {instance.terminal}. Boarding at {boarding_time_str}.",
        title_ar=f"تحديث معلومات البوابة",
        desc_ar=f"البوابة: {instance.gateCode}، الصالة: {instance.terminal}. الصعود في {boarding_time_str}."
    )

@receiver(post_save, sender=PassengerFlight)
def booking_created(sender, instance, created, **kwargs):
    if created:
        passenger = instance.passenger
        flight = instance.flight
        lang = passenger.preferredLanguage
        
        token = instance.access_token
        tracking_link = f"http://127.0.0.1:8000/passengers/track/booking/{token}/"
        
        try:
            boarding_time = flight.scheduledDeparture.strftime('%H:%M')
        except:
            boarding_time = str(flight.scheduledDeparture)

        if lang == 'ar':
            subject = "تأكيد الحجز - راصد"
            template = 'emails/booking_confirmation_ar.html'
            context = {
                'passenger_name': passenger.fullName,
                'flight_number': flight.flightNumber,
                'origin': flight.origin.code,
                'destination': flight.destination.code,
                'departure_time': boarding_time,
                'tracking_link': tracking_link
            }
        else:
            subject = "Booking Confirmation - Rassid"
            template = 'emails/booking_confirmation_en.html'
            context = {
                'passenger_name': passenger.fullName,
                'flight_number': flight.flightNumber,
                'origin': flight.origin.code,
                'destination': flight.destination.code,
                'departure_time': boarding_time,
                'tracking_link': tracking_link
            }

        html_message = render_to_string(template, context)
        plain_message = strip_tags(html_message)
        
        try:
            print(f"Sending booking confirmation to {passenger.email}...")
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [passenger.email],
                html_message=html_message,
                fail_silently=False
            )
            print("Booking email sent.")
        except Exception as e:
            print(f"Failed to send booking email to {passenger.email}: {e}")
