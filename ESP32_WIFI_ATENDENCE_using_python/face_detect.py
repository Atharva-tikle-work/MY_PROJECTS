import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import pandas as pd

# Path where training images are stored
path = 'Training_images'
images = []
classNames = []
myList = os.listdir(path)

# Load training images and extract names
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    
    # Ensure image is loaded correctly
    if curImg is None:
        print(f"Warning: Unable to load image {cl}. Skipping this file.")
        continue
    
    # Log image details for debugging
    print(f"Loaded image: {cl} | Shape: {curImg.shape} | Type: {curImg.dtype}")
    
    # Convert image to RGB (face_recognition expects RGB)
    try:
        curImgRGB = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)
    except Exception as e:
        print(f"Error converting {cl} to RGB: {e}")
        continue

    # Ensure image is a 3D array (RGB) and convert to uint8
    if len(curImgRGB.shape) != 3 or curImgRGB.shape[2] != 3:
        print(f"Warning: Image {cl} is not in RGB format. Converting to RGB.")
        curImgRGB = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)  # Ensure it is RGB
    
    # Convert to uint8 to ensure proper format for face_recognition
    curImgRGB = np.asarray(curImgRGB, dtype=np.uint8)
    
    # Log the converted image details for debugging
    print(f"Converted image: {cl} | Shape: {curImgRGB.shape} | Type: {curImgRGB.dtype}")
    
    # Check pixel values and image depth for any anomalies
    print(f"Pixel values for image {cl}: min={curImgRGB.min()} max={curImgRGB.max()} mean={curImgRGB.mean()}")
    print(f"Image depth for {cl}: {curImgRGB.dtype}")
    
    # Save the image for inspection
    cv2.imwrite(f"converted_{cl}", curImgRGB)  # Save the converted image to inspect it later
    
    images.append(curImgRGB)
    classNames.append(os.path.splitext(cl)[0])

# Function to encode known images
def findEncodings(images):
    encodeList = []
    for img in images:
        # Log image encoding details
        print(f"Encoding image | Shape: {img.shape} | Type: {img.dtype}")
        
        # Ensure the image is in the correct format (RGB)
        if img.ndim == 3 and img.shape[2] == 3:  # Ensure img is in RGB format
            try:
                encode = face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
            except IndexError:
                print("No faces found in image, skipping...")
        else:
            print("Image is not in RGB format.")
    return encodeList

encodeListKnown = findEncodings(images)
print('Encoding Complete')

# Mark attendance function (unchanged)
def markAttendance(name):
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = [line.split(',')[0] for line in myDataList]
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%Y-%m-%d %H:%M:%S')
            f.writelines(f'\n{name},{dtString}')

# Run the video feed and detect faces
ESP32_CAM_URL = 'http://192.168.31.116:81/stream'  # Replace with your ESP32 CAM URL
cap = cv2.VideoCapture(ESP32_CAM_URL)

while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame from ESP32-CAM. Reconnecting...")
        cap = cv2.VideoCapture(ESP32_CAM_URL)
        continue

    # Resize frame for faster processing
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Check the pixel values for the current frame
    print(f"Pixel values for current frame: min={imgS.min()} max={imgS.max()} mean={imgS.mean()}")

    # Try encoding the current frame
    try:
        encode = face_recognition.face_encodings(imgS)[0]
        matches = face_recognition.compare_faces(encodeListKnown, encode)
        faceDis = face_recognition.face_distance(encodeListKnown, encode)
        
        matchIndex = np.argmin(faceDis)
        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            cv2.putText(imgS, name, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            markAttendance(name)
    except IndexError:
        print("No faces found in the current frame.")

    # Display the processed image
    cv2.imshow('ESP32-CAM Face Recognition', imgS)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
