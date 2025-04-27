import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings

class PermissionFileStorage(FileSystemStorage):
    """
    Custom storage class that avoids using temporary directories
    """

    def _save(self, name, content):
        """
        Save the file directly to the intended location
        """
        # Get full path information for debugging
        full_path = self.path(name)
        directory = os.path.dirname(full_path)

        print(f"Saving file to: {full_path}")

        # Ensure directory exists
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
        except Exception as e:
            print(f"Error creating directory: {e}")

        # Use the parent class's save functionality
        try:
            return super()._save(name, content)
        except Exception as e:
            print(f"Error in _save: {e}")
            return name
