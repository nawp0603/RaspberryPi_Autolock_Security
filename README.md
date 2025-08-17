# Implementation of a Raspberry Pi-Powered Real-Time Facial Recognition System for Car Entry Security

Welcome to my project, this project implemented face recognition for car security using edge devices 

This project enhances home/office security by automatically locking/unlocking doors based on facial recognition.

## Features:
- 🔒 Auto lock/unlock with real-time **face recognition**.
- 📷 Works with Raspberry Pi Camera or USB Camera.
- 🖥️ Simple command-line interface (extendable to web/app).
- 📡 Can be integrated with motion sensors and notifications (Telegram/Email).


## Requirements
- Raspberry Pi 4/5 (recommended: Pi 5 + SSD for faster performance).
- Raspberry Pi Camera or USB Camera (1080p).
- Python >= 3.9.
- Single channel isolated relay 5 voltage. 
- A solenoid lock 12 voltage (Can be replaced by a LED).

## How to use:
- Run file enroll_faces_10encodinsg.py to enroll author's face with 10 encodings
- delete_faces.py for deleting all encodings saved.
- Run file main.py for the main program.
