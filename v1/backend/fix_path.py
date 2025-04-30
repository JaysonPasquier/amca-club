#!/usr/bin/env python3
import sys
import os
import site

# Remove holberton-hub from sys.path
filtered_path = []
for p in sys.path:
    if 'holberton-hub' not in p:
        filtered_path.append(p)
    else:
        print(f"Removing path: {p}")

sys.path = filtered_path

# Add current project path at the beginning
project_path = os.path.dirname(os.path.abspath(__file__))
if project_path not in sys.path:
    sys.path.insert(0, project_path)
    print(f"Added path: {project_path}")

# Check for site-packages
site_packages = site.getsitepackages()
for site_path in site_packages:
    # Look for .pth files that might be adding the holberton path
    pth_files = [f for f in os.listdir(site_path) if f.endswith('.pth')]
    for pth_file in pth_files:
        full_path = os.path.join(site_path, pth_file)
        try:
            with open(full_path, 'r') as f:
                content = f.read()
                if 'holberton-hub' in content:
                    print(f"Found holberton path in {full_path}")
                    print("Consider removing or commenting out the holberton path in this file")
        except:
            pass

# Print the current path for verification
print("\nCurrent Python path:")
for p in sys.path:
    print(f"- {p}")

print("\nTo permanently fix your environment:")
print("1. Add this to your .bashrc or .zshrc:")
print("   export PYTHONPATH=\"$PYTHONPATH:/home/scorpio/personall-website/amca/v1/backend\"")
print("\n2. Run Django commands with the fixed path:")
print("   PYTHONPATH=/home/scorpio/personall-website/amca/v1/backend python3 manage.py makemigrations core")

# Return true so this can be used in conditional imports
if __name__ == "__main__":
    print("\nPath has been fixed for this session.")
