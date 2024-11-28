import cv2
import numpy as np
import face_recognition
import os
import requests
from datetime import datetime

# ESP32-CAM IP address
esp32cam_ip = "http://192.168.31.116:81/stream"  # Replace with your ESP32-CAM IP


# Path to known images
path = 'Images_Basic'
images = []
classNames = []
mylist = os.listdir(path)
print(mylist)
for cl in mylist:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

# Function to encode known faces
def find_encodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

# Function to mark attendance
def mark_attendance(name):
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')

# Function to send name to ESP32-CAM
def send_to_esp32(name):
    try:
        url = f"{esp32cam_ip}"
        requests.get(url, params={'name': name})
        print(f"Sent {name} to ESP32-CAM")
    except Exception as e:
        print(f"Error sending data to ESP32-CAM: {e}")

# Encode known faces
encodelistknown = find_encodings(images)
print("Encoding Complete!")

# Open video stream
cap = cv2.VideoCapture(esp32cam_feed)

while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame")
        continue

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodelistknown, encodeFace)
        faceDis = face_recognition.face_distance(encodelistknown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            print(name)
            mark_attendance(name)
            send_to_esp32(name)
        else:
            send_to_esp32("UNKNOWN")

        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('ESP32-CAM Feed', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
        break

cv2.destroyAllWindows()
