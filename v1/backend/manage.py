#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Clean up problematic paths from sys.path
    sys.path = [p for p in sys.path if 'holberton-hub' not in p]

    # Set the Python path to prioritize the current project directory
    current_path = os.path.dirname(os.path.abspath(__file__))
    if current_path not in sys.path:
        sys.path.insert(0, current_path)

    # For debugging - print Python path
    print("Python path:", sys.path)

    # Check your directory structure and use the correct settings module
    if os.path.exists(os.path.join(current_path, 'amca', 'settings.py')):
        module_name = 'amca.settings'
    elif os.path.exists(os.path.join(current_path, 'amca_project', 'settings.py')):
        module_name = 'amca_project.settings'
    elif os.path.exists(os.path.join(current_path, 'project', 'settings.py')):
        module_name = 'project.settings'
    else:
        # Fall back to using the standalone settings.py file
        module_name = 'settings'

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', module_name)

    # Print which settings module we're using for debugging
    print(f"Using settings module: {module_name}")

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
