import speech_recognition as sr
import playsound # Ejecutar archivos de audio
from gtts import gTTS # Transformar texto a audio
import random
import os # Para poder eliminar archivos
import speech_google


class controlVoz():
    def __init__(self, parent):
        self.parent = parent
        self.r = sr.Recognizer()
        
    def iniciar(self):
        self.hablar('¿Qué quieres hacer?')
        self.orden = speech_google.iniciar()
        self.responder()
        self.parent.voz_button.setChecked(False)
                 
    #Aquí añadimos las llamadas a las acciones necesarias o podemos devolver 
    # al controler para que ejecute las acciones necesarias.
    def responder(self):
        if self.orden == 1:
            if self.parent.connected == True:
                if self.parent.modo_jugar == True:
                    self.hablar('Desactiva el modo jugar para activar el centinela')
                elif self.parent.modo_centinela == True:
                     self.parent.cent_button.setChecked(False)
                     self.parent.centinela_on()
                     self.hablar('Modo centinela desactivado')
                else:
                     self.parent.cent_button.setChecked(True)
                     self.parent.centinela_on()
                     self.hablar('Modo centinela activado')
            else:
                self.hablar('Primero debes estar conectado')
                
        if self.orden == 2:
            if self.parent.connected == True:
                if self.parent.modo_centinela == True:
                    self.hablar('El modo centinela tiene el control de los motores')
                if self.parent.modo_jugar == True:
                    self.hablar('El modo jugar tiene el control de los motores')
                elif self.parent.motor_on == True:
                    self.parent.motor_on_button.setChecked(False)
                    self.parent.motor_on_off()
                    self.hablar('Apagando los motores')
                else:
                    self.parent.motor_on_button.setChecked(True)
                    self.parent.motor_on_off()
                    self.hablar('Se han activado los motores')
            else:
                self.hablar('Primero debes estar conectado')
                
        if self.orden == 3:
            if self.parent.connected == True:
                if self.parent.modo_centinela == True:
                    self.hablar('El modo centinela tiene el control de disparo')
                if self.parent.modo_jugar == True:
                    self.hablar('El modo jugar tiene el control de disparo')
                elif self.parent.motor_on == False:
                    self.hablar('Enciende los motores para poder disparar')
                else:
                    self.parent.disparar_button.setChecked(True)
                    self.parent.disparar_on()
            else:
                self.hablar('Primero debes estar conectado')    
                
        if self.orden == 4:
            if self.parent.connected == True:
                self.hablar('Ya estás conectado con el robot')
            else:
                self.parent.peticion_voz = 4

                
        if self.orden == 5:
            if self.parent.connected == True:
                if self.parent.modo_centinela == True:
                    self.hablar('Desactiva el modo centinela para poder jugar')
                elif self.parent.modo_jugar == True:
                    self.parent.jugar_button.setChecked(False)
                    self.parent.jugar_on()
                    self.hablar('Fin de la partida')
                else:
                    self.parent.jugar_button.setChecked(True)
                    self.parent.jugar_on()
                    self.hablar('Empieza el modo de juego')

            else:
                self.hablar('Primero debes estar conectado')    
                
                
        if self.orden == 6:
            if self.parent.connected == True:
                self.hablar('Ya estás conectado con Unity')
            else:
                self.parent.peticion_voz = 6
                
                
        if self.orden == 0:
            self.hablar('¡Hasta la próxima!')
            self.parent.exit_app()

        if  self.orden == 99:
            self.hablar('Lo siento, no te he entendido')

    """
    #Método auxiliar para buscar en una frase
    def there_exists(self, terms):
        for term in terms:
            if term in self.voice_data:
                return True
                
    def grabar_audio(self,):
        self.voice_data = ''
        with sr.Microphone() as source:
            audio = self.r.listen(source);
            try:
                self.voice_data = self.r.recognize_google(audio,None,"es-ES")
            except sr.UnknownValueError:
                self.hablar('Lo siento, no te he entendido.')
            except sr.RequestError:
                self.hablar('Lo siento, el servicio esta apagado.')

    #Aquí añadimos las llamadas a las acciones necesarias o podemos devolver 
    # al controler para que ejecute las acciones necesarias.
    def responder(self):
        
        if 'centinela' in self.voice_data:
            if self.parent.connected == True:
                if self.parent.modo_centinela == True:
                    self.hablar('El modo centinela ya está activado')
                else:
                    self.parent.centinela_on()
                    self.hablar('Modo centinela activado')
            else:
                self.hablar('Primero debes estar conectado')
                
        elif 'motor' in self.voice_data:
            if self.parent.connected == True:
                if self.parent.modo_centinela == True:
                    self.hablar('El modo centinela tiene el control de los motores')
                elif self.parent.motor_on == True:
                    self.hablar('Los motores ya están en funcionamiento')
                else:
                    self.parent.motor_on_button.setChecked(True)
                    self.parent.motor_on_off()
                    self.hablar('Se han activado los motores')
            else:
                self.hablar('Primero debes estar conectado')
                
        elif 'disparar' in self.voice_data:
            if self.parent.connected == True:
                if self.parent.modo_centinela == True:
                    self.hablar('El modo centinela tiene el control de disparo')
                elif self.parent.motor_on == False:
                    self.hablar('Enciende los motores para poder disparar')
                else:
                    self.parent.disparar_on()
            else:
                self.hablar('Primero debes estar conectado')     
        elif self.there_exists(["exit", "hasta luego","adios", "salir"]):
            self.hablar('¡Hasta la próxima!')
            self.parent.exit_app()
    """
    
    def hablar(self, texto_audio):
        tts = gTTS(text=texto_audio, lang='es') # text to speech(voice)
        r = random.randint(1,20000000)
        audio_file = 'mascara' + str(r) + '.mp3'
        tts.save(audio_file) # Guardamos como mp3
        playsound.playsound(audio_file) # Ejecutamos el archivo mp3
        os.remove(audio_file) #Eliminamos el audio
    

