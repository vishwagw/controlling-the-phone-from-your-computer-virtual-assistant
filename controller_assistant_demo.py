# this is a sample codebase for building the asssitant. 
# objective: control the smartphone thorugh computer virtual assistant.
# VERSION 1.7.20
# 2024:04:30

# adding the phone control function:
# using gTTS
# importing libs
import speech_recognition as sr
import datetime
import webbrowser
import wikipedia
import psutil
import os
import subprocess
import platform
from gtts import gTTS
import pygame
import tempfile
import time
import requests
import json
import threading

# Function for speaking with gTTS
def speak(text):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        temp_filename = fp.name
    
    # Generate speech
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(temp_filename)
    
    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(temp_filename)
    pygame.mixer.music.play()
    
    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    # Clean up
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    
    # Remove temporary file
    try:
        os.unlink(temp_filename)
    except:
        pass
    
    print(text)

# Function to listen to voice input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
    
    try:
        print("Recognizing...")
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't understand that.")
        return ""
    except sr.RequestError:
        speak("Sorry, there was an error with the speech recognition service.")
        return ""

# Function to greet the user
def greet_user():
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning!"
    elif 12 <= current_hour < 18:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"
    
    speak(greeting)
    print(greeting)

# New phone control functionality
class PhoneController:
    def __init__(self):
        # Default configuration - should be loaded from a config file in a real implementation
        self.phone_type = None  # "android" or "ios"
        self.phone_ip = None
        self.phone_port = None
        self.connected = False
        self.api_key = None  # For secure communication
        self.device_id = None
        
        # Load configuration if available
        self.load_config()
    
    def load_config(self):
        # Check if config file exists
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phone_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.phone_type = config.get('phone_type')
                    self.phone_ip = config.get('phone_ip')
                    self.phone_port = config.get('phone_port')
                    self.api_key = config.get('api_key')
                    self.device_id = config.get('device_id')
                    
                    # Test connection
                    if self.test_connection():
                        self.connected = True
                        print(f"Successfully connected to {self.phone_type} phone at {self.phone_ip}:{self.phone_port}")
                    else:
                        print("Phone configuration found but connection failed")
            except Exception as e:
                print(f"Error loading phone configuration: {str(e)}")
    
    def save_config(self):
        config = {
            'phone_type': self.phone_type,
            'phone_ip': self.phone_ip,
            'phone_port': self.phone_port,
            'api_key': self.api_key,
            'device_id': self.device_id
        }
        
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phone_config.json")
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            print("Phone configuration saved successfully")
            return True
        except Exception as e:
            print(f"Error saving phone configuration: {str(e)}")
            return False
    
    def setup_phone(self):
        speak("Let's set up phone control. What type of phone do you have? Android or iPhone?")
        phone_type = listen().lower()
        
        if "android" in phone_type:
            self.phone_type = "android"
            speak("Android phone selected. To control your Android phone, you'll need to install a companion app.")
            speak("Please install 'Trinity Phone Control' from the Google Play Store.")
        elif "iphone" in phone_type or "ios" in phone_type:
            self.phone_type = "ios"
            speak("iPhone selected. To control your iPhone, you'll need to install a companion app.")
            speak("Please install 'Trinity Phone Control' from the App Store.")
        else:
            speak("Sorry, I didn't understand the phone type. Please try again saying 'Android' or 'iPhone'.")
            return False
        
        speak("After installing the app, please enter the IP address shown in the app.")
        ip_address = listen().replace(" ", "").replace("dot", ".")
        self.phone_ip = ip_address
        
        speak("Now please enter the port number shown in the app.")
        try:
            port = int(listen().replace(" ", ""))
            self.phone_port = port
        except:
            speak("I couldn't understand the port number. Using default port 8080.")
            self.phone_port = 8080
        
        speak("Now please enter the pairing code shown in the app.")
        pairing_code = listen().replace(" ", "")
        
        # In a real implementation, this would perform secure pairing
        # For demonstration purposes, we'll just simulate it
        speak("Attempting to pair with your phone...")
        
        # Simulate pairing process
        time.sleep(2)
        
        # Generate a fake API key and device ID for demonstration
        import uuid
        self.api_key = str(uuid.uuid4())
        self.device_id = str(uuid.uuid4())[:8]
        
        if self.test_connection():
            self.connected = True
            self.save_config()
            speak(f"Successfully paired with your {self.phone_type} phone. You can now control it with voice commands.")
            return True
        else:
            speak("Pairing failed. Please check that the app is running and try again.")
            return False
    
    def test_connection(self):
        # In a real implementation, this would make an actual API call to the phone
        # For demonstration purposes, we'll just simulate a successful connection
        
        # Uncommenting the code below would attempt a real connection
        """
        try:
            url = f"http://{self.phone_ip}:{self.phone_port}/ping"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Device-ID": self.device_id
            }
            response = requests.get(url, headers=headers, timeout=3)
            return response.status_code == 200
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False
        """
        
        # For demo purposes, assume connection works if we have all the necessary info
        return (self.phone_type and self.phone_ip and 
                self.phone_port and self.api_key and self.device_id)
    
    def send_command(self, command_type, params=None):
        if not self.connected:
            speak("Phone is not connected. Please set up phone control first.")
            return False
        
        # In a real implementation, this would make an actual API call to the phone
        # For demonstration purposes, we'll just simulate successful commands
        
        """
        try:
            url = f"http://{self.phone_ip}:{self.phone_port}/command"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Device-ID": self.device_id,
                "Content-Type": "application/json"
            }
            payload = {
                "command": command_type,
                "parameters": params or {}
            }
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Command failed: {str(e)}")
            return False
        """
        
        # For demo purposes
        print(f"Sending command to {self.phone_type} phone: {command_type}")
        if params:
            print(f"Parameters: {params}")
        
        # Simulate a delay for command execution
        time.sleep(1)
        return True
    
    def make_call(self, contact_name):
        speak(f"Calling {contact_name} on your phone...")
        return self.send_command("make_call", {"contact": contact_name})
    
    def send_text(self, contact_name, message):
        speak(f"Sending text to {contact_name}...")
        return self.send_command("send_text", {"contact": contact_name, "message": message})
    
    def open_app(self, app_name):
        speak(f"Opening {app_name} on your phone...")
        return self.send_command("open_app", {"app_name": app_name})
    
    def take_photo(self):
        speak("Taking a photo with your phone camera...")
        return self.send_command("take_photo")
    
    def set_alarm(self, time_str):
        speak(f"Setting alarm for {time_str} on your phone...")
        return self.send_command("set_alarm", {"time": time_str})
    
    def check_battery(self):
        speak("Checking your phone's battery level...")
        # In a real implementation, this would return the actual battery level
        # For demonstration, we'll just simulate it
        
        """
        try:
            url = f"http://{self.phone_ip}:{self.phone_port}/battery"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Device-ID": self.device_id
            }
            response = requests.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                data = response.json()
                battery_level = data.get("level", 0)
                is_charging = data.get("charging", False)
                
                status = "charging" if is_charging else "not charging"
                speak(f"Your phone's battery is at {battery_level} percent and is {status}.")
                return True
            return False
        except Exception as e:
            print(f"Battery check failed: {str(e)}")
            return False
        """
        
        # For demo purposes
        import random
        battery_level = random.randint(20, 95)
        is_charging = random.choice([True, False])
        status = "charging" if is_charging else "not charging"
        speak(f"Your phone's battery is at {battery_level} percent and is {status}.")
        return True
    
    def find_phone(self):
        speak("Triggering sound alert on your phone to help you find it...")
        return self.send_command("find_phone")
    
    def toggle_do_not_disturb(self):
        speak("Toggling Do Not Disturb mode on your phone...")
        return self.send_command("toggle_dnd")
    
    def get_notifications(self):
        speak("Checking recent notifications on your phone...")
        # In a real implementation, this would return actual notifications
        # For demonstration, we'll just simulate it
        
        """
        try:
            url = f"http://{self.phone_ip}:{self.phone_port}/notifications"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Device-ID": self.device_id
            }
            response = requests.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                data = response.json()
                notifications = data.get("notifications", [])
                
                if not notifications:
                    speak("You have no recent notifications.")
                else:
                    speak(f"You have {len(notifications)} recent notifications.")
                    # Read the 3 most recent notifications
                    for i, notif in enumerate(notifications[:3]):
                        app = notif.get("app", "Unknown app")
                        message = notif.get("message", "No content")
                        speak(f"Notification from {app}: {message}")
                return True
            return False
        except Exception as e:
            print(f"Notification check failed: {str(e)}")
            return False
        """
        
        # For demo purposes
        speak("You have 3 recent notifications.")
        speak("Notification from Messages: 'Are we still meeting today?'")
        speak("Notification from Calendar: 'Meeting reminder in 30 minutes'")
        speak("Notification from Weather: 'Rain expected this afternoon'")
        return True

