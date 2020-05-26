# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
import serial
import socket
import threading

#modulo para establecer la conexion con arduino
class establecerConexion(QWidget):    

    def __init__(self, parent, auto):
        super().__init__()
        self.parent = parent
        
        self.auto = auto

            
        self.ui = loadUi('GUI/dial.ui', self)

        self.COMportlineEdit = self.ui.COMportlineEdit
        self.connect_button = self.ui.connect_button
        if self.auto == True:
            self.conexion_auto()
        else:
        #comprovamos que se pueda establacer la conexion(no estamos conectados ya)
            self.parent.dial = True
            self.connect_button.clicked.connect(self.check_if_can_connect)
            

            
    def conexion_auto(self):
        port = "COM2"
        try:
            #comprovamos el puerto introducido, por defecto COM2
            self.parent.comunicacion_abierta = serial.Serial(port, 9600)
            print("Conectar con el puerto: ", port)
            self.parent.connected = True
            self.parent.set_ui()
            msj = threading.Thread(target=lambda:self.parent.voz.hablar('Conexión con el robot establecida'))
            msj.start()    
            
            self.parent.iniciar()     #iniciamos centinela

        except:
            #excepcion de salida
            if self.parent.connected == True:
                self.parent.exit_app()
                
            self.parent.voz.hablar("Error al conectarse con el robot")
            print("No es posible conectarse a este puerto")
            return False
            
    def check_if_can_connect(self):
        port = self.COMportlineEdit.text()
        try:
            #comprovamos el puerto introducido, por defecto COM2
            self.parent.comunicacion_abierta = serial.Serial(port, 9600)
            print("Conectar con el puerto: ", port)
            self.parent.connected = True
            self.parent.set_ui()
            self.close()
            self.parent.iniciar()     #iniciamos centinela

        except:
            #excepcion de salida
            if self.parent.connected == True:
                self.parent.exit_app()
                
            self.COMportlineEdit.setText("Imposible conectar")
            print("No es posible conectarse a este puerto")
            return False

    #volvemos a poner a false la ventana de conexion
    def closeEvent(self, event):
        self.parent.dial = False
        
class establecerConexionUnity():
    def __init__(self, parent):
        super().__init__()
        
        self.parent = parent
        self.conectar()
        
    def conectar(self):
        try:
            self.parent.comunicacion_abierta = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.parent.comunicacion_abierta.connect(('127.0.0.1', 13000))
            self.parent.unity = True
            self.parent.connected = True
            self.parent.set_ui()
            self.parent.iniciar()     #iniciamos centinela


        except:
            #excepcion de salida
            if self.parent.connected == True:
                self.parent.exit_app()
            print("Imposible conectarse con Unity")
            self.parent.voz.hablar("Error al conectar con Unity")
            self.parent.unity_button.setChecked(False)
            return False

    