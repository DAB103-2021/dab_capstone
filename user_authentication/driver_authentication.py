
from asyncio.windows_events import NULL
import numpy as np
import pandas as pd
import pyodbc as pyodbc
import face_recognition as face_recognition
from PIL import Image
import io

auth_id = 1

cnxn = pyodbc.connect(driver='{SQL Server}', server='DESKTOP-9KO479H\SQLEXPRESS', database='facerecognition',trusted_connection='yes')
cursor = cnxn.cursor()


cursor.execute("SELECT dAuthImage from dr_vh_auth where authentication_id = ?",(auth_id)) 
for row in cursor:
    print("***********************************")
    print("copying driver image from dr_vh_auth ")
    driver_authentication_image = row[0]
    driver_authentication_image_data = driver_authentication_image

da_image = Image.open(io.BytesIO(driver_authentication_image_data))
da_image.save("driverToAuthenticate.jpg")

known_image = face_recognition.load_image_file("driverToAuthenticate.jpg")
driver_encoding = face_recognition.face_encodings(known_image)[0]

cursor.execute("SELECT count(*) from driverDetails ;") 
for row in cursor:
    print()
    print("driverDetails count = ", row[0])
    forLoopRange = row[0]

status = False
row=[]
for i in range(forLoopRange + 1 ):
    cursor.execute("SELECT * from driverDetails where id =?", (i)) 
    for row in cursor:
        print(i)
        print("Comparing image for Driver Id = ", row[0])
        print("Comparing image for Driver Name = ", row[1])
        driver_image = row[5]
        driver_image_data = driver_image
        dr_image = Image.open(io.BytesIO(driver_image_data))
        dr_image.save("driverToCompare.jpg")
        unknown_image = face_recognition.load_image_file("driverToCompare.jpg")
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        results = face_recognition.compare_faces([driver_encoding], unknown_encoding)
        status = results[0]
        print("Driver image matched = ", results)
    if status == True:
        break
print("Matched Driver Id is= ", row[0])
print("Matched Driver name is= ", row[1])


cursor.execute("UPDATE dr_vh_auth SET dAuthImage_Status = ? , did = ? WHERE authentication_id = ?", ("Success",row[0],auth_id))

cnxn.commit()

cnxn.close()