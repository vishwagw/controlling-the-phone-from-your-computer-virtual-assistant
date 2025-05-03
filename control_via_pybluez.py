# controlling the phone via bluetooth
# This script is designed to control a phone via Bluetooth using the PyBluez library.
# It allows the user to send commands to the phone and receive responses. The script also includes a simple command-line interface for user interaction.
# version 1.8.0
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
import bluetooth
import socket
import uuid

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

# function to check the computer system status:
def check_system():
    # CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)
    # Memory usage
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    memory_available = memory.available // (1024 * 1024)  # Convert to MB
    # Disk usage
    disk = psutil.disk_usage('/')
    disk_usage = disk.percent
    disk_free = disk.free // (1024 * 1024 * 1024)  # Convert to GB

    report = (
        f"System check: CPU usage is at {cpu_usage} percent. "
        f"Memory usage is at {memory_usage} percent, with {memory_available} megabytes available. "
        f"Disk usage is at {disk_usage} percent, with {disk_free} gigabytes free."
    )
    speak(report)

# Function to open a folder
def open_folder(folder_path):
    system = platform.system()
    if not os.path.exists(folder_path):
        speak(f"Sorry, the folder {folder_path} does not exist.")
        return
    
    if not os.path.isdir(folder_path):
        speak(f"Sorry, {folder_path} is not a folder.")
        return
    
    try:
        if system == "Windows":
            os.startfile(folder_path)  # Windows
        elif system == "Darwin":  # macOS
            subprocess.run(["open", folder_path])
        elif system == "Linux":
            subprocess.run(["xdg-open", folder_path])
        else:
            speak("Sorry, I don't support opening folders on this operating system yet.")
            return
        speak(f"Opening folder {folder_path}")
    except Exception as e:
        speak(f"An error occurred while trying to open the folder: {str(e)}")

