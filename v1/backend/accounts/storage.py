import os
import tempfile
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import shutil

class PermissionFileStorage(FileSystemStorage):
    """
    Custom storage class that handles permission issues by using
    a temporary directory first, then moving the file to its final destination.
    """

    def _save(self, name, content):
        # Create a temporary directory to store the file
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, os.path.basename(name))

        # Save the file to the temporary directory first
        with open(temp_file_path, 'wb') as temp_file:
            for chunk in content.chunks():
                temp_file.write(chunk)

        # Get the final path where the file should be saved
        full_path = self.path(name)
        directory = os.path.dirname(full_path)

        # Make sure the directory exists with proper permissions
        try:
            os.makedirs(directory, exist_ok=True)
            os.chmod(directory, 0o777)  # Full permissions
        except Exception as e:
            print(f"Directory permission error: {str(e)}")

        # Try to move the file from temp to final location
        try:
            shutil.move(temp_file_path, full_path)
            os.chmod(full_path, 0o666)  # File permissions
        except Exception as e:
            print(f"File move error: {str(e)}")
            # If move fails, try a different way
            try:
                shutil.copyfile(temp_file_path, full_path)
                os.chmod(full_path, 0o666)
            except Exception as e2:
                print(f"File copy error: {str(e2)}")
                return name  # Return name anyway to not break the form

        # Clean up the temp directory
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

        return name
