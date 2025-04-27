import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings

class PermissionFileStorage(FileSystemStorage):
    """
    Custom storage class that ensures proper permissions when saving files.
    """

    def _save(self, name, content):
        # Use parent class to save the file
        file_name = super()._save(name, content)

        # Get full path of saved file
        full_path = self.path(file_name)

        # Ensure proper permissions are set
        try:
            # Set permissions for the file itself
            os.chmod(full_path, settings.FILE_UPLOAD_PERMISSIONS)

            # Set permissions for the directory
            directory = os.path.dirname(full_path)
            os.chmod(directory, settings.FILE_UPLOAD_DIRECTORY_PERMISSIONS)
        except Exception as e:
            print(f"Warning: Could not set permissions: {str(e)}")

        return file_name
