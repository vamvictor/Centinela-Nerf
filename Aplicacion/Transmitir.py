#modulo para enviar y recibir mensajes con arduino/unity

class transmision_arduino():
    def __init__(self, parent):
        self.parent = parent

    def send_message(self, message):
        self.parent.comunicacion_abierta.write(message)
        
    def read_message(self):
        self.parent.leer = self.parent.comunicacion_abierta.read()

class transmission_unity():
    def __init__(self, parent):
        self.parent = parent

    def send_unity_message(self,message):
        self.parent.comunicacion_abierta.send(str.encode(message))
        
    def exit_socket(self):
        self.parent.comunicacion_abierta.close()