#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Change to match the actual module name in your folder structure
    # Either "amca.settings" or "amca_project.settings" based on what you have
    module_name = 'amca.settings'

    # Uncomment and replace if your project structure uses amca_project instead
    # module_name = 'amca_project.settings'

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', module_name)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
