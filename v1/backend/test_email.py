#!/usr/bin/env python
"""
Test script to verify email sending functionality.
Run this directly on the server to debug email issues.
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amca.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email(recipient_email):
    """Test sending an email"""
    print(f"Testing email sending to {recipient_email}")
    print(f"Email settings:")
    print(f"  HOST: {settings.EMAIL_HOST}")
    print(f"  PORT: {settings.EMAIL_PORT}")
    print(f"  USER: {settings.EMAIL_HOST_USER}")
    print(f"  TLS: {settings.EMAIL_USE_TLS}")

    try:
        print("Attempting to send email...")
        result = send_mail(
            'Test Email from AMC-F.COM',
            'This is a test email to verify SMTP configuration.',
            'contact@amc-f.com',
            [recipient_email],
            fail_silently=False,
        )
        print(f"Email sent successfully! Result: {result}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        print("Full exception details:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        recipient = sys.argv[1]
    else:
        recipient = input("Enter recipient email address: ")

    test_email(recipient)
