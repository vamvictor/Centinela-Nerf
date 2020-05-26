import numpy as np
from PIL import Image
import cv2
import pickle
import math


def find_face(image_to_check, max_target_distance):
        
    dueño = False
    gray = cv2.cvtColor(image_to_check, cv2.COLOR_BGR2GRAY) #convert image to black and white
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trainner.yml")
        
    labels = {}
    with open("labels.pickle", 'rb') as f:
        og_labels = pickle.load(f)
        labels = {v:k for k,v in og_labels.items()}

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)     #look for faces
    
    for (x,y,w,h) in faces:
        roi_gray = gray[y:y+h, x:x+w]        
        roi_color = image_to_check[y:y+h, x:x+w]
        id_, conf = recognizer.predict(roi_gray)
        font = cv2.FONT_HERSHEY_SIMPLEX
        name = labels[id_]
        color = (255, 255, 255)
        stroke = 2
        cv2.putText(image_to_check,  name, (x, y), font, 1, color, stroke, cv2.LINE_AA)
            
        stroke = 2
        end_cord_x = x + w
        end_cord_y = y + h
        
        #if (name != "No_Mascarilla"):
        if (name != "desconocidos"):
            color = (0, 255, 0)
            dueño = True
        else:
            color = (0, 0, 255)
            dueño = False
        cv2.rectangle(image_to_check, (x,y), (end_cord_x, end_cord_y), color, stroke)
            
    if len(faces) >= 1: #if face(s) detected
        faces = list(faces)[0] #if several faces found use the first one

        x = faces[0]
        y = faces[1]
        w = faces[2]
        h = faces[3]
            
        center_face_X = int(x + w / 2)
        center_face_Y = int(y + h / 2)
        height, width, channels = image_to_check.shape
        
        distance_from_center_X = (center_face_X - width/2)/220 # why? can't remember why I did this
        distance_from_center_Y = (center_face_Y - height/2)/195 # why?
    
        target_distance = math.sqrt((distance_from_center_X*220)**2 + (distance_from_center_Y*195)**2) # calculate distance between image center and face center
    
        if target_distance < max_target_distance :#set added geometry colour
            locked = True
            color = (0, 255, 0)
        else:
            locked = False
            color = (0, 0, 255)
    
        cv2.rectangle(image_to_check,(center_face_X-10, center_face_Y), (center_face_X+10, center_face_Y),    #draw first line of the cross
                          color, 2)
        cv2.rectangle(image_to_check,(center_face_X, center_face_Y-10), (center_face_X, center_face_Y+10),    #draw second line of the cross
                          color,2)
    
        cv2.circle(image_to_check, (int(width/2), int(height/2)), int(max_target_distance) , color, 2)    #draw circle
    
        return [True, image_to_check, distance_from_center_X, distance_from_center_Y, locked, dueño]
    
    else:
        return [False]