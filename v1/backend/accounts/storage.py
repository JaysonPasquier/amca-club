import os
import tempfile
import shutil
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import uuid

class PermissionFileStorage(FileSystemStorage):
    """
    Custom storage class that uses a temporary file first to avoid permission issues
    """

    def _save(self, name, content):
        # Create a unique filename
        dir_name, file_name = os.path.split(name)
        extension = os.path.splitext(file_name)[1]
        unique_name = f"{uuid.uuid4().hex}{extension}"

        # Create a temporary file first
        temp_file_path = os.path.join(tempfile.gettempdir(), unique_name)

        # Save content to temp file
        with open(temp_file_path, 'wb') as temp_file:
            for chunk in content.chunks():
                temp_file.write(chunk)

        # Define the final path where the file should be saved
        if not dir_name:
            name = unique_name
        else:
            name = os.path.join(dir_name, unique_name)

        # Get location in the proper directory
        full_path = self.path(name)
        directory = os.path.dirname(full_path)

        # Make sure the directory exists
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
            return name

        # Try to move the file from temp directory to target location
        try:
            shutil.move(temp_file_path, full_path)
            print(f"Successfully moved file to {full_path}")
        except Exception as e:
            print(f"Error moving file: {e}")
            # If we can't move it, try to copy it
            try:
                shutil.copyfile(temp_file_path, full_path)
                print(f"Successfully copied file to {full_path}")
                os.remove(temp_file_path)
            except Exception as e2:
                print(f"Error copying file: {e2}")
                # Return the original name to not break the form
                return name

        return name
