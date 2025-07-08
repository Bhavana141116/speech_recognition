import speech_recognition as sr
import pyttsx3
import openai
from openai import OpenAI
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import queue
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SpeechRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Speech Recognition - Python")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize components
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        
        # OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # State variables
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.transcript_text = ""
        self.enhanced_text = ""
        
        # Setup GUI
        self.setup_gui()
        
        # Adjust microphone for ambient noise
        self.calibrate_microphone()
        
    def setup_gui(self):
        """Setup the GUI components"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="AI Speech Recognition", 
            font=("Arial", 20, "bold"),
            bg='#f0f0f0',
            fg='#333'
        )
        title_label.pack(pady=10)
        
        # Subtitle
        subtitle_label = tk.Label(
            self.root, 
            text="Speak naturally and let AI enhance your words", 
            font=("Arial", 12),
            bg='#f0f0f0',
            fg='#666'
        )
        subtitle_label.pack(pady=5)
        
        # Control buttons frame
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(pady=20)
        
        # Start/Stop button
        self.record_button = tk.Button(
            control_frame,
            text="🎤 Start Recording",
            font=("Arial", 12, "bold"),
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=10,
            command=self.toggle_recording
        )
        self.record_button.pack(side=tk.LEFT, padx=10)
        
        # Clear button
        clear_button = tk.Button(
            control_frame,
            text="🗑️ Clear All",
            font=("Arial", 12),
            bg='#f44336',
            fg='white',
            padx=20,
            pady=10,
            command=self.clear_all
        )
        clear_button.pack(side=tk.LEFT, padx=10)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Ready to record",
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#666'
        )
        self.status_label.pack(pady=5)
        
        # Transcript section
        transcript_frame = tk.LabelFrame(
            self.root,
            text="Live Transcript",
            font=("Arial", 12, "bold"),
            bg='#f0f0f0',
            fg='#333'
        )
        transcript_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.transcript_text_widget = scrolledtext.ScrolledText(
            transcript_frame,
            height=8,
            font=("Arial", 11),
            bg='#fff',
            fg='#333',
            wrap=tk.WORD
        )
        self.transcript_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # AI Enhancement section
        ai_frame = tk.LabelFrame(
            self.root,
            text="AI Enhanced Response",
            font=("Arial", 12, "bold"),
            bg='#f0f0f0',
            fg='#333'
        )
        ai_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # AI buttons frame
        ai_buttons_frame = tk.Frame(ai_frame, bg='#f0f0f0')
        ai_buttons_frame.pack(pady=5)
        
        self.enhance_button = tk.Button(
            ai_buttons_frame,
            text="🤖 Enhance with AI",
            font=("Arial", 11),
            bg='#2196F3',
            fg='white',
            padx=15,
            pady=5,
            command=self.enhance_with_ai
        )
        self.enhance_button.pack(side=tk.LEFT, padx=5)
        
        self.speak_original_button = tk.Button(
            ai_buttons_frame,
            text="🔊 Speak Original",
            font=("Arial", 11),
            bg='#FF9800',
            fg='white',
            padx=15,
            pady=5,
            command=self.speak_original
        )
        self.speak_original_button.pack(side=tk.LEFT, padx=5)
        
        self.speak_enhanced_button = tk.Button(
            ai_buttons_frame,
            text="🔊 Speak Enhanced",
            font=("Arial", 11),
            bg='#9C27B0',
            fg='white',
            padx=15,
            pady=5,
            command=self.speak_enhanced
        )
        self.speak_enhanced_button.pack(side=tk.LEFT, padx=5)
        
        self.enhanced_text_widget = scrolledtext.ScrolledText(
            ai_frame,
            height=8,
            font=("Arial", 11),
            bg='#f8f9fa',
            fg='#333',
            wrap=tk.WORD
        )
        self.enhanced_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        self.status_label.config(text="Calibrating microphone for ambient noise...")
        self.root.update()
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.status_label.config(text="Microphone calibrated. Ready to record.")
        except Exception as e:
            self.status_label.config(text=f"Microphone calibration failed: {str(e)}")
    
    def toggle_recording(self):
        """Toggle recording on/off"""
        if not self.is_listening:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start continuous speech recognition"""
        self.is_listening = True
        self.record_button.config(text="🛑 Stop Recording", bg='#f44336')
        self.status_label.config(text="🔴 Recording... Speak now!")
        
        # Start listening in a separate thread
        self.listen_thread = threading.Thread(target=self.listen_continuously)
        self.listen_thread.daemon = True
        self.listen_thread.start()
    
    def stop_recording(self):
        """Stop speech recognition"""
        self.is_listening = False
        self.record_button.config(text="🎤 Start Recording", bg='#4CAF50')
        self.status_label.config(text="Recording stopped.")
    
    def listen_continuously(self):
        """Continuously listen for speech"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Recognize speech in background
                threading.Thread(
                    target=self.recognize_speech, 
                    args=(audio,),
                    daemon=True
                ).start()
                
            except sr.WaitTimeoutError:
                # Timeout is normal, continue listening
                pass
            except Exception as e:
                if self.is_listening:  # Only show error if still supposed to be listening
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"Listening error: {str(e)}"
                    ))
                break
    
    def recognize_speech(self, audio):
        """Recognize speech from audio"""
        try:
            # Use Google's speech recognition
            text = self.recognizer.recognize_google(audio)
            
            # Update transcript in main thread
            self.root.after(0, lambda: self.update_transcript(text))
            
        except sr.UnknownValueError:
            # Speech was unintelligible
            pass
        except sr.RequestError as e:
            self.root.after(0, lambda: self.status_label.config(
                text=f"Speech recognition error: {str(e)}"
            ))
    
    def update_transcript(self, text):
        """Update the transcript display"""
        self.transcript_text += text + " "
        self.transcript_text_widget.delete(1.0, tk.END)
        self.transcript_text_widget.insert(tk.END, self.transcript_text)
        self.transcript_text_widget.see(tk.END)
    
    def enhance_with_ai(self):
        """Enhance transcript using OpenAI"""
        if not self.transcript_text.strip():
            messagebox.showwarning("Warning", "No transcript to enhance!")
            return
        
        if not os.getenv('OPENAI_API_KEY'):
            messagebox.showerror("Error", "OpenAI API key not found! Please set OPENAI_API_KEY in .env file")
            return
        
        self.enhance_button.config(text="🔄 Processing...", state='disabled')
        self.status_label.config(text="Enhancing with AI...")
        
        # Process in background thread
        threading.Thread(target=self.process_with_openai, daemon=True).start()
    
    def process_with_openai(self):
        """Process transcript with OpenAI API"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that enhances speech transcripts. Fix grammar, improve structure, and make the text more coherent while maintaining the original meaning."
                    },
                    {
                        "role": "user",
                        "content": f"Please enhance and improve the following speech transcript:\n\n{self.transcript_text}"
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            enhanced_text = response.choices[0].message.content
            
            # Update UI in main thread
            self.root.after(0, lambda: self.update_enhanced_text(enhanced_text))
            
        except Exception as e:
            self.root.after(0, lambda: self.show_ai_error(str(e)))
    
    def update_enhanced_text(self, enhanced_text):
        """Update the enhanced text display"""
        self.enhanced_text = enhanced_text
        self.enhanced_text_widget.delete(1.0, tk.END)
        self.enhanced_text_widget.insert(tk.END, enhanced_text)
        
        self.enhance_button.config(text="🤖 Enhance with AI", state='normal')
        self.status_label.config(text="AI enhancement complete!")
    
    def show_ai_error(self, error_msg):
        """Show AI processing error"""
        self.enhance_button.config(text="🤖 Enhance with AI", state='normal')
        self.status_label.config(text="AI enhancement failed")
        messagebox.showerror("AI Error", f"Failed to enhance text: {error_msg}")
    
    def speak_original(self):
        """Speak the original transcript"""
        if not self.transcript_text.strip():
            messagebox.showwarning("Warning", "No transcript to speak!")
            return
        
        threading.Thread(target=self.speak_text, args=(self.transcript_text,), daemon=True).start()
    
    def speak_enhanced(self):
        """Speak the enhanced text"""
        if not self.enhanced_text.strip():
            messagebox.showwarning("Warning", "No enhanced text to speak!")
            return
        
        threading.Thread(target=self.speak_text, args=(self.enhanced_text,), daemon=True).start()
    
    def speak_text(self, text):
        """Convert text to speech"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("TTS Error", f"Text-to-speech failed: {str(e)}"))
    
    def clear_all(self):
        """Clear all text fields"""
        self.transcript_text = ""
        self.enhanced_text = ""
        self.transcript_text_widget.delete(1.0, tk.END)
        self.enhanced_text_widget.delete(1.0, tk.END)
        self.status_label.config(text="All text cleared. Ready to record.")

def main():
    # Check for required API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key.")
    
    # Create and run the application
    root = tk.Tk()
    app = SpeechRecognitionApp(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication closed by user.")

if __name__ == "__main__":
    main()
