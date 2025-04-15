#!/bin/bash

echo "===== Django + Ngrok Launcher ====="

# Kill any existing ngrok processes
echo "Checking for existing ngrok processes..."
if pgrep -x "ngrok" > /dev/null; then
    echo "Killing existing ngrok processes..."
    pkill -f ngrok
    sleep 2
fi

# Check for existing Django server
echo "Checking for existing Django server..."
if pgrep -f "python manage.py runserver" > /dev/null; then
    echo "Killing existing Django server..."
    pkill -f "python manage.py runserver"
    sleep 2
fi

# Change to the Django project directory
cd /amca/v1/backend || { echo "Django project directory not found"; exit 1; }

# Start Django server in the background
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Wait for Django server to start
echo "Waiting for Django server to initialize..."
sleep 3

# Check if Django server started successfully
if ! ps -p $DJANGO_PID > /dev/null; then
    echo "Django server failed to start. Exiting."
    exit 1
fi

echo "Django server running with PID: $DJANGO_PID"

# Start ngrok in the foreground
echo "Starting ngrok with sensible-horribly-raven domain..."
ngrok http --url=sensible-horribly-raven.ngrok-free.app 8000

# This will execute when the user presses Ctrl+C to stop ngrok
echo "Shutting down servers..."
kill $DJANGO_PID
echo "Django server stopped"
echo "Done!"
