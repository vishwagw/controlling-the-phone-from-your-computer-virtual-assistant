# Controlling smartphone via Trinity virtual assistant

This program is a computer AI virtual assistant that is being built by using several AI subfields including Natrual Language Processing, Tesxt-to-Speech etc.

1. Purpose
The major purpose is to control the smart phone via our custom-built AI assistant instead of the built in virtual assistant for your smart phone (Apple: Siri or Android: Google Assistant)

2. Tech stack:
* Python 3x
* speech_recognition
* gTTS or pyttsx3

3. Design:
This application is a modification of basic codebase of trinity.
* Create a new function to handle phone control
* Add detection for phone-related commands in the main  process_command function
* Incorporate a way to communicate with the mobile device

* for the controlling purposes, We have added the controller function.

4. usability:
* Make calls: "Call John" or "Phone Mary"
* Send text messages: "Text Sarah saying I'll be late" or "Send message to Tim"
* Open apps: "Open Instagram app on my phone" or "Launch Spotify on phone"
* Take photos: "Take a photo with my phone"
* Set alarms: "Set an alarm for 7 AM on my phone"
* Check battery level: "Check my phone battery"

4. There are 3 different applications in This repository.
* Using custom mobile server
* Using pybluez PYthon Library
* Using bleak Python library

