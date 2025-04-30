#!/bin/bash

project_path = '/home/scorpio/personall-website/amca/v1/backend'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

print(f"Clean Python Path: {sys.path}")
EOF

# Check if core/urls.py exists, if not create it
if [ ! -f "/home/scorpio/personall-website/amca/v1/backend/core/urls.py" ]; then
    echo "Creating core/urls.py..."
    mkdir -p "/home/scorpio/personall-website/amca/v1/backend/core"
    cat > "/home/scorpio/personall-website/amca/v1/backend/core/urls.py" << 'EOF'
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/toggle-participation/', views.toggle_event_participation, name='toggle_event_participation'),
    path('social/', views.social_links, name='social_links'),
]
EOF
fi

# Set essential environment variables
export PYTHONPATH="/home/scorpio/personall-website/amca/v1/backend"
export PYTHONSTARTUP="/tmp/clean_path.py"
export DJANGO_SETTINGS_MODULE="amca.settings"

# Use the -c option to execute Python code that imports the path cleaner first
python3 -c "
import sys
sys.path = [p for p in sys.path if 'holberton-hub' not in p]
sys.path.insert(0, '/home/scorpio/personall-website/amca/v1/backend')

from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py'] + sys.argv[1:])
" "$@"