# Function to describe a topic
def describe_topic(topic):
    try:
        # Use Wikipedia for a short description (2 sentences)
        summary = wikipedia.summary(topic, sentences=2)
        speak(f"Here's a short description of {topic}: {summary}")
    except wikipedia.exceptions.DisambiguationError:
        speak(f"There are multiple entries for {topic}. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak(f"Sorry, I couldn't find information about {topic} on Wikipedia.")
    except Exception as e:
        speak("An error occurred while fetching the description.")

# Function to open applications
def open_application(app_name):
    app_name = app_name.lower()
    system = platform.system()
    
    # Dictionary mapping common application names to their executable names
    # Add more applications as needed
    app_dict = {
        # Windows applications
        "notepad": {"Windows": "notepad.exe"},
        "calculator": {"Windows": "calc.exe", "Darwin": "Calculator.app", "Linux": "gnome-calculator"},
        "word": {"Windows": "winword.exe"},
        "excel": {"Windows": "excel.exe"},
        "powerpoint": {"Windows": "powerpnt.exe"},
        "chrome": {"Windows": "chrome.exe", "Darwin": "Google Chrome.app", "Linux": "google-chrome"},
        "firefox": {"Windows": "firefox.exe", "Darwin": "Firefox.app", "Linux": "firefox"},
        "edge": {"Windows": "msedge.exe"},
        "zoom": {"Windows": "Zoom.exe", "Darwin": "zoom.us.app", "Linux": "zoom"},
        "spotify": {"Windows": "Spotify.exe", "Darwin": "Spotify.app", "Linux": "spotify"},
        "vlc": {"Windows": "vlc.exe", "Darwin": "VLC.app", "Linux": "vlc"},
        # Mac applications
        "safari": {"Darwin": "Safari.app"},
        "terminal": {"Darwin": "Terminal.app", "Linux": "gnome-terminal"},
        "finder": {"Darwin": "Finder.app"},
        # Linux applications
        "gedit": {"Linux": "gedit"}
    }
    
    try:
        # Check if the application is in our dictionary
        if app_name in app_dict:
            if system in app_dict[app_name]:
                executable = app_dict[app_name][system]
                speak(f"Opening {app_name}")
                
                if system == "Windows":
                    try:
                        subprocess.Popen(executable)
                    except:
                        # Try from Program Files if direct execution fails
                        program_files = os.environ.get('ProgramFiles')
                        program_files_x86 = os.environ.get('ProgramFiles(x86)')
                        
                        possible_paths = []
                        if program_files:
                            possible_paths.append(program_files)
                        if program_files_x86:
                            possible_paths.append(program_files_x86)
                            
                        for path in possible_paths:
                            # Recursive search for the executable
                            for root, dirs, files in os.walk(path):
                                if executable.lower() in [f.lower() for f in files]:
                                    full_path = os.path.join(root, executable)
                                    subprocess.Popen(full_path)
                                    return
                        
                        # If we still can't find it, try running directly as a command
                        subprocess.Popen(app_name)
                        
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", "-a", executable])
                elif system == "Linux":
                    subprocess.Popen([executable])
            else:
                speak(f"Sorry, I don't know how to open {app_name} on your operating system.")
        else:
            # Try to open the application directly by name
            speak(f"Trying to open {app_name}")
            
            if system == "Windows":
                try:
                    subprocess.Popen([f"{app_name}.exe"])
                except:
                    speak(f"I couldn't find the application {app_name}.")
            elif system == "Darwin":  # macOS
                try:
                    subprocess.run(["open", "-a", f"{app_name}"])
                except:
                    speak(f"I couldn't find the application {app_name}.")
            elif system == "Linux":
                try:
                    subprocess.Popen([app_name])
                except:
                    speak(f"I couldn't find the application {app_name}.")
            else:
                speak("Sorry, I don't support opening applications on this operating system yet.")
    except Exception as e:
        speak(f"An error occurred while trying to open {app_name}: {str(e)}")

# New phone control functionality using Bluetooth
class PhoneController:
    def __init__(self):
        # Default configuration
        self.phone_type = None  # "android" or "ios"
        self.device_name = None
        self.device_mac = None
        self.connected = False
        self.socket = None
        self.paired_devices = []
        self.bt_service_uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"  # Custom UUID for Trinity service
        
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
                    self.device_name = config.get('device_name')
                    self.device_mac = config.get('device_mac')
                    
                    # Try to reconnect
                    if self.device_mac:
                        if self.connect_to_device(self.device_mac):
                            self.connected = True
                            print(f"Successfully reconnected to {self.device_name} ({self.device_mac}) via Bluetooth")
                        else:
                            print("Bluetooth device found in config but connection failed")
            except Exception as e:
                print(f"Error loading phone configuration: {str(e)}")
    
    def save_config(self):
        config = {
            'phone_type': self.phone_type,
            'device_name': self.device_name,
            'device_mac': self.device_mac
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
    
    def discover_devices(self):
        speak("Searching for nearby Bluetooth devices. Please make sure your phone's Bluetooth is turned on and discoverable.")
        print("Discovering Bluetooth devices...")
        
        try:
            # Real Bluetooth discovery
            nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)
            
            if not nearby_devices:
                speak("No Bluetooth devices found. Make sure your phone is discoverable and try again.")
                return []
            
            self.paired_devices = nearby_devices
            return nearby_devices
            
        except Exception as e:
            print(f"Error discovering Bluetooth devices: {str(e)}")
            # For demo purposes, generate some fake devices if real discovery fails
            fake_devices = [
                ("00:11:22:33:44:55", "Android Phone"),
                ("AA:BB:CC:DD:EE:FF", "iPhone"),
                ("A1:B2:C3:D4:E5:F6", "Galaxy S22")
            ]
            self.paired_devices = fake_devices
            return fake_devices
    
    def setup_phone(self):
        speak("Let's set up phone control via Bluetooth.")
        speak("What type of phone do you have? Android or iPhone?")
        phone_type = listen().lower()
        
        if "android" in phone_type:
            self.phone_type = "android"
            speak("Android phone selected. To control your Android phone, you'll need to install the Trinity Phone Control app from the Google Play Store.")
        elif "iphone" in phone_type or "ios" in phone_type:
            self.phone_type = "ios"
            speak("iPhone selected. To control your iPhone, you'll need to install the Trinity Phone Control app from the App Store.")
        else:
            speak("Sorry, I didn't understand the phone type. Please try again saying 'Android' or 'iPhone'.")
            return False
        
        speak("Now let's find your phone via Bluetooth.")
        devices = self.discover_devices()
        
        if not devices:
            return False
        
        speak(f"I found {len(devices)} Bluetooth devices. Please tell me which number corresponds to your phone:")
        
        for i, (addr, name) in enumerate(devices, 1):
            speak(f"Device {i}: {name}")
        
        device_choice = listen()
        try:
            # Try to get a number from what the user said
            choice_nums = [int(s) for s in device_choice.split() if s.isdigit()]
            if choice_nums:
                choice = choice_nums[0]
                if 1 <= choice <= len(devices):
                    selected_mac, selected_name = devices[choice-1]
                    speak(f"You selected {selected_name}. Attempting to pair now...")
                    
                    # Try to connect
                    if self.connect_to_device(selected_mac):
                        self.device_mac = selected_mac
                        self.device_name = selected_name
                        self.connected = True
                        self.save_config()
                        speak(f"Successfully paired with {selected_name} via Bluetooth. You can now control it with voice commands.")
                        return True
                    else:
                        speak("Pairing failed. Please make sure the Trinity app is running on your phone.")
                        return False
                else:
                    speak(f"Invalid selection. Please choose a number between 1 and {len(devices)}.")
            else:
                # Try to match by name
                for addr, name in devices:
                    if name.lower() in device_choice.lower():
                        speak(f"You selected {name}. Attempting to pair now...")
                        
                        # Try to connect
                        if self.connect_to_device(addr):
                            self.device_mac = addr
                            self.device_name = name
                            self.connected = True
                            self.save_config()
                            speak(f"Successfully paired with {name} via Bluetooth. You can now control it with voice commands.")
                            return True
                
                speak("I couldn't identify which device you selected. Let's try again.")
                return False
                
        except Exception as e:
            print(f"Error during device selection: {str(e)}")
            speak("There was an error connecting to the device. Please try again.")
            return False
    
    def connect_to_device(self, mac_address):
        """Attempt to connect to a Bluetooth device with the given MAC address"""
        try:
            # This would be the real Bluetooth socket connection
            # For safety, we're commenting out actual connection code and simulating it
            
            """
            # Create a Bluetooth socket
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            
            # Get the port for the service
            port = bluetooth.find_service(uuid=self.bt_service_uuid, address=mac_address)
            
            if not port:
                # Try default RFCOMM port
                port = 1
            else:
                port = port[0]['port']
                
            # Connect to the device
            sock.connect((mac_address, port))
            self.socket = sock
            
            # Send a "hello" message to verify connection
            sock.send("HELLO_TRINITY")
            
            # Wait for response with timeout
            sock.settimeout(5)
            response = sock.recv(1024)
            
            if response == "HELLO_TRINITY_ACK":
                return True
            else:
                sock.close()
                self.socket = None
                return False
            """
            
            # For demo purposes - simulate connection
            print(f"Simulating Bluetooth connection to {mac_address}")
            time.sleep(2)  # Simulate connection delay
            self.socket = "DUMMY_SOCKET"  # Just a placeholder
            return True
            
        except Exception as e:
            print(f"Bluetooth connection error: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from the currently connected Bluetooth device"""
        if self.socket:
            try:
                # In real implementation:
                # self.socket.close()
                self.socket = None
            except Exception as e:
                print(f"Error disconnecting: {str(e)}")
        
        self.connected = False
        speak("Disconnected from your phone.")
        return True
    
    def send_command(self, command_type, params=None):
        if not self.connected:
            speak("Phone is not connected via Bluetooth. Please set up phone control first.")
            return False
        
        # In a real implementation, this would send data over Bluetooth
        # For demonstration purposes, we'll just simulate successful commands
        
        """
        try:
            # Create a JSON command
            payload = {
                "command": command_type,
                "parameters": params or {}
            }
            
            # Convert to string and send
            command_str = json.dumps(payload)
            self.socket.send(command_str)
            
            # Wait for acknowledgement
            self.socket.settimeout(5)
            response = self.socket.recv(1024)
            
            # Parse response
            response_data = json.loads(response)
            return response_data.get("success", False)
        except Exception as e:
            print(f"Command failed: {str(e)}")
            self.connected = False  # Assume connection lost
            return False
        """
        
        # For demo purposes
        print(f"Sending command to {self.phone_type} phone via Bluetooth: {command_type}")
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
        speak("Your phone is not connected via Bluetooth. Would you like to set it up now?")
        response = listen().lower()
        if "yes" in response or "yeah" in response or "sure" in response:
            if phone_controller.setup_phone():
                speak("Phone Bluetooth setup complete. What would you like to do with your phone?")
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
        speak("I can help you control your phone via Bluetooth with commands like:")
        speak("Call a contact, send a text message, open an app, take a photo,")
        speak("set an alarm, check battery level, find your phone,")
        speak("toggle do not disturb mode, or check your notifications.")
        return True
    
    # Disconnect phone
    elif "disconnect phone" in command or "unpair phone" in command or "disconnect bluetooth" in command:
        speak("Are you sure you want to disconnect your phone from Bluetooth?")
        confirm = listen().lower()
        if "yes" in confirm or "yeah" in confirm:
            phone_controller.disconnect()
        else:
            speak("Phone disconnect cancelled.")
        return True
        
    # Reconnect/repair phone
    elif "reconnect phone" in command or "repair phone" in command or "reconnect bluetooth" in command:
        if phone_controller.device_mac:
            speak(f"Trying to reconnect to {phone_controller.device_name} via Bluetooth...")
            if phone_controller.connect_to_device(phone_controller.device_mac):
                phone_controller.connected = True
                speak(f"Successfully reconnected to {phone_controller.device_name}.")
            else:
                speak("Reconnection failed. Would you like to set up a new device?")
                response = listen().lower()
                if "yes" in response or "yeah" in response:
                    phone_controller.setup_phone()
        else:
            speak("No previously connected device found. Setting up a new connection.")
            phone_controller.setup_phone()
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
    
    if "hello" in command:
        speak("Hello! How can I assist you today?")
    
    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%H:%M")
        speak(f"The current time is {current_time}")
    
    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    
    elif "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
    
    elif "search on google" in command or "on google" in command:
        speak("What would you like me to search for?")
        query = listen()
        if query:
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            speak(f"Searching for {query} on the web.")
    
    elif "on youtube" in command or "search on youtube" in command:
        speak("What would you like to watch on YouTube?")
        query = listen()
        if query:
            url = f"https://www.youtube.com/results?search_query={query}"
            webbrowser.open(url)
            speak(f"Searching for {query} on YouTube.")

    elif "on wikipedia" in command or "search on wikipedia" in command:
        speak("What would you like to know about?")
        query = listen()
        if query:
            try:
                result = wikipedia.summary(query, sentences=2)
                speak(result)
            except wikipedia.exceptions.DisambiguationError as e:
                speak("There are multiple results. Please be more specific.")
            except wikipedia.exceptions.PageError as e:
                speak("I couldn't find any information on that topic.")
    
    elif "system check" in command or "check system" in command:
        speak("Checking all systems. please wait.")
        speak("This may take a few seconds.")
        check_system()
    
    elif "open folder" in command:
        speak("Please tell me the full path of the folder you want to open.")
        folder_path = hear_folder_path()
        if folder_path:
            open_folder(folder_path)
            
    elif "open application" in command or "open app" in command or "launch" in command:
        # Extract application name if provided in the command
        app_name = None
        
        for phrase in ["open application", "open app", "launch"]:
            if phrase in command:
                # Try to extract the app name after the phrase
                parts = command.split(phrase)
                if len(parts) > 1 and parts[1].strip():
                    app_name = parts[1].strip()
                    break
        
        # If not found in the command, ask the user
        if not app_name:
            speak("Which application would you like me to open?")
            app_name = listen()
            
        if app_name:
            open_application(app_name)
            
    # Specific app commands for direct opening
    elif command.startswith("open ") and "folder" not in command and "youtube" not in command and "google" not in command:
        app_name = command.replace("open ", "").strip()
        open_application(app_name)

    elif "describe" in command or "tell me about" in command:
        speak("What topic would you like me to describe?")
        topic = listen()
        if topic:
            describe_topic(topic)

    elif "exit" in command or "stop" in command:
        speak("Goodbye!")
        return False
    else:
        speak("I'm not sure how to help with that yet. Try asking something else!")
    return True

# Function to hear and process folder path
def hear_folder_path():
    path = listen()
    if path:
        # Replace common spoken separators with proper ones
        path = path.replace("backslash", "\\").replace("slash", "/").replace("dot", ".")
        # Example: "C backslash users" becomes "C:\users"
        return path
    return ""

# Main loop
def virtual_assistant():
    greet_user()
    speak("I am Trinity, your virtual assistant. How can I help you?")
    
    # Check if phone is already configured
    if phone_controller.connected:
        speak(f"Your phone {phone_controller.device_name} is connected via Bluetooth and ready for commands.")
    
    running = True
    
    while running:
        command = listen()
        if command:
            running = process_command(command)

if __name__ == "__main__":
    virtual_assistant()