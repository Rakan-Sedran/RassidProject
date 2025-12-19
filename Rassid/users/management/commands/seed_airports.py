from django.core.management.base import BaseCommand
from flights.services.flights_api import fetch_airports, save_airports_to_db

class Command(BaseCommand):
    help = 'Seeds database with airports from AviationStack API'

    def handle(self, *args, **kwargs):


        gcc_airports = [
            # Saudi Arabia
            {'name': 'King Khalid International', 'code': 'RUH', 'city': 'Riyadh', 'country': 'Saudi Arabia'},
            {'name': 'King Abdulaziz International', 'code': 'JED', 'city': 'Jeddah', 'country': 'Saudi Arabia'},
            {'name': 'King Fahd International', 'code': 'DMM', 'city': 'Dammam', 'country': 'Saudi Arabia'},
            {'name': 'Prince Mohammad Bin Abdulaziz', 'code': 'MED', 'city': 'Madinah', 'country': 'Saudi Arabia'},
            {'name': 'Abha International', 'code': 'AHB', 'city': 'Abha', 'country': 'Saudi Arabia'},
            {'name': 'Taif International', 'code': 'TIF', 'city': 'Taif', 'country': 'Saudi Arabia'},
            # UAE
            {'name': 'Dubai International', 'code': 'DXB', 'city': 'Dubai', 'country': 'United Arab Emirates'},
            {'name': 'Abu Dhabi International', 'code': 'AUH', 'city': 'Abu Dhabi', 'country': 'United Arab Emirates'},
            {'name': 'Sharjah International', 'code': 'SHJ', 'city': 'Sharjah', 'country': 'United Arab Emirates'},
            # Qatar
            {'name': 'Hamad International', 'code': 'DOH', 'city': 'Doha', 'country': 'Qatar'},
            # Kuwait
            {'name': 'Kuwait International', 'code': 'KWI', 'city': 'Kuwait City', 'country': 'Kuwait'},
            # Bahrain
            {'name': 'Bahrain International', 'code': 'BAH', 'city': 'Manama', 'country': 'Bahrain'},
            # Oman
            {'name': 'Muscat International', 'code': 'MCT', 'city': 'Muscat', 'country': 'Oman'},
            {'name': 'Salalah International', 'code': 'SLL', 'city': 'Salalah', 'country': 'Oman'},
        ]

        self.stdout.write("Seeding GCC Airports (Manual Fallback due to API Restriction)...")
        
        from flights.models import Airport
        
        for item in gcc_airports:
            Airport.objects.update_or_create(
                code=item['code'],
                defaults={
                    'name': item['name'],
                    'city': item['city'],
                    'country': item['country']
                }
            )
            
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(gcc_airports)} GCC Airports.'))
