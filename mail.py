import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import datetime
import cv2
import openpyxl
import RPi.GPIO as GPIO

# SMTP email configuration (configure these settings with your email provider)
smtp_server = "smtp.example.com"
smtp_port = 587
smtp_username = "your_email@example.com"
smtp_password = "your_password"
sender_email = "your_email@example.com"
receiver_email = "recipient@example.com"

# Initialize LED (connect it to a GPIO pin)
GPIO.setmode(GPIO.BCM)
LED_PIN = 18
GPIO.setup(LED_PIN, GPIO.OUT)

# Function to capture and save a photo
def capture_photo():
    photo_path = "/path/to/photo.jpg"  # Change to your desired photo path
    os.system(f"raspistill -o {photo_path}")
    return photo_path

# Function to send an email with a photo attachment
def send_email(subject, body, attachment_path):
    msg = MIMEMultipart()
    msg.attach(MIMEText(body, "plain"))

    with open(attachment_path, "rb") as fp:
        img = MIMEImage(fp.read())
    msg.attach(img)

    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Email could not be sent: {str(e)}")

# Open the Excel workbook using openpyxl
workbook = openpyxl.load_workbook(r'C:\Users\police\Desktop\facerecognition in raspberry pi\attendance.xlsx')
sheet = workbook.active

# Initialize 'currentname' to trigger only when a new person is identified.
currentname = "unknown"
# Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings.pickle"

# load the known faces and embeddings along with OpenCV's Haar cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())

# Initialize video stream and allow the camera sensor to warm up
vs = VideoStream(src=0, framerate=10).start()
time.sleep(2.0)

# Start the FPS counter
fps = FPS().start()

# Dictionary to store the last recorded time for each face
last_recorded_time = {}

# Loop over frames from the video file stream
while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=500)
    boxes = face_recognition.face_locations(frame)
    encodings = face_recognition.face_encodings(frame, boxes)
    names = []

    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"

        if True in matches:
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            name = max(counts, key=counts.get)

            if currentname != name:
                currentname = name
                print("name", currentname)

                current_time = datetime.datetime.now()

                if (
                    name not in last_recorded_time
                    or (current_time - last_recorded_time[name]).total_seconds() >= 24 * 60 * 60
                ):
                    row = [name, current_time.strftime("%Y-%m-%d"), current_time.strftime("%H:%M:%S")]
                    sheet.append(row)

                    last_recorded_time[name] = current_time

                    if name == "Unknown":
                        photo_path = capture_photo()
                        send_email("Unknown Face Detected", "An unknown face was detected. See attached photo.", photo_path)
                    else:
                        GPIO.output(LED_PIN, GPIO.HIGH)
                else:
                    GPIO.output(LED_PIN, GPIO.LOW)

        names.append(name)

    for ((top, right, bottom, left), name) in zip(boxes, names):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 225), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow("Facial Recognition is Running", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    fps.update()
    workbook.save(r'C:\Users\police\Desktop\facerecognition in raspberry pi\attendance.xlsx')

fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

cv2.destroyAllWindows()
vs.stop()
