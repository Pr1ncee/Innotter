from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
import dotenv

from user.models import User


config = dotenv.dotenv_values(".env")


class Command(BaseCommand):
    def handle(self, *args, **options):
        user_queryset = User.objects

        username = config['ADMIN_USERNAME']
        email = config['ADMIN_EMAIL']
        password = config['ADMIN_PASSWORD']

        try:
            self.stdout.write(f'Creating account for {username} {email}')
            admin = user_queryset.create_superuser(email=email, username=username, password=password)
            admin.is_active = True
            admin.is_admin = True
        except IntegrityError:
            self.stdout.write('Admin account with such credentials already exists')
        else:
            admin.save()
            self.stdout.write('Created successfully')
