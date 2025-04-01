"""
WSGI config for amca project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amca.settings')

application = get_wsgi_application()
