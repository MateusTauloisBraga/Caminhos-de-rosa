"""WSGI config for caminhos_rosa project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "caminhos_rosa.settings")

application = get_wsgi_application()
