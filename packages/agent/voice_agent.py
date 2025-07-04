#!/usr/bin/env python3
import speech_recognition as sr
import subprocess
from tools.memory import write_to_memory
from datetime import datetime

def listen():
    """Placeholder docstring for listen."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Speak now...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        print("❌ Couldn't understand.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

def main():
    """Placeholder docstring for main."""
    listen()