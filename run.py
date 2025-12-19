import subprocess
import os
import signal
import sys

def signal_handler(sig, frame):
    print("Exiting...")
    backend.terminate()
    frontend.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

print("Starting Backend...")
# Start Backend in background
backend = subprocess.Popen(["uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"])

print("Starting Frontend...")
# Start Frontend in foreground
# DigitalOcean provides PORT env var, usually 8080
port = os.environ.get("PORT", "8080")
frontend = subprocess.Popen([
    "streamlit", "run", "frontend/app.py", 
    "--server.port", port, 
    "--server.address", "0.0.0.0",
    "--server.headless", "true"
])

# Wait for frontend (since it's the main UI)
frontend.wait()
backend.terminate()