# Initialize the phone controller
phone_controller = PhoneController()

# Function to handle phone control commands
def handle_phone_command(command):
    if not phone_controller.connected:
        speak("Your phone is not connected. Would you like to set it up now?")
        response = listen().lower()
        if "yes" in response or "yeah" in response or "sure" in response:
            if phone_controller.setup_phone():
                speak("Phone setup complete. What would you like to do with your phone?")
                new_command = listen()
                if new_command:
                    return handle_phone_command(new_command)
            return True
        else:
            speak("OK, phone setup cancelled.")
            return True
    
    # Call commands
    if "call" in command:
        # Extract contact name
        for phrase in ["call", "phone"]:
            if phrase in command:
                parts = command.split(phrase)
                if len(parts) > 1 and parts[1].strip():
                    contact = parts[1].strip()
                    phone_controller.make_call(contact)
                    return True
        
        # If contact not found in command
        speak("Who would you like to call?")
        contact = listen()
        if contact:
            phone_controller.make_call(contact)
        return True
    
    # Text message commands
    elif "text" in command or "message" in command or "send message" in command:
        contact = None
        message = None
        
        # Check if the command already has the contact
        for phrase in ["text", "message to", "send message to"]:
            if phrase in command:
                parts = command.split(phrase)
                if len(parts) > 1:
                    # Look for "saying" or similar to split contact and message
                    contact_msg = parts[1].strip()
                    for separator in ["saying", "that says", "with message", "with text"]:
                        if separator in contact_msg:
                            contact_msg_parts = contact_msg.split(separator, 1)
                            contact = contact_msg_parts[0].strip()
                            message = contact_msg_parts[1].strip()
                            break
                    
                    # If no separator found, just extract contact
                    if not message and contact_msg:
                        contact = contact_msg
        
        # If contact not found or incomplete information
        if not contact:
            speak("Who would you like to send a message to?")
            contact = listen()
        
        if contact and not message:
            speak(f"What message would you like to send to {contact}?")
            message = listen()
        
        if contact and message:
            phone_controller.send_text(contact, message)
        return True
    
    # Open app commands
    elif "open" in command and ("app" in command or "application" in command):
        app_name = None
        
        for phrase in ["open app", "open application", "launch app"]:
            if phrase in command:
                parts = command.split(phrase)
                if len(parts) > 1 and parts[1].strip():
                    app_name = parts[1].strip()
                    break
        
        if not app_name:
            speak("Which app would you like to open on your phone?")
            app_name = listen()
            
        if app_name:
            phone_controller.open_app(app_name)
        return True
    
    # Take a photo
    elif "take photo" in command or "take picture" in command or "take a photo" in command or "take a picture" in command:
        phone_controller.take_photo()
        return True
    
    # Set an alarm
    elif "set alarm" in command or "set an alarm" in command:
        time_str = None
        
        for phrase in ["set alarm", "set an alarm", "wake me up"]:
            if phrase in command:
                parts = command.split(phrase)
                if len(parts) > 1 and parts[1].strip():
                    time_str = parts[1].strip()
                    break
        
        if not time_str:
            speak("What time would you like to set the alarm for?")
            time_str = listen()
            
        if time_str:
            phone_controller.set_alarm(time_str)
        return True
    
    # Check battery
    elif "battery" in command or "charge" in command:
        phone_controller.check_battery()
        return True
    
    # Find phone
    elif "find phone" in command or "find my phone" in command or "locate phone" in command or "where is my phone" in command:
        phone_controller.find_phone()
        return True
    
    # Toggle Do Not Disturb
    elif "do not disturb" in command or "silent mode" in command or "silence phone" in command:
        phone_controller.toggle_do_not_disturb()
        return True
    
    # Check notifications
    elif "notification" in command or "messages" in command:
        phone_controller.get_notifications()
        return True
    
    # Help with phone commands
    elif "phone help" in command or "what can you do with my phone" in command:
        speak("I can help you control your phone with commands like:")
        speak("Call a contact, send a text message, open an app, take a photo,")
        speak("set an alarm, check battery level, find your phone,")
        speak("toggle do not disturb mode, or check your notifications.")
        return True
    
    # Disconnect phone
    elif "disconnect phone" in command or "unpair phone" in command:
        speak("Are you sure you want to disconnect your phone?")
        confirm = listen().lower()
        if "yes" in confirm or "yeah" in confirm:
            phone_controller.connected = False
            speak("Phone disconnected. You can reconnect it anytime.")
        else:
            speak("Phone disconnect cancelled.")
        return True
    
    # If no specific phone command matched
    else:
        speak("I'm not sure what you want to do with your phone. You can try commands like 'call someone', 'send a text', or 'open an app'.")
        return True

# the command function for interaction:
def process_command(command):
    # Handle phone control commands first
    if any(phrase in command for phrase in ["phone", "call", "text", "message", "battery"]):
        if handle_phone_command(command):
            return True

# Main loop
def virtual_assistant():
    greet_user()
    speak("I am Trinity, your virtual assistant. How can I help you?")
    
    # Check if phone is already configured
    if phone_controller.connected:
        speak("Your phone is connected and ready for commands.")
    
    running = True
    
    while running:
        command = listen()
        if command:
            running = process_command(command)

if __name__ == "__main__":
    virtual_assistant()
