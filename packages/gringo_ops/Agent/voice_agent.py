#!/usr/bin/env python3
import speech_recognition as sr
import subprocess

def listen():

    """Placeholder docstring for listen."""    recognizer = sr.Recognizer()
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

    """Placeholder docstring for main."""    while True:
        command = listen()
        if not command:
            continue
        print(f"🗣️ You said: {command}")
        if command.lower() in ["exit", "quit", "stop"]:
            print("👋 Exiting voice agent.")
            break
        subprocess.run(["agent"] + command.lower().split())

if __name__ == "__main__":
    main()