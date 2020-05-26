from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
import time
import Transmitir
import Conectar
import Centinela
import Speech_recognition
import sys, os
import threading
import pyautogui as pgi
import numpy
import cv2

class Nerf_App(QWidget):    #clase de control y menu

    def __init__(self):
        super().__init__()

        self.ui = loadUi('GUI/nerf_turret.ui', self)  #cargamos fichero UI
        self.show()         #los mostramos por pantalla

        self.comunicacion_abierta = False   #guardamos el serial de la comunicacionn
        self.dial = False                   #true cuando la ventana de conexion se abre
        self.connected = False              #conexion establecida
        self.unity = False                  #conexion con unity
        self.motor_on = False               #encender/apagar motor
        self.exit = False                   #activar boton de salir
        self.velocidad = 253                #velocidad motor maximo 253 por la transmision de bytes
        self.disparar = False               #disparo
        self.activar_voz = False            #actuvar voz
        self.modo_centinela = False         #modo centinela
        self.modo_jugar = False             #modo de juego
        self.on_pad = False                 #true cuando el cursor esta en el pad de movimiento
        self.peticion_voz = 99              #peticiones de voz sin estar conectado, con join del thread

        
        self.transmision = Transmitir.transmision_arduino(self)       #objeto para trnasmision de datos
        self.transmision_unity = Transmitir.transmission_unity(self)  #transmision con unity

        self.pad_label = self.ui.pad_label                       #pad del menu de la aplicacion
        self.conectar_button = self.ui.conectar_button           #boton de conexion
        self.unity_button = self.ui.unity_button                 #boton de conexion unity
        self.motor_on_button = self.ui.motor_on_button           #boton del motor
        self.exit_button = self.ui.exit_button                   #boton de salida
        self.cent_button = self.ui.cent_button                   #boton del modo centinela
        self.disparar_button = self.ui.disparar_button           #boton de disparar
        self.jugar_button = self.ui.jugar_button                 #boton de jugar
        self.voz_button = self.ui.voz_button                     #boton de voz
        
        self.minY = 0               #minimo valor de Y
        self.maxY = 253             #maximo valor de Y
        self.minX = 0               #minimo valor de X
        self.maxX = 253             #maximo valor de X
        self.x = 90                 #coordenada x rango 0-253, inicialmente 90
        self.y = 115                #coordenada y rango 0-253, inicialmente 115
        
        self.leer = ""              #leer mensaje de arduino
        self.unity_message = ""     #mensaje para unity
        self.video_capture = ""     #vairable para captura de imagen

        self.height = 0 #medidas de la captura
        self.width = 0
        
        self.conectar_button.clicked.connect(self.conectar_arduino)  #llamar a la funcion al clickar en boton conectar
        self.unity_button.clicked.connect(self.conectar_unity)  #llamar a la funcion al clickar en boton conectar
        self.motor_on_button.clicked.connect(self.motor_on_off)      #llamar a la funcion al clickar en boton motores
        self.disparar_button.clicked.connect(self.disparar_on)       #llamar a la funcion al clickar en boton disparar
        self.jugar_button.clicked.connect(self.jugar_on)             #llamar a la funcion al clickar en boton disparar
        self.voz_button.clicked.connect(self.voz_on)                 #llamar a la funcion al clickar en boton voz
        self.cent_button.clicked.connect(self.centinela_on)          #llamar a la funcion al clickar en boton centinela
        self.exit_button.clicked.connect(self.exit_app)              #cerramos la aplicacon al clickar en boton salir

        self.voz = Speech_recognition.controlVoz(self)  #objeto de la clase de voz
        self.centinela = Centinela.modoVigilar(self)    #creamos objeto de la clase centinela
        


        
    def centinela_on(self):
        self.modo_centinela = self.cent_button.isChecked()
        
        #modo centinela desactiva boton de jugar, disparar y motor, y enciende motor
        if self.modo_centinela == True:
            self.disparar_button.setEnabled(False)
            self.motor_on_button.setEnabled(False)
            self.jugar_button.setEnabled(False)
            self.motor_on = True
            
            
        #no hay modo centinela, motores on por defecto, se puede disparar
        else:
            self.disparar_button.setEnabled(True)
            self.jugar_button.setEnabled(True)
            self.jugar_button.setChecked(False)
            self.modo_jugar = False
            self.motor_on_button.setEnabled(True)
            self.motor_on_button.setChecked(True)
            
        #self.unity_message = "C@%d&" %self.modo_centinela
        self.enviar_mensaje()
        
    def jugar_on(self):
        self.modo_jugar = self.jugar_button.isChecked()
        #modo jugar desactiva boton de centinela, disparar y motor, y enciende motor
        if self.modo_jugar == True:
            self.disparar_button.setEnabled(False)
            self.motor_on_button.setEnabled(False)
            self.cent_button.setEnabled(False)
            self.motor_on = True
            
        #no hay modo jugar, motores on por defecto, se puede disparar
        else:
            self.disparar_button.setEnabled(True)
            self.cent_button.setEnabled(True)
            self.cent_button.setChecked(False)
            self.modo_centinela = False
            self.motor_on_button.setEnabled(True)
            self.motor_on_button.setChecked(True)
            
        #self.unity_message = "C@%d&" %self.modo_centinela
        self.enviar_mensaje()    
            
                
    #salir de la aplicacion si estamos conectados
    def exit_app(self):
        if self.connected == True:
            if self.unity == True:
                self.transmision_unity.exit_socket()
            else:
                #apagamos motores
                self.motor_on = False
                message = bytes([255, self.x, self.y, self.motor_on, self.velocidad, self.disparar, 254])
                self.transmision.send_message(message)
                self.video_capture.release()
            cv2.destroyAllWindows()
        sys.exit(1)
        os._exit(1)
        sys.exit(app.exec_())
        

    #conectarse con arduino
    def conectar_arduino(self):    
        if not self.connected and not self.dial:
            dial_box = Conectar.establecerConexion(self, False)
            dial_box.show()

    #conectarse con arduino
    def conectar_unity(self):    
        if not self.connected and not self.dial:
            Conectar.establecerConexionUnity(self)

              
    #orden de disparar
    def disparar_on(self):
        #si el motor esta encendido disparamos
        if self.motor_on:
            self.disparar = self.disparar_button.isChecked()
            self.unity_message = "D@%d&" %self.disparar
            self.enviar_mensaje()
            #esperamos 100ms para volver a tener el disparo disponible
            time.sleep(1/10)
            self.disparar = False
            self.disparar_button.setChecked(False)
            self.unity_message = "D@%d&" %self.disparar
            self.enviar_mensaje()

    def voz_on(self):
        self.activar_voz = self.voz_button.isChecked()
        if self.activar_voz == True:
            voz_thread = threading.Thread(target=lambda:self.voz.iniciar())
            voz_thread.start()          
            if self.connected == False: 
                voz_thread.join()
                if self.peticion_voz == 0:
                    self.peticion_voz = 99
                    self.exit_app()
                if self.peticion_voz == 4:
                    self.peticion_voz = 99
                    Conectar.establecerConexion(self, True)
                if self.peticion_voz == 6:
                    self.peticion_voz = 99
                    Conectar.establecerConexionUnity(self)

                      
    #cambiamos menu una vez conectado
    def set_ui(self):  
        if self.unity == True:
            new_button_img = QIcon('GUI/unity_on.png')
            self.unity_button.setIcon(new_button_img)
            self.conectar_button.setEnabled(False)

        else:
            new_button_img = QIcon('GUI/conexion_on.png')
            self.conectar_button.setIcon(new_button_img)
            self.unity_button.setEnabled(False)

        self.motor_on_button.setEnabled(True)
        self.cent_button.setEnabled(True)
        self.jugar_button.setEnabled(True)
        self.pad_label.setEnabled(True)
            
    #envio de mensajes
    def enviar_mensaje(self):
        if self.connected:
            if self.unity == False:
                message = bytes([255, self.x, self.y, self.motor_on,self.velocidad, self.disparar, 254])
                self.transmision.send_message(message)
            else:
                self.transmision_unity.send_unity_message(self.unity_message)
            
    #apagar/encender motor
    def motor_on_off(self):
        if self.connected:
            self.motor_on = self.motor_on_button.isChecked()
            #self.unity_message = "D@%d&" %self.motor_on
            self.enviar_mensaje()
            if self.motor_on == True:
                self.disparar_button.setEnabled(True)
            else:
                self.disparar_button.setEnabled(False)
            
    #mover servos eje x y eje y con el raton sobre el pad
    def mouseMoveEvent(self, event):
        if self.modo_centinela == False and self.modo_jugar == False:
            if (69<event.x()<541 and 69<event.y()<541): #si el cursor esta encima del pad
                #calculamos los nuevos X/Y de 0 a 253 con los limites del pad
                #hacemos una funcion de map igual que la que hay en arduino
                self.x = int(self.mapFuncion(event.x(),70, 540, self.minX, self.maxX ))
                self.y = int(self.mapFuncion(event.y(),70, 540, self.minY, self.maxY ))
                self.on_pad = True
                self.unity_message = "M@"+str(self.x)+","+str(self.y)+"&"
            else:
                #si salimos del pad todo a false
                self.on_pad = False
                self.disparar = False
            #enviamos los nuevos ejes
            self.enviar_mensaje()
        
    #funcion map igual a la que se implementa en arduino
    def mapFuncion(self, valor, in_min, in_max, out_min, out_max):
      return (valor - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    #disparar
    def mousePressEvent(self, event):
        if self.modo_centinela == False and self.modo_jugar == False:
            #comprovamos si estamos dentro del pad y lso motores estan on 
            #la comprovacion de motores se hace en arduino tambien
            if self.on_pad and self.motor_on:
                #al hacer click ponemos el disparo a true y enviamos el mensaje
                self.disparar_button.setChecked(True)
                self.disparar = True
                self.unity_message = "D@%d&" %self.disparar
                self.enviar_mensaje()
                time.sleep(1/10)

    #volver a poner la variable de disparo a false despues del click
    def mouseReleaseEvent(self, event):
        if self.on_pad:
            self.disparar = False
            self.disparar_button.setChecked(False)
            self.unity_message = "D@%d&" %self.disparar
            self.enviar_mensaje()


    def iniciar(self):
        
        if self.unity == True:
            self.video_capture = pgi
        else:
            self.video_capture = cv2.VideoCapture(0)
            #capturamos a 30 frames por segundo
            self.video_capture.set(cv2.CAP_PROP_FPS, 30)
        
        while True:

            if self.unity == True:
                frame = self.video_capture.screenshot(region=(0,0, 754, 500))
                frame=numpy.array(frame)
                frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB) 
            else:
                # Capturamos los frames
                ret, frame = self.video_capture.read()
            
            self.height, self.width, _ = frame.shape
            
            if self.modo_centinela == True:
                processed_img = self.centinela.image_process(frame)
                
                if self.centinela.cara_detectada == True:
                    self.centinela.aviso_mascarilla()
                
                if self.centinela.cara_fijada == True and self.centinela.mascarilla == False:
                    self.centinela.secuencia_disparo()
                else:
                    self.centinela.sec_disparo_cont = self.centinela.sec_disparo #reiniciamos secuencia
                # Enviamos mensaje de las nuevas coordenadas
                self.unity_message = "M@"+str(self.x)+","+str(self.y)+"&"
                self.enviar_mensaje()
                    
                
                #mostramos la imagen 
                cv2.imshow('Video', processed_img[:, :, ::-1])
            elif self.modo_jugar == True:
                #llamamos a la funcion de jugar
                frame = self.centinela.jugar(frame)
                
                # Enviamos mensaje de las nuevas coordenadas
                self.unity_message = "M@"+str(self.x)+","+str(self.y)+"&"
                self.enviar_mensaje()
                
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Nerf_App()
    app.exec_()



            