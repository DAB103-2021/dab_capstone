import cv2
import dlib
import pyttsx3
from scipy.spatial import distance
from fetchCoordinates import fetchCoordinates
import pyodbc as pyodbc
import datetime

cnxn = pyodbc.connect(driver='{SQL Server}', server='DESKTOP-9KO479H\SQLEXPRESS', database='facerecognition',trusted_connection='yes')
cursor = cnxn.cursor()
cursor.execute('SELECT ISNULL(max(tripId ),0) FROM trips')
trips = cursor.fetchone()
tripId = trips[0] + 1


def drowsyMonitoring(dr_id,dr_name,vh_number):
	dr_id = dr_id
	dr_name = dr_name
	vh_number = vh_number
	print(dr_id,dr_name,vh_number)
	#below function will fetch the coordinates at the start of the trip
	starting_coordinates = fetchCoordinates()
	st_coordinates = str(starting_coordinates[0]) + ',' + str(starting_coordinates[1])
	st = datetime.datetime.now()
	# Initiliazing python pyttsx3 for text to speech conversion
	engine = pyttsx3.init()
	#video capture from webcam (0 is the camera number)
	cap = cv2.VideoCapture(0)
	# initiating dlib liberary for eyes detection
	face_detector = dlib.get_frontal_face_detector()
    #reading the haarcascade file to predict eye shapes.
	#Install dlib to use shape_predictor function. change the path as per the dat file.
	dlib_facelandmark = dlib.shape_predictor("C:\\Users\\sach\\Videos\\prj-101\\proj101\\shape_predictor_68_face_landmarks.dat")
    #Below scipy spatial distance function calculates the euclidean distance on eyes landmark
	def eud_dist(eye_shape):
		point_1 = distance.euclidean(eye_shape[1], eye_shape[5])
		point_2 = distance.euclidean(eye_shape[2], eye_shape[4])
		point_3 = distance.euclidean(eye_shape[0], eye_shape[3])
		eyeAspectRatio = (point_1+point_2)/(2*point_3)
		return eyeAspectRatio
    # This loop detect the drowsyness based on the frames in camera
	while True:
		null, frame = cap.read()
		gray_scale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		faces = face_detector(gray_scale)

		for face in faces:
			face_landmarks = dlib_facelandmark(gray_scale, face)
			leftEye = []
			rightEye = []

			for n in range(42, 48):
				x = face_landmarks.part(n).x
				y = face_landmarks.part(n).y
				rightEye.append((x, y))
				next_point = n+1
				if n == 47:
					next_point = 42
				x2 = face_landmarks.part(next_point).x
				y2 = face_landmarks.part(next_point).y
				cv2.line(frame, (x, y), (x2, y2), (0, 255, 0), 1)

			for n in range(36, 42):
				x = face_landmarks.part(n).x
				y = face_landmarks.part(n).y
				leftEye.append((x, y))
				next_point = n+1
				if n == 41:
					next_point = 36
				x2 = face_landmarks.part(next_point).x
				y2 = face_landmarks.part(next_point).y
				cv2.line(frame, (x, y), (x2, y2), (255, 255, 0), 1)

			#calculate aspect ratio of eye call eud_dist function
			right_Eye = eud_dist(rightEye)
			left_Eye = eud_dist(leftEye)
			Eye_Rat = (left_Eye+right_Eye)/2
			Eye_Rat = round(Eye_Rat, 2)

			# eye_rat value determine the drowsyness of a person ratio can be changed accordingly
			if Eye_Rat < 0.15:
				cv2.putText(frame, "DROWSINESS DETECTED", (50, 100),
							cv2.FONT_HERSHEY_PLAIN, 2, (21, 56, 210), 3)
				cv2.putText(frame, "Danger!!!!", (50, 450),
							cv2.FONT_HERSHEY_PLAIN, 2, (21, 56, 212), 3)

				#below command will create alert sound if the drowsyness is detected and the record will get inserted in database.
				engine.say("Alert!!!! WAKE UP! WAKE UP! ")
				#below function will fetch the coordinates at the drowsyness detection of the trip
				drowsiness_coordinates = fetchCoordinates()
				dt = datetime.datetime.now()
				dateDiff = dt - st
				tripTime = dateDiff.total_seconds()
				trip_id = int(tripId)
				driver_id = int(dr_id)
				drowsiness_detection_time = str(dt)
				dr_coordinates = str(drowsiness_coordinates[0]) + ',' + str(drowsiness_coordinates[1])
				start_time = str(st)
				print(tripId, dr_id,dr_name,vh_number,drowsiness_coordinates,starting_coordinates,start_time,drowsiness_detection_time,tripTime)
				query = f"insert into trips (tripId,dId ,dName ,vNum ,startLoc ,drwsyDetectn ,drwsyLoc ,startTime ,drwsyDetectnTime ,tripTime ) values (?,?,?,?,?,?,?,?,?,?)" 
				print(query)
				cursor.execute(query, (trip_id,driver_id,dr_name,vh_number,st_coordinates,'Y',dr_coordinates,start_time,drowsiness_detection_time, tripTime))
				cnxn.commit()
				engine.runAndWait()
			
		cv2.imshow("Drowsiness detection window", frame)
		key = cv2.waitKey(9)
		if key == 20:
			break
	cap.release()
	cv2.destroyAllWindows()
