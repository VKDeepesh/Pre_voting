import tkinter as tk
from tkinter import messagebox
from imutils.video import VideoStream
import face_recognition
import cv2
import pickle
import datetime
import numpy as np
import serial
import time
import paho.mqtt.client as paho  		    #mqtt library
import os
import json
import time
#from datetime import datetime

ACCESS_TOKEN='6QPsI9aRDt28gKgwuDTN'                 #Token of your device
broker="demo.thingsboard.io"   			    #host name
port=1883 					    #data listening port

def on_publish(client,userdata,result):             #create function for callback
    print("data published to thingsboard \n")
    pass
client1= paho.Client("control1")                    #create client object
client1.on_publish = on_publish                     #assign function to callback
client1.username_pw_set(ACCESS_TOKEN)               #access token from thingsboard device
client1.connect(broker,port,keepalive=60)           #establish connection

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition System")

        self.reward_points = {}  # Dictionary to store reward points for each face
        self.serial_port = serial.Serial("COM6", 115200, timeout=1)  # Change COM6 to your ESP8266 port

        self.title_label = tk.Label(root, text="Face Recognition System", font=("Helvetica", 20))
        self.title_label.pack(pady=10)

        self.start_camera_button = tk.Button(root, text="Start Camera", command=self.start_camera)
        self.start_camera_button.pack(pady=20)

        self.camera = None
        self.capture_button_list = []

        self.last_face_detected_time = None
        self.camera_status = False  # To keep track of camera status

        self.check_servo_timeout()  # Initial call

    def start_camera(self):
        self.camera = VideoStream(src=0, framerate=10).start()

        self.start_camera_button.config(state=tk.DISABLED)  # Disable the button after starting the camera
        self.camera_status = True  # Set camera status to True when the camera is started

        self.capture_button_list = []  # Reset the capture buttons

        # Main loop for face recognition
        while self.camera_status:
            frame = self.camera.read()
            frame = cv2.resize(frame, (640, 480))  # Resize the frame

            faces = face_recognition.face_locations(frame)
            if faces:
                for face in faces:
                    self.process_face(frame, face)
            else:
                # No face detected, check servo timeout
                self.check_servo_timeout()

            cv2.imshow("Face Recognition", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cv2.destroyAllWindows()
        self.camera.stop()
        self.start_camera_button.config(state=tk.NORMAL)  # Enable the button after stopping the camera

    def process_face(self, frame, face_location):
        encoding = face_recognition.face_encodings(frame, [face_location])[0]

        # Load the known faces and embeddings
        data = pickle.loads(open("encodings.pickle", "rb").read())

        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(data["encodings"], encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            name = data["names"][best_match_index]

            if self.last_face_detected_time is None or name != self.last_face_name:
                # Different face detected or first detection, update reward points
                self.last_face_name = name
                self.last_face_detected_time = datetime.datetime.now()
                self.reward_points[name] = self.reward_points.get(name, 0) + 1

                # Check if a button for this person already exists
                if name not in [button_name for button_name, _ in self.capture_button_list]:
                    self.create_capture_button(name)
                else:
                    self.update_capture_button(name)

                # Send command to ESP8266 to open the servo
                self.serial_port.write(b'O')

    def create_capture_button(self, name):
        button = tk.Button(self.root, text=f"{name} - {self.reward_points[name]} points",
                           command=lambda n=name: self.display_points(n))
        button.pack(pady=5)
        self.capture_button_list.append((name, button))

    def update_capture_button(self, name):
        for button_name, button_widget in self.capture_button_list:
            if name in button_name:
                button_text = f"{name} - {self.reward_points[name]} points"
                button_widget.config(text=button_text)
    def location(self,lat,long):
  
       payload="{"
       payload+="\"Name\":"+str(lat)+","; 
       payload+="\"Rewards\":"+str(long); 
       payload+="}"
       ret= client1.publish("v1/devices/me/telemetry",payload) #topic-v1/devices/me/telemetry
       print("Please check LATEST TELEMETRY field of your device")
       print(payload);
       time.sleep(5)

    def display_points(self, name):
        points = self.reward_points.get(name, 0)
        messagebox.showinfo("Reward Points", f"{name} has {points} points.")
        #while True:
        self.location(name,points)

    def check_servo_timeout(self):
        if self.last_face_detected_time is not None and self.camera_status:
            current_time = datetime.datetime.now()
            elapsed_time = (current_time - self.last_face_detected_time).total_seconds()

            # Check if 5 seconds have passed since the last face detection
            if elapsed_time >= 5:
                # Send command to ESP8266 to close the servo
                self.serial_port.write(b'C')
                self.last_face_detected_time = None

        # Schedule the function call after 1000 milliseconds (1 second)
        self.root.after(1000, self.check_servo_timeout)

    def stop_camera(self):
        self.camera_status = False
    
    

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_camera)  # Handle window close event
    app.start_camera()  # Automatically start the camera
    root.mainloop()
