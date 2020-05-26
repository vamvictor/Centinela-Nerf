import cv2
import numpy as np
import math

def detectarDiana(frame):

    opcion = 1
    #precision de la diana
    max_distancia = 20
    #cv2.imshow('frame entrada',frame)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    #cv2.imshow('imagen gray',gray)

    image = cv2.Canny(gray,100,500)
    #retval, image = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
   # cv2.imshow('canny',image)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(5,5))
    #image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    image = cv2.dilate(image, kernel)
    
    #cv2.imshow('binary',image)

    centro = False
    centro_x = 0
    centro_y = 0
    
    #inicialiamos la variable que detecta si la diana esta apuntada
    locked = False
                
    if opcion == 1:
        # Busca los contornos
        contours, hierarchy = cv2.findContours(image,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
            
        true_centers = []
        centers = []
        radii = []
        pt1 = []
        pt2 = []
        fill = []
        areas = []
            
        detectado = False
        # Miramos los contornos detectados
        for contour in contours:
                
            area = cv2.contourArea(contour)
            # Comprovar el area que ocupa
            if area < 200:
                continue
                
            detectado = True
            fill.append(contour)
            areas.append(area)
               
            br = cv2.boundingRect(contour)        
            
            # Guardar puntos para recrear el overlay
            pt1.append((br[0], br[1]))
            pt2.append((br[0]+br[2], br[1]+br[3]))
            
            radii.append(min(br[2], br[3])/2)        
                
            true_centers.append((br[0]+ (int)(br[2]/2), br[1]+ (int)(br[3]/2)))
                
            m = cv2.moments(contour)
            center = (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
            centers.append(center)
            

        if detectado:
            maxV = 0
            maxIndex = 0
            maxIndex2 = 0
                
            for i in range(len(areas)):
                if areas[i] > maxV:
                    maxV = areas[i]
                    maxIndex2 = maxIndex
                    maxIndex = i
            if maxIndex != 0:
                fill[maxIndex] = None
                
            overlay = frame.copy()
            
            # Buscamos los centros
            if(len(centers)):
                for n in range(len(centers)):           
                    if n != maxIndex2:
                        continue            
                    centro = True
                    centro_x = true_centers[n][0]
                    centro_y = true_centers[n][1]
                    ellip = cv2.fitEllipse(fill[n])            
                    cv2.drawContours(frame, fill, maxIndex2, (255, 255, 255), 1)
                    cv2.ellipse(overlay, ellip, (125, 125, 0), -1)
                    cv2.rectangle(frame, pt1[n], pt2[n], (0, 0, 255), 1, 8, 0)
                    cv2.circle(frame, true_centers[n], 3, (0, 0, 0), -1)
                    cv2.circle(frame, centers[n], 3, (255, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)   
                    cv2.circle(frame, (centro_x, centro_y), 10 ,(0, 0, 0), 2)
                    
                
    if opcion == 2:
        circles	= cv2.HoughCircles(image,cv2.HOUGH_GRADIENT,1,120,param1=100,param2=30,minRadius=50,maxRadius=92)
        if circles is not None:
            centro = True
            overlay = frame.copy()

            circles	= np.uint16(np.around(circles))
            for	i in circles[0,:]:
        		#	draw	the	outer	circle
                cv2.circle(frame,(i[0],i[1]),i[2],(0,255,0),6)
        		#	draw	the	center	of	the	circle
                cv2.circle(frame,(i[0],i[1]),2,(0,0,255),3)
                centro_x = i[0]
                centro_y = i[1]
                cv2.circle(frame, (centro_x, centro_y), 10 ,(0, 0, 255), 2)

    if centro:
        height, width, _ = frame.shape
        
        centro_x = centro_x-(width/2)
        centro_y = centro_y-(height/2)
        distancia = math.sqrt((centro_x**2)+(centro_y**2))
        
        color = (0, 0, 255)
        if distancia < max_distancia:
            locked = True
            color = (0, 255, 0)
        
        cv2.circle(frame, (int(width/2), int(height/2)), int(max_distancia) , color, 2)   

 
    return [frame, centro, centro_x, centro_y, locked]

