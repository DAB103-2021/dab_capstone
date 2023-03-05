import numpy as np
import pandas as pd
import pyodbc as pyodbc
import face_recognition as face_recognition
from PIL import Image   #Python Imaging Library
import io
import cv2
from matplotlib import pyplot as plt
import imutils
import easyocr
import pytesseract

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'



auth_id = 1

cnxn = pyodbc.connect(driver='{SQL Server}', server='DESKTOP-9KO479H\SQLEXPRESS', database='facerecognition',trusted_connection='yes')
cursor = cnxn.cursor()


cursor.execute("SELECT vAuthImage from dr_vh_auth where authentication_id = ?",(auth_id)) 
for row in cursor:
    print("***********************************")
    print("copying vehicle image from dr_vh_auth ")
    driver_authentication_image = row[0]
    driver_authentication_image_data = driver_authentication_image

da_image = Image.open(io.BytesIO(driver_authentication_image_data))
da_image.save("vehicleToAuthenticate.jpg")




# Read the image file
im = cv2.imread('vehicleToAuthenticate.jpg')
imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
plt.imshow(cv2.cvtColor(imgray, cv2.COLOR_BGR2RGB))
#plt.show()

bfilter = cv2.bilateralFilter(imgray, 11, 17, 17) #Noise reduction
#canny_edge = cv2.Canny(bfilter, 30, 200) #Edge detection
#plt.imshow(cv2.cvtColor(canny_edge, cv2.COLOR_BGR2RGB))
#plt.show()

ret, thresh = cv2.threshold(imgray, 127, 255, 0)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours=sorted(contours, key = cv2.contourArea, reverse = True)[:50]

#cv2.drawContours(im, contours, -1, (0,255,0), 3)
#plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
#plt.show()




location = None
for contour in contours:
    approx = cv2.approxPolyDP(contour, 10, True)
    if len(approx) == 4:
        location = approx
        break


#print(location)


mask = np.zeros(imgray.shape, np.uint8)
new_image = cv2.drawContours(mask, [location], 0,255, -1)
new_image = cv2.bitwise_and(im, im, mask=mask)
plt.imshow(cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB))
#plt.show()

(x,y) = np.where(mask==255)
(x1, y1) = (np.min(x), np.min(y))
(x2, y2) = (np.max(x), np.max(y))
cropped_image = imgray[x1:x2+1, y1:y2+1]


cropped_image = cv2.bilateralFilter(cropped_image, 10, 10, 10)
(thresh, cropped_image) = cv2.threshold(cropped_image, 150, 180, cv2.THRESH_BINARY)

plt.imshow(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
plt.show()


print("*************2**********************")
text = pytesseract.image_to_string(cropped_image,config='--psm 1')
print("*************3**********************", text)

reader = easyocr.Reader(['en'])
result = reader.readtext(cropped_image,paragraph="False")
print("*************4**********************", result)

print(" cc" , result[0][1])


cursor.execute("UPDATE dr_vh_auth SET vAuthImage_Status = ? , vNum = ? WHERE authentication_id = ?", ("Success",result[0][1] ,auth_id))

cnxn.commit()

cnxn.close()