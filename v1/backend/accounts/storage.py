import os
import stat
from django.core.files.storage import FileSystemStorage
from django.conf import settings

class PermissionFileStorage(FileSystemStorage):
    """
    Custom storage class with enhanced debugging for permission issues.
    """

    def _save(self, name, content):
        # Print diagnostic information
        full_path = self.path(name)
        directory = os.path.dirname(full_path)

        print(f"Attempting to save file to: {full_path}")
        print(f"Directory path: {directory}")

        # Check if directory exists and print permissions
        if os.path.exists(directory):
            dir_stat = os.stat(directory)
            print(f"Directory exists with permissions: {stat.filemode(dir_stat.st_mode)}")
            print(f"Directory owner: {dir_stat.st_uid}, group: {dir_stat.st_gid}")
            print(f"Process running as user: {os.getuid()}, group: {os.getgid()}")
        else:
            print(f"Directory does not exist: {directory}")

        # Try to create directory if it doesn't exist
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Directory created/checked: {directory}")
        except Exception as e:
            print(f"Error creating directory: {str(e)}")

        # Attempt to save the file with error catching
        try:
            file_name = super()._save(name, content)
            print(f"File saved successfully as: {file_name}")
            return file_name
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            # Return original name to prevent form from breaking
            return name
