from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = 'Creates a Platform Admin user'

    def handle(self, *args, **kwargs):
        email = input("Enter Email: ")
        password = input("Enter Password: ")
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'User with email {email} already exists.'))
            return
            
        User.objects.create(
            email=email,
            password=password,
            role='platform_admin',
            active=True
        )
        self.stdout.write(self.style.SUCCESS(f'Successfully created Platform Admin: {email}'))
