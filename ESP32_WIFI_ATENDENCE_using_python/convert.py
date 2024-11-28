from PIL import Image
import os
import cv2
import numpy as np  # Import NumPy

# Path where training images are stored
path = 'Training_images'
images = []
classNames = []
myList = os.listdir(path)

for cl in myList:
    img_path = os.path.join(path, cl)
    try:
        img = Image.open(img_path)
        img = img.convert('RGB')  # Ensure it's in RGB format
        
        # Convert Pillow image to NumPy array
        img_np = np.array(img)
        
        # Convert BGR to RGB using OpenCV
        img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
        
        # Save the image in JPEG format
        new_path = os.path.join(path, os.path.splitext(cl)[0] + '.jpeg')
        cv2.imwrite(new_path, img_rgb)  # Use cv2.imwrite to save the image
    except Exception as e:
        print(f"Error converting image {cl}: {e}")