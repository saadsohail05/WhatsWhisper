import os
import subprocess
import sys
import platform

def check_system_dependencies():
    print("📦 Checking system dependencies...")
    if platform.system() == "Linux":
        try:
            subprocess.check_call(["sudo", "apt-get", "update"])
            # Added ffmpeg for audio processing
            subprocess.check_call(["sudo", "apt-get", "install", "-y", "libsndfile1", "ffmpeg"])
        except subprocess.CalledProcessError:
            print("❌ Failed to install system dependencies")
            print("Please manually install required packages using:")
            print("sudo apt-get install libsndfile1 ffmpeg")
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
    directories = ['uploads', 'tokens', 'models']
    for dir in directories:
        os.makedirs(dir, exist_ok=True)

def check_credentials():
    print("🔑 Checking for required credentials...")
    required_files = ['credentials.json', '.env']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("❌ Missing credential files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure you have:")
        print("1. credentials.json for Google Calendar API")
        print("2. .env file with OPENROUTER_API_KEY for Phi-3.5 and Groq Key For Whisper API")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Setting up WhatsApp Voice Transcription Bot...")
    check_system_dependencies()
    check_python_dependencies()
    check_node_dependencies()
    create_directories()
    check_credentials()
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Run 'python server.py' in one terminal")
    print("2. Run 'node whatsapp-bot.js' in another terminal")
    print("3. Scan the QR code with WhatsApp to connect")
