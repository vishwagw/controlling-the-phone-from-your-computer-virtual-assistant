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



