"""ASGI config for caminhos_rosa project."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "caminhos_rosa.settings")

application = get_asgi_application()
