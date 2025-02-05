import os
import subprocess
import sys

def check_python_dependencies():
    print("📦 Checking Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        sys.exit(1)

def check_node_dependencies():
    print("📦 Checking Node.js dependencies...")
    try:
        subprocess.check_call(["npm", "install"])
    except subprocess.CalledProcessError:
        print("❌ Failed to install Node.js dependencies")
        sys.exit(1)

def create_directories():
    print("📁 Creating required directories...")
    directories = ['uploads', 'tokens']
    for dir in directories:
        os.makedirs(dir, exist_ok=True)

if __name__ == "__main__":
    print("🚀 Setting up WhatsApp Voice Transcription Bot...")
    check_python_dependencies()
    check_node_dependencies()
    create_directories()
    print("✅ Setup complete! Run 'python server.py' and 'node whatsapp-bot.js' to start")
