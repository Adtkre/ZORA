import tkinter as tk
import threading
import speech_recognition as sr
import webbrowser
import pyttsx3
import os
import subprocess
import pyautogui
import time
import psutil
from openai import OpenAI
import queue
import platform
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

recognizer = sr.Recognizer()
engine = pyttsx3.init()
speak_queue = queue.Queue()

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
status_label = tk.Label(root, text="🎧 ZORA is running...", fg="white", bg="#ebc8e1", font=("Segoe UI", 11))
status_label.pack(expand=True)


def speak_worker():
    while True:
        text = speak_queue.get()
        status_label.config(text="💬 " + text[:30] + "...")
        engine.say(text)
        engine.runAndWait()
        speak_queue.task_done()

def speak(text):
    speak_queue.put(text)

threading.Thread(target=speak_worker, daemon=True).start()

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

client = OpenAI("your-api-key") 

def aiProcess(command):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  
            messages=[{"role": "user", "content": command}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("AI error:", e)
        return "Sorry, I couldn't get a response from the AI."
def check_battery():
    battery = psutil.sensors_battery()
    percent = battery.percent
    plugged = battery.power_plugged

    if not plugged and percent <= 30:
        if percent < 10:
            speak(f"Critical alert! Battery at {percent}%. Connect your charger now or I might shut down.")
        else:
            speak(f"Battery is at {percent}%. Please plug in the charger.")

def battery_monitor():
    while True:
        check_battery()
        time.sleep(300)  

def open_settings():
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(["start", "ms-settings:"], shell=True)
        elif system == "Darwin":
            subprocess.run(["open", "/System/Applications/System Preferences.app"])
        elif system == "Linux":
            subprocess.run(["gnome-control-center"])
        else:
            speak("Sorry, your OS is not supported.")
    except Exception as e:
        print(f"Error opening settings: {e}")


def change_volume(step):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        new_volume = min(max(0.0, current + step), 1.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
    except Exception as e:
        speak("Failed to change volume.")
        print("Volume error:", e)

def increase_volume():
    change_volume(0.1)
    speak("Volume increased")

def decrease_volume():
    change_volume(-0.1)
    speak("Volume decreased")

def increase_brightness():
    try:
        current = sbc.get_brightness(display=0)[0]
        sbc.set_brightness(min(100, current + 10))
        speak("Brightness increased")
    except Exception as e:
        speak("Failed to increase brightness")
        print("Brightness error:", e)

def decrease_brightness():
    try:
        current = sbc.get_brightness(display=0)[0]
        sbc.set_brightness(max(0, current - 10))
        speak("Brightness decreased")
    except Exception as e:
        speak("Failed to decrease brightness")
        print("Brightness error:", e)

# Command
def processCommand(c):
    c = c.lower()

    if "open google" in c:
        speak("Opening Google")
        webbrowser.open("https://google.com")

    elif "open youtube" in c:
        speak("Opening Youtube")
        webbrowser.open("https://youtube.com")

    elif "open netflix" in c:
        speak("Opening Netflix")
        webbrowser.open("https://netflix.com")

    elif "shutdown" in c:
        speak("Shutting down your computer.")
        os.system("shutdown /s /t 1")

    elif "sleep" in c:
        speak("Putting your computer to sleep.")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    elif "lock screen" in c:
        speak("Locking your computer.")
        os.system("rundll32.exe user32.dll,LockWorkStation")

    elif "restart" in c:
        speak("Restarting your computer.")
        os.system("shutdown /r /t 1")

    elif "open notepad" in c:
        speak("Opening Notepad")
        subprocess.Popen("notepad.exe")
        time.sleep(2)
        speak("Start speaking. Say 'stop typing' to finish.")
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
        vscode_path = "add your path"
        if os.path.exists(vscode_path):
            speak("Opening VS Code")
            os.startfile(vscode_path)
        else:
            speak("VS Code not found.")

    elif "open chrome" in c:
        chrome_path = "add your path"
        if os.path.exists(chrome_path):
            speak("Opening Google Chrome")
            subprocess.Popen(chrome_path)
        else:
            speak("Chrome not found.")

    elif "open settings" in c:
        speak("Opening Settings")
        open_settings()

    elif "increase volume" in c:
        increase_volume()

    elif "decrease volume" in c:
        decrease_volume() 

    elif "increase brightness" in c:
        increase_brightness()

    elif "decrease brightness" in c:
        decrease_brightness()

    elif any(exit_word in c for exit_word in ["stop", "exit", "bye"]):
        speak("Okay. Goodbye!")
        exit(0)

    else:
        speak("Processing with AI.")
        output = aiProcess(c)
        speak(output)

def assistant_loop():
    speak("Starting ZORA...")
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
                    print("ZORA is active. Listening for command...")
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_google(audio)
                    processCommand(command)

        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    threading.Thread(target=assistant_loop, daemon=True).start()
    threading.Thread(target=battery_monitor, daemon=True).start()
    root.mainloop()

