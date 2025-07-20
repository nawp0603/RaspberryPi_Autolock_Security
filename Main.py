import face_recognition
import cv2
import time
import smtplib
import RPi.GPIO as GPIO
import os
import numpy as np
from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import dlib
import pickle

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def bye():
    print("Entry denied")
    GPIO.cleanup()
    exit()

def opendoor(name):
    print("Welcome Home " + name)
    GPIO.output(17, GPIO.HIGH
    sleep(5)
    GPIO.output(17, GPIO.LOW)
    GPIO.cleanup()
    exit()

def takephoto(camera_index=0, save_path="/home/[YOUR_NAME]/shared/guest_image.jpeg"):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Camera not opening")
        sleep(5)
        return
    ret, frame = cap.read()
    if not ret:
        print("Could not capture image")
        sleep(5)
        return
    cv2.imwrite(save_path, frame)
    cap.release()
    print("Photo saved as:", save_path)
    return

def send_notice():
    sender_email = "your_sender_gmail@gmail.com"
    sender_password = "your_password"
    receiver_email = "your_receiver_mail@gmail.com"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Intruder detected."
    msg.attach(MIMEText("An unknown person was detected at your door."))

    image_path = "/home/[YOUR_NAME]/shared/guest_image.jpeg"
    if os.path.exists(image_path):
        with open(image_path, 'rb') as img_file:
            image_data = img_file.read()
        image = MIMEImage(image_data, name=os.path.basename(image_path))
        msg.attach(image)

    server.send_message(msg)
    server.quit()

# Liveliness detection setup
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)

def blink_detection(frame, blink_counter, eye_closed):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    EAR_THRESHOLD = 0.25
    for face in faces:
        landmarks = predictor(gray, face)
        left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
        right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0
        if ear < EAR_THRESHOLD:
            blink_counter += 1
            if blink_counter >= 3:  # Adjust threshold as needed
                eye_closed = True
        else:
            blink_counter = 0
            eye_closed = False

        if eye_closed:
            print("Blink detected, continuing...")
        else:
            print("Eyes open, continue checking...")

    return blink_counter, eye_closed

# Load encoding from enroll_faces2.py output file
encodings_file = "/home/[YOUR_NAME]/shared/seif/face_encodings.pkl"
known_face_encodings, known_face_names = [], []

if os.path.exists(encodings_file):
    with open(encodings_file, 'rb') as f:
        known_face_encodings, known_face_names = pickle.load(f)
    print(f"Loaded {len(known_face_names)} enrolled face(s).")
else:
    print("No enrolled faces found.")
    bye()


reference_name = known_face_names[0]
prev_time = time.time()

blink_counter = 0
eye_closed = False

video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time
    name = "Unknown"

    if GPIO.input(27) == GPIO.HIGH:
        t_end = time.time() + 10
        name = "Unknown"
        while time.time() < t_end:
            ret, frame = video_capture.read()
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.28)
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    blink_counter, eye_closed = blink_detection(frame, blink_counter, eye_closed)
                    if blink_counter >= 1 and not eye_closed:
                        name = known_face_names[best_match_index]
                        opendoor(name)
                        blink_counter = 0

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            cv2.imshow('Camera Feed', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                bye()

        video_capture.release()
        cv2.destroyAllWindows()

        if name == "Unknown":
            takephoto()
            send_notice()
            bye()

GPIO.cleanup()