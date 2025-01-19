from imutils.video import VideoStream
import face_recognition
import cv2
import pickle
import datetime
import numpy as np
import serial
import time
import paho.mqtt.client as paho  # mqtt library
import os
import json

ACCESS_TOKEN = '6QPsI9aRDt28gKgwuDTN'  # Token of your device
broker = "demo.thingsboard.io"  # host name
port = 1883  # data listening port


def on_publish(client, userdata, result):  # create function for callback
    print("data published to thingsboard \n")
    pass


client1 = paho.Client("control1")  # create client object
client1.on_publish = on_publish  # assign function to callback
client1.username_pw_set(ACCESS_TOKEN)  # access token from thingsboard device
client1.connect(broker, port, keepalive=60)  # establish connection


class FaceRecognitionApp:
    def __init__(self):
        self.reward_points = {}  # Dictionary to store reward points for each face
        self.serial_port = serial.Serial("COM6", 115200, timeout=1)  # Change COM6 to your ESP8266 port
        self.last_face_detected_time = None

    def start_camera(self):
        camera = VideoStream(src=0, framerate=10).start()
        self.camera_status = True  # Set camera status to True when the camera is started

        # Main loop for face recognition
        while self.camera_status:
            frame = camera.read()
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
        camera.stop()

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

                # Send command to ESP8266 to open the servo
                self.serial_port.write(b'O')

                # Send data to thingsboard
                self.location(name, self.reward_points[name])

    def location(self, lat, long):
        payload = "{" + \
                  "\"Name\":" + str(lat) + "," + \
                  "\"Rewards\":" + str(long) + \
                  "}"
        ret = client1.publish("v1/devices/me/telemetry", payload)  # topic-v1/devices/me/telemetry
        print("Please check LATEST TELEMETRY field of your device")
        print(payload)
        time.sleep(5)

    def check_servo_timeout(self):
        if self.last_face_detected_time is not None and self.camera_status:
            current_time = datetime.datetime.now()
            elapsed_time = (current_time - self.last_face_detected_time).total_seconds()

            # Check if 5 seconds have passed since the last face detection
            if elapsed_time >= 5:
                # Send command to ESP8266 to close the servo
                self.serial_port.write(b'C')
                self.last_face_detected_time = None


if __name__ == "__main__":
    app = FaceRecognitionApp()
    app.start_camera()  # Automatically start the camera
