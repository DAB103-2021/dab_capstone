import easyocr
import cv2
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import pytesseract
import os
from os import listdir
import pyodbc as pyodbc
from PIL import Image   #Python Imaging Library
import io
import imutils
import re

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
cnxn = pyodbc.connect(driver='{SQL Server}', server='DESKTOP-9KO479H\SQLEXPRESS', database='facerecognition',trusted_connection='yes')
cursor = cnxn.cursor()

def authenticateVehicle(auth_id):

    cursor.execute("SELECT vAuthImage from dr_vh_auth where authentication_id = ?",(auth_id)) 
    for row in cursor:
       print("***********************************")
       print("copying vehicle image from dr_vh_auth ")
       driver_authentication_image = row[0]
       driver_authentication_image_data = driver_authentication_image

    da_image = Image.open(io.BytesIO(driver_authentication_image_data))
    da_image.save("vehicleToAuthenticate.jpg")
    
    # Read the image file
    image = cv2.imread('vehicleToAuthenticate.jpg')
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image,allowlist = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    print(result)
    box_arr = []
    size = 0
    text = ''
    for (bbox, text, prob) in result:
        (tl, tr, br, bl) = bbox
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))
        size_box = (int(br[0])- int(tl[0]))*(int(br[1]) -int(tl[1]))
        if size_box >= size:
            curr_box = [tl,br,(int(br[0])- int(tl[0]))*(int(br[1]) -int(tl[1])) ]
            box_arr = curr_box
            size = size_box
            display_text = text
   
    #print(box_arr)
    #print(display_text)
    cv2.rectangle(image, box_arr[0], box_arr[1], (0, 255, 0), 1)
    #cv2.putText(image, display_text, (tl[0], tl[1] - 2),cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0),1)
    #plt.rcParams['figure.figsize'] = (16,16)
    #plt.imshow(image)
    #plt.show()
    x0 = box_arr[0][0]
    y0 = box_arr[0][1]
    x1 = box_arr[1][0]
    y1 = box_arr[1][1]

    cropped_img =  image[y0:y1-5, x0:x1-5]
    #plt.imshow(cropped_img)
    #plt.show()

    reader = easyocr.Reader(['en'])
    result = reader.readtext(cropped_img,paragraph="False")
    print("*************4**********************", result)
    veh_number = re.sub(r'\W+', '',  result[0][1])
    print(" Easy OCR detected the number as: " ,veh_number )

    cursor.execute("UPDATE dr_vh_auth SET vAuthImage_Status = ? , vNum = ? WHERE authentication_id = ?", ("Success",veh_number ,auth_id))
    cnxn.commit()
    return veh_number 