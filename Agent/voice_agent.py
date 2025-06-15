#!/usr/bin/env python3
import speech_recognition as sr
import subprocess
from tools.memory import write_to_memory
from datetime import datetime

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Speak now...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        print("❌ Couldn't understand.")
    except sr.RequestError as e:
        print(f"🛑 API error: {e}")

def main():
    while True:
        command = listen()
        if not command:
            continue
        print(f"🗣️ You said: {command}")
        # Save to memory
        metadata = {
            "agent": "voice",
            "timestamp": datetime.now().isoformat(),
            "command": command
        }
        write_to_memory(command, f"Ran: {command}", metadata)
        if command.lower() in ["exit", "quit", "stop"]:
            print("👋 Exiting voice agent.")
            break
        subprocess.run(["agent"] + command.lower().split())

if __name__ == "__main__":
    main()