from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from user.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user_queryset = User.objects

        username = settings.ADMIN_USERNAME
        email = settings.ADMIN_EMAIL
        password = settings.ADMIN_PASSWORD

        try:
            self.stdout.write(f'Creating account for {username} {email}')
            admin = user_queryset.create_superuser(email=email, username=username, password=password)
            admin.is_active = True
            admin.is_superuser = True
        except IntegrityError:
            self.stdout.write('Admin account with such credentials already exists')
        else:
            admin.save()
            self.stdout.write('Created successfully')
