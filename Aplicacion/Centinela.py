import random
import time
import Rec_facial_mascarilla
import IdentificarDiana
import threading
from PyQt5.QtGui import QIcon

class modoVigilar():
    def __init__(self, parent):
        self.parent = parent
        
        self.distancia_fijar = 30       #margen de distancia al centro para considerar la cara fijada
        self.cara_detectada = False     #cara detectada
        self.cara_fijada = False        #la cara esta fijada en el centro
        self.diana_fijada = False
        
        self.iniciar_roam = 20                    #frames sin detectar cara para empezar a buscar
        self.iniciar_cont = self.iniciar_roam     #contador de frames actuales sin detectar
        self.reiniciar_roam = 20                  #frames de pausa para reiniciar nueva busqueda
        self.reiniciar_cont = self.reiniciar_roam #contador frames reiniciar
        self.sec_disparo = 10                     #frames que dura la sec de disparo
        self.sec_disparo_cont = self.sec_disparo  #contador frames disparo
        self.sec_aviso = 50                       #frames para controlar los avisos que se dan
        self.sec_aviso_cont = self.sec_aviso      #contador de aviso
        
        self.roamX = 0 #primera posicion para el roam, la inicial
        self.roamY = 125
        
        #direccion del roam, sentido del incremento
        self.roamX_inc = True
        self.roamY_inc = True

                     
        self.mascarilla = False #detectamos si lleva mascarilla
        
        self.msg=["¡Cuidado! Ponte la mascarilla o abriremos fuego",
                    "Has sido detectado sin mascarilla",
                    "No llevas mascarilla",
                    "Si no usas mascarillas voy a disparar",
                    "La mascarilla es obligatoria, póntela"]
        
        self.msg_ok=["Gracias por utilizar mascarilla", 
                     "Por favor, no te quites la mascarilla", 
                     "La mascarilla es muy importante", 
                     "Entre todos evitamos el contagio", 
                     "Juntos venceremos"]



    def image_process(self, img):
        processed_img = Rec_facial_mascarilla.reconocimientoFacial(img, self.distancia_fijar)
        #retorno de la funcion
        #[cara_detectada, image, center_face_X, center_face_Y, locked, class_id]
        #cara_detectada: true si detecta una cara, false si no hay cara
        #image: imagen con los recuadros de la deteccion
                # si se llama a la funcion con draw_result=True sera la original
        #center_face_X: distancia desde el centro a la coordenada X
        #center_face_Y: distancia desde el centro a la coordenada Y
        #locked: True si la cara esta fijada, false si no esta fijada
        #class_id: True si lleva mascara, false si no lleva mascara
        
        #cara detectada
        if(processed_img[0]): 
            self.cara_detectada = True
            
            self.iniciar_cont = self.iniciar_roam  #reset de contadores
            self.reiniciar_cont = self.reiniciar_roam
            
            #si la cara no esta fijada movemos para fijarla
            self.cara_fijada = processed_img[4]
            if self.cara_fijada == False:
                self.fijar(processed_img[2], processed_img[3])
            
            #si no lleva mascarilla
            self.mascarilla = processed_img[5]
            
            return processed_img[1]
        
        #no hay cara detectada
        else:
            self.cara_detectada = False
            self.cara_fijada = False
            self.mascarilla = False
            
            #control del roaming
            if self.iniciar_cont> 0:
                self.iniciar_cont -= 1      #decrementamos contador
            else:
                self.roam()                 #cuando llegue a 0 iniciamos el roaming
            
            return processed_img[1]
        
    def jugar(self, frame):
        if self.parent.turno_robot == True:
            processed_img = IdentificarDiana.detectarDiana(frame)
            #retorno de la funcion
            # [frame, centro, centro_x, centro_y, locked]
            #frame: imagen con los recuadros de la deteccion
            #centro: True si se encuentra la diana, False si no hay
            #centro_x: coordenada x del centro de la diana
            #centro_y: coordenada y del centro de la diana
            #locked: True si la diana esta fijada, false si no esta fijada
            
            #si tenemos la ajustamos
            if processed_img[1] == True:
                self.diana_fijada = processed_img[4]
                if self.diana_fijada == False:
                    self.fijar(processed_img[2], processed_img[3])
                else:
                    self.parent.y += 10
                    self.parent.unity_message = "M@"+str(self.parent.x)+","+str(self.parent.y)+"&"
                    self.parent.enviar_mensaje()
                    time.sleep(2/10)
            
                    self.parent.disparar = True
                    self.parent.unity_message = "D@%d&" %self.parent.disparar
                    self.parent.enviar_mensaje()
                    #esperamos 100ms para volver a tener el disparo disponible
                    time.sleep(1/10)
                    self.parent.disparar = False
                    self.sec_disparo_cont = self.sec_disparo
                    self.parent.enviar_mensaje()
                    self.parent.turno_robot = False
                    self.parent.disparar_button.setEnabled(True)
                    self.parent.turno_button.setIcon(QIcon('GUI/turno_on.png'))

            return processed_img[0]
        else:
            return frame
        
    def fijar(self, distance_X, distance_Y):

        velocidad = 2
        velocidadX = 3
        velocidadY = 3
        if distance_X > 0:
            self.parent.x += velocidadX
            #self.parent.x += int(self.parent.mapFuncion(distance_X,0, self.width, self.parent.minX, self.parent.maxX))
        elif distance_X < 0:
            self.parent.x -= velocidadX
            #self.parent.x -= int(self.parent.mapFuncion(abs(distance_X),0, self.width, self.parent.minX, self.parent.maxX))

        if distance_Y > 0:
            self.parent.y -= velocidadY
            #self.parent.y += int(self.parent.mapFuncion(distance_Y,0, self.height, self.parent.minY, self.parent.maxY))
        elif distance_Y < 0:
            self.parent.y += velocidadY
            #self.parent.y -= int(self.parent.mapFuncion(abs(distance_Y),0, self.height, self.parent.minY, self.parent.maxY))
  
        if self.parent.x > 253:
            self.parent.x = 253
        elif self.parent.x < 0:
            self.parent.x = 0
            
        if self.parent.y > 253:
            self.parent.y = 253
        elif self.parent.y < 0:
            self.parent.y = 0
    
    def roam(self):

        #vamos de lado a lado
        velocidadX = 2
        velocidadY = 8
        
        if self.roamX_inc == True:
            self.roamX +=velocidadX
        else:
            self.roamX -=velocidadX
            
        if self.roamY_inc == True:
            self.roamY +=velocidadY
        else:
            self.roamY -=velocidadY
                 
        if self.roamX > 253:
            self.roamX = 253
            self.roamX_inc = False
        elif self.roamX < 0:
            self.roamX = 0
            self.roamX_inc = True
            
        if self.roamY > 200:
            self.roamY = 200
            self.roamY_inc = False
        elif self.roamY < 50:
            self.roamY = 50
            self.roamY_inc = True
        

        self.parent.x = self.roamX 
        self.parent.y = self.roamY
        
    
    def roamAleatorio(self):
        #velocidad del roam
        velocidad_roam = 6
        #hemos llegado al obejtivo en las coordenadas
        objX = False
        objY = False
        
        if self.reiniciar_cont < 0 :                        #contador de frames
            self.reiniciar_cont = self.reiniciar_roam            #reset del contador
            
            #posicion a la random a la que llegar
            self.roamX = int(random.uniform(self.parent.minX+velocidad_roam, self.parent.maxX-velocidad_roam))
            self.roamY = int(random.uniform(self.parent.minY+velocidad_roam, self.parent.maxY-velocidad_roam))
            
        else:        
            #si la x/y es mas grande que el objetivo la decrementamos, sino al reves
            if self.parent.x > self.roamX+velocidad_roam-1: 
                self.parent.x -= velocidad_roam
            elif self.parent.x < self.roamX-velocidad_roam+1: 
                self.parent.x += velocidad_roam
            else:
                objX = True
                
            if self.parent.y > self.roamY+velocidad_roam-1: 
                self.parent.y -= velocidad_roam
            elif self.parent.y < self.roamY-velocidad_roam+1: 
                self.parent.y += velocidad_roam
            else:
                objY = True
                
            #si hemos llegado al objetivo, decrementamos el contador
            if objX == True and objY == True:
                self.reiniciar_cont -= 1
                
    def secuencia_disparo(self):

        if self.sec_disparo_cont == 0:
            self.parent.y += 10
            self.parent.unity_message = "M@"+str(self.parent.x)+","+str(self.parent.y)+"&"
            self.parent.enviar_mensaje()
            time.sleep(2/10)
            self.parent.disparar = True
            self.parent.unity_message = "D@%d&" %self.parent.disparar
            self.parent.enviar_mensaje()
            #esperamos 100ms para volver a tener el disparo disponible
            time.sleep(1/10)
            self.parent.disparar = False
            self.sec_disparo_cont = self.sec_disparo
            self.parent.enviar_mensaje()

        self.sec_disparo_cont -= 1
        


    def aviso_mascarilla(self):
        if self.sec_aviso_cont == self.sec_aviso:
            msg_sel = int(random.uniform(0,5))
    
            if self.mascarilla == True:
                sound_thread = threading.Thread(target=lambda:self.parent.voz.hablar(self.msg_ok[msg_sel]))
            else:
                sound_thread = threading.Thread(target=lambda:self.parent.voz.hablar(self.msg[msg_sel]))
            
            sound_thread.start()
            
        self.sec_aviso_cont -= 1
        if self.sec_aviso_cont == 0:
            self.sec_aviso_cont = self.sec_aviso


    """
    def iniciar(self):
        
        if self.parent.unity == True:
            self.video_capture = pgi
        else:
            self.video_capture = cv2.VideoCapture(0)
            #capturamos a 30 frames por segundo
            self.video_capture.set(cv2.CAP_PROP_FPS, 30)
        
        while True:

            if self.parent.unity == True:
                frame = self.video_capture.screenshot(region=(0,0, 754, 500))
                frame=numpy.array(frame)
                frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB) 
            else:
                # Capturamos los frames
                ret, frame = self.video_capture.read()
            
            self.height, self.width, _ = frame.shape
            
            if self.parent.modo_centinela == True:
                processed_img = self.image_process(frame)
                
                if self.cara_detectada == True:
                    self.aviso_mascarilla()
                
                if self.cara_fijada == True and self.mascarilla == False:
                    self.secuencia_disparo()
                else:
                    self.sec_disparo_cont = self.sec_disparo #reiniciamos secuencia
                # Enviamos mensaje de las nuevas coordenadas
                self.parent.unity_message = "M@"+str(self.parent.x)+","+str(self.parent.y)+"&"
                self.parent.enviar_mensaje()
                    
                
                #mostramos la imagen 
                cv2.imshow('Video', processed_img[:, :, ::-1])
            elif self.parent.modo_jugar == True:
                #llamamos a la funcion de jugar
                frame = self.jugar(frame)
                
                # Enviamos mensaje de las nuevas coordenadas
                self.parent.unity_message = "M@"+str(self.parent.x)+","+str(self.parent.y)+"&"
                self.parent.enviar_mensaje()
                
                #mostramos la imagen
                cv2.imshow('Video', frame)
                
            else:
                cv2.imshow('Video', frame)
            
            #boton de salir 's'
            if cv2.waitKey(1) & 0xFF == ord('s'):
                break
            # eliminamos la pantalla de la captura 
        self.video_capture.release()
        cv2.destroyAllWindows()
    
        
    def salir(self):
        if self.parent.unity == False:
            self.video_capture.release()
        cv2.destroyAllWindows()
        sys.exit(1)
    """