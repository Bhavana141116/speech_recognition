import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🚀 Installing Python Speech Recognition Dependencies...")
    print("=" * 50)
    
    # List of required packages
    packages = [
        "speechrecognition==3.10.0",
        "pyttsx3==2.90", 
        "openai==1.3.0",
        "python-dotenv==1.0.0",
        "pyaudio==0.2.11"
    ]
    
    # Install each package
    success_count = 0
    for package in packages:
        print(f"\n📦 Installing {package}...")
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Installation complete! {success_count}/{len(packages)} packages installed successfully.")
    
    if success_count == len(packages):
        print("\n🎉 All dependencies installed! You can now run the application with:")
        print("   python main.py")
    else:
        print("\n⚠️  Some packages failed to install. Please check the errors above.")
        print("   You may need to install them manually or check your Python environment.")
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("\n📝 Don't forget to create a .env file with your OpenAI API key:")
        print("   OPENAI_API_KEY=your_api_key_here")

if __name__ == "__main__":
    main()
