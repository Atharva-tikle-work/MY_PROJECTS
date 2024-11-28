import pandas as pd
import cv2
import urllib.request
import numpy as np
import os
from datetime import datetime
import face_recognition
 
path = 'Training_images'
url='http://192.168.31.116:81/stream'
##'''cam.bmp / cam-lo.jpg /cam-hi.jpg / cam.mjpeg '''
 
attendance_dir = os.path.join(os.getcwd(), 'attendance')
if not os.path.exists(attendance_dir):
    os.makedirs(attendance_dir)

if 'Attendance.csv' in os.listdir(attendance_dir):
    print("there iss..")
    os.remove(os.path.join(attendance_dir, "Attendance.csv"))
else:
    df = pd.DataFrame(list())
    df.to_csv(os.path.join(attendance_dir, "Attendance.csv"))
    
 
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    if curImg is None:
        print(f"Error reading image: {cl}")
        continue  # Skip this image if it cannot be read
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)
 
 
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
        if img is not None and img.ndim == 3:  # Check if image is valid and has 3 channels
            encode = face_recognition.face_encodings(img)
            if encode:  # Check if any encodings were found
                encodeList.append(encode[0])
            else:
                print("No face found in the image.")
        else:
            print("Invalid image format or empty image.")
    return encodeList
 
 
def markAttendance(name):
    with open("Attendance.csv", 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
            if name not in nameList:
                now = datetime.now()
                dtString = now.strftime('%H:%M:%S')
                f.writelines(f'\n{name},{dtString}')
 
 
encodeListKnown = findEncodings(images)
print('Encoding Complete')
 
#cap = cv2.VideoCapture(0)
 
while True:
    #success, img = cap.read()
    img_resp=urllib.request.urlopen(url)
    imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
    img=cv2.imdecode(imgnp,-1)
# img = captureScreen()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
 
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
 
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
# print(faceDis)
        matchIndex = np.argmin(faceDis)
 
        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
# print(name)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            markAttendance(name)
 
    cv2.imshow('Webcam', img)
    key=cv2.waitKey(5)
    if key==ord('q'):
        break
cv2.destroyAllWindows()
cv2.imread