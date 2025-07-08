"""
Setup script for the Python Speech Recognition project
"""
import os

def create_env_file():
    """Create a sample .env file"""
    env_content = """# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Speech Recognition Settings (Optional)
SPEECH_RECOGNITION_TIMEOUT=5
SPEECH_RECOGNITION_PHRASE_TIME_LIMIT=10

# Text-to-Speech Settings (Optional)
TTS_RATE=200
TTS_VOLUME=0.9
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file template")
        print("📝 Please edit .env and add your OpenAI API key")
    else:
        print("⚠️  .env file already exists")

def create_readme():
    """Create README file"""
    readme_content = """# Python Speech Recognition with AI Enhancement

A Python desktop application that combines real-time speech recognition with AI-powered text enhancement.

## Features

- 🎤 Real-time speech recognition
- 🤖 AI-powered text enhancement using OpenAI GPT-4
- 🔊 Text-to-speech for both original and enhanced text
- 🖥️ User-friendly GUI interface
- 🎯 Cross-platform compatibility

## Installation

1. Install Python dependencies:
   ```bash
   python install_dependencies.py
