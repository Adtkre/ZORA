import tkinter as tk
import threading
import speech_recognition as sr
import webbrowser
import pyttsx3
import os
import subprocess
import pyautogui
import time
from openai import OpenAI

recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Floating window
root = tk.Tk()
root.title("ZORA")
root.geometry("300x150")
root.configure(bg="#ebc8e1")
root.wm_attributes("-topmost", 1)
root.resizable(False, False)

# Dragging support
def start_move(event):
    root.x = event.x
    root.y = event.y

def do_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")

root.bind("<Button-1>", start_move)
root.bind("<B1-Motion>", do_move)

# Label
status_label = tk.Label(root, text="🎧 Zora is running...", fg="white", bg="#ebc8e1", font=("Segoe UI", 11))
status_label.pack(expand=True)

def speak(text):
    status_label.config(text="💬 " + text[:30] + "...")
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I did not catch that.")
        return ""
    except sr.RequestError:
        speak("Sorry, there was a speech service issue.")
        return ""

def aiProcess(command):
    client = OpenAI(
        api_key="your-openai-api-key"
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[{"role": "user", "content": command}]
    )

    return completion.choices[0].message.content

def processCommand(c):
    c = c.lower()

    if "open google" in c:
        webbrowser.open("https://google.com")

    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")

    elif "open netflix" in c:
        webbrowser.open("https://netflix.com")

    # OS Commands
    elif "shutdown" in c:
        speak("Shutting down your computer.")
        os.system("shutdown /s /t 1")

    elif "restart" in c:
        speak("Restarting your computer.")
        os.system("shutdown /r /t 1")

    elif "open notepad" in c:
        speak("Opening Notepad")
        subprocess.Popen("notepad.exe")
        time.sleep(2)

        speak("Start speaking. I will type in Notepad. Say 'stop typing' to finish.")
        while True:
            try:
                with sr.Microphone() as source:
                    audio = recognizer.listen(source)
                    said = recognizer.recognize_google(audio).lower()
                    if "stop typing" in said:
                        speak("Okay, stopping typing.")
                        break
                    pyautogui.typewrite(said + "\n")
            except Exception as e:
                print("Typing error:", e)
                speak("Sorry, I couldn't hear you.")

    elif "open calculator" in c:
        speak("Opening Calculator")
        subprocess.Popen("calc.exe")

    elif "open spotify" in c:
        speak("Opening Spotify")
        subprocess.Popen("spotify.exe")

    elif "open files" in c:
        speak("Opening File Explorer")
        subprocess.Popen("explorer.exe")

    elif "open code editor" in c:
        vscode_path = "C:\\Users\\DELL\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Visual Studio Code\\Visual Studio Code.lnk"
        if os.path.exists(vscode_path):
            speak("Opening VS Code")
            os.startfile(vscode_path)
        else:
            speak("VS Code not found.")

    elif "open chrome" in c:
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        if os.path.exists(chrome_path):
            speak("Opening Google Chrome")
            subprocess.Popen(chrome_path)
        else:
            speak("Chrome not found.")

    elif any(exit_word in c for exit_word in ["stop", "exit", "bye"]):
        speak("Okay. Goodbye!")
        exit(0)

    else:
        speak("Processing with AI.")
        output = aiProcess(c)
        speak(output)


def assistant_loop():
    speak("Starting Zora...")
    while True:
        print("Recognizing...")
        try:
            with sr.Microphone() as source:
                status_label.config(text="🎧 Listening for wake word...")
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=2)

            word = recognizer.recognize_google(audio)

            if word.lower() == "zora":
                speak("Yes boss")
                with sr.Microphone() as source:
                    status_label.config(text="🎤 Waiting for your command...")
                    print("Zora is active. Listening for command...")
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_google(audio)
                    processCommand(command)

        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    threading.Thread(target=assistant_loop, daemon=True).start()
    root.mainloop()
