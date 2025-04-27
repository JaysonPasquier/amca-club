import os
import stat
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Fix media directory permissions and provide diagnostic information'

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        subdirs = ['profile_images', 'banner_images', 'posts']

        self.stdout.write(f"Checking main media directory: {media_root}")
        self._check_and_print_permissions(media_root)

        # Create and check subdirectories
        for subdir in subdirs:
            path = os.path.join(media_root, subdir)
            self.stdout.write(f"Checking subdirectory: {path}")
            try:
                os.makedirs(path, exist_ok=True)
                self._check_and_print_permissions(path)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating directory {path}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("Permissions check and fixes completed."))

    def _check_and_print_permissions(self, path):
        """Check permissions on a path and print diagnostic info"""
        try:
            if os.path.exists(path):
                path_stat = os.stat(path)
                self.stdout.write(f"Path exists with permissions: {stat.filemode(path_stat.st_mode)}")
                self.stdout.write(f"Owner UID: {path_stat.st_uid}, Group GID: {path_stat.st_gid}")
                self.stdout.write(f"Current process running as UID: {os.getuid()}, GID: {os.getgid()}")

                # Try to fix permissions
                try:
                    if os.path.isdir(path):
                        os.chmod(path, 0o755)  # rwxr-xr-x
                    else:
                        os.chmod(path, 0o644)  # rw-r--r--
                    self.stdout.write(self.style.SUCCESS(f"Successfully set permissions on {path}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Cannot set permissions on {path}: {str(e)}"))
            else:
                self.stdout.write(self.style.WARNING(f"Path does not exist: {path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error checking {path}: {str(e)}"))
