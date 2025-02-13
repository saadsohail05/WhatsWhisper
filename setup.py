import os
import subprocess
import sys
import platform

def check_system_dependencies():
    print("📦 Checking system dependencies...")
    if platform.system() == "Linux":
        try:
            subprocess.check_call(["sudo", "apt-get", "update"])
            subprocess.check_call(["sudo", "apt-get", "install", "-y", "libsndfile1"])
        except subprocess.CalledProcessError:
            print("❌ Failed to install system dependencies")
            print("Please manually install libsndfile1 using: sudo apt-get install libsndfile1")
            sys.exit(1)

def check_python_dependencies():
    print("📦 Checking Python dependencies...")
    try:
        # Install PyTorch and related packages first
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "torch", "torchaudio", "torchvision",
            "--index-url", "https://download.pytorch.org/whl/cpu"
        ])
        # Install remaining dependencies
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
    check_system_dependencies()
    check_python_dependencies()
    check_node_dependencies()
    create_directories()
    print("✅ Setup complete! Run 'python server.py' and 'node whatsapp-bot.js' to start")
