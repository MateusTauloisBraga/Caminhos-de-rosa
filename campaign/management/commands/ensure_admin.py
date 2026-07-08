from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update the admin user from environment variables."

    def handle(self, *args, **options):
        if not settings.ADMIN_PASSWORD:
            raise CommandError("ADMIN_PASSWORD is empty. Set it in .env before running this command.")

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=settings.ADMIN_USERNAME,
            defaults={"email": settings.ADMIN_EMAIL},
        )
        user.email = settings.ADMIN_EMAIL
        user.is_staff = True
        user.is_superuser = True
        user.set_password(settings.ADMIN_PASSWORD)
        user.save()

        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"Admin user {settings.ADMIN_USERNAME!r} {action}."))
