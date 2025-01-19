import os
import csv
from datetime import datetime
import face_recognition
import cv2

# Initialize or append to CSV for logging
csv_file = 'recognition_log.csv'

if not os.path.exists(csv_file):
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'name', 'success', 'fps'])

# Load face encodings and names (replace this with your actual data loading logic)
data = {"encodings": [], "names": []}  # Replace with actual loading logic

# Start video capture (replace with your actual video capture logic)
video_capture = cv2.VideoCapture(0)
fps = cv2.CAP_PROP_FPS

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_frame = small_frame[:, :, ::-1]

    # Find face encodings in the current frame
    encodings = face_recognition.face_encodings(rgb_frame)
    
    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"
        success = 0

        if True in matches:
            # Recognition successful
            success = 1
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1
            name = max(counts, key=counts.get)

        # Log results
        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now(), name, success, fps])

    # Display the video feed
    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
