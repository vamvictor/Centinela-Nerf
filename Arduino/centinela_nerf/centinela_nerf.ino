#include <Servo.h>

//servo disparo
Servo servoDisparo; //declaramos el servo
const int sDISPARO = 3; //pin donde conectar el servo
const byte posCargar = 180; //posicion de reposo del servo de disparo
const byte posDisparar = 125; //posicion a la que llegar para poner la bala en los motores

//control del disparo
bool disparando = false;
bool disparoDisponible = true;
  
//tiempo entre disparos 
const long tiempoDisparo = 150;
const long tiempoRecarga = tiempoDisparo*2;
unsigned long inicioDisparo = 0;
unsigned long tiempoActualDisparo = 0;


//servo eje x
Servo servoX; //declaramos el servo
const int sX = 5; //pin donde conectar el servo
  //limites del eje que puede girar el servo
const byte minX = 0;
const byte maxX = 180;

//servo eje y
Servo servoY; //declaramos el servo
const int sY = 6; //pin donde conectar el servo
  //limites del eje que puede girar el servo
const byte minY = 65;
const byte maxY = 180;

//motor1
const int pinENABLE_1 = 11;
const int pinIN1_1 = 12;
const int pinIN1_2 = 13;

//motor2
const int pinENABLE_2 = 10;
  //Para que vayan a la inversa intercambiar pin
const int pinIN2_1 = 8;
const int pinIN2_2 = 7;

//velocidades
int speed1 = 0; // de 0 a 255 max
int speed2 = 0; // de 0 a 255 max

//booleano para saber si estan encendidos los motores
bool motorON = false;

//control de datos de la comunicacion
byte byte_from_app;
byte bytesRecvd = 0;
boolean data_received = false;
const byte buffSize = 30;
byte inputBuffer[buffSize];
const byte byte_inicio = 255;
const byte byte_final = 254;


void setup()
{
  //unimos el servo con el pin
  servoDisparo.attach(sDISPARO);
  servoX.attach(sX);
  servoY.attach(sY);

  //motor 1
  pinMode(pinENABLE_1, OUTPUT);
  pinMode(pinIN1_1, OUTPUT);
  pinMode(pinIN1_2, OUTPUT);

  //motor 2
  pinMode(pinENABLE_2, OUTPUT);
  pinMode(pinIN2_1, OUTPUT);
  pinMode(pinIN2_2, OUTPUT);
  
  //motores iniciales a 0
  analogWrite(pinENABLE_1, speed1);
  analogWrite(pinENABLE_2, speed2);

   servoX.write(90);
   servoY.write(115);
   servoDisparo.write(posCargar);
   delay(100);

  //iniciamos la comunicacion serial
  Serial.begin(9600);
}

void loop()
{

  getDataFromPC();
  if (data_received) 
  {
    set_motor();
    mover();
    disparar();
  }
  //control velocidad con enable pin analogico
  analogWrite(pinENABLE_1, speed1);
  analogWrite(pinENABLE_2, speed2);
  
  digitalWrite(pinIN1_1, HIGH);
  digitalWrite(pinIN1_2, LOW);
  digitalWrite(pinIN2_1, HIGH);
  digitalWrite(pinIN2_2, LOW);

  //Serial.print("hola");
}

void disparar()
{
  //si llega una accion de disprar, con disparo disponible y motores on
  if (inputBuffer[4] == 1 && disparoDisponible && motorON)
  {
    //estamos disparando y no tenemos disparo disponible
    disparando = true;
    disparoDisponible = false;
    //tiempo inicio disparo
    inicioDisparo = millis();
  }
  //tiempo actual del disparo
  tiempoActualDisparo = millis();

  //si estamos disparando, comparamos el tiempo actual con el inicio, si es mas pequeño que
  //que el tiempo de disparo movemos el servo a la posicion de disparo
  if (disparando && tiempoActualDisparo-inicioDisparo < tiempoDisparo)
  {
    servoDisparo.write(posDisparar);
  }
  //sino, comprobamos si estamos disparando y el tiempo es mas pequeño que la recarga para mover
  //el servo a posicion de recarga
  else if (disparando && tiempoActualDisparo-inicioDisparo < tiempoRecarga)
  {
    servoDisparo.write(posCargar);
  }
  //sino, si estamos disparando y los tiempos superan a la recarga el disparo ha finalizado
  //actualizamos las variables de control de disparo
  else if (disparando && tiempoActualDisparo-inicioDisparo > tiempoRecarga)
  {
    disparando = false;
    disparoDisponible = true;
  }
}



void mover()
{
  byte newX = map(inputBuffer[0], 0, 253, maxX, minX);//convertimos el valor del buffer que llega entre 0 y 253 al rango de X
  servoX.write(newX); //actualizamos posicion servo eje x
  byte newY = map(inputBuffer[1], 0 , 253, maxY, minY);//convertimos el valor del buffer que llega entre 0 y 253 al rango de Y
  servoY.write(newY); //actualizamos posicion servo eje y
}

void set_motor() 
{
  //apagar o encender motores
  if (inputBuffer[2] == 1) //caso de motor encendido
  { 
    if (inputBuffer[3] == 253)      
    {//para aprovechar la maxima velocidad, si llega 253 (valor maximo posible que se puede indiicar)
     //subimos la velocidad de los motores al maximo 255
      speed1 = 255;
      speed2 = 255;
    }
    else 
    {
      //si llega una velocidad distinta a 253 ponemos la velocidad indicada
      speed1 = inputBuffer[3];
      speed2 = inputBuffer[3];
    }
    motorON = true;
  }
  else {  
    //motor apagado, ponemos velocidad a 0                                 
     speed1 = 0;
     speed2 = 0;
     motorON = false;
  }
}


void getDataFromPC() 
{

  //formato de la estructura de datos 7 bytes
  //[byte inicio, eje x, eje y, motor on/off, velocidad, disparo, byte final]
  //byte inicio = 255
  //eje x, arriba y abajo = entre 0 y 253
  //eje y, movimiento lateral = entre 0 y 253
  //motor on/ff = 0 apagar - 1 encender
  //velocidad = entre 0 y 253
  //disparo = 0 no disparar - 1 disparar
  //byte final = 254

  if (Serial.available()) {  //si tenemos datos en el serial

    byte_from_app = Serial.read();  //leemos el siguiente byte

    if (byte_from_app == byte_inicio)       //comprobamos si es el byte de inicio
    {     
      bytesRecvd = 0;               //reseteamos los bytes recibidos a 0 para leer la secuencia desde el inicio
      data_received = false;        //todavia no tenemos secuencia de datos
    }

    else if (byte_from_app == byte_final)  //si el byte es el de final de secuencia
    {    
      data_received = true;         //indicamos que se ha redcibido una secuencencia de datos
    }
      else                          //estamos en medio de una secuencia, añadimos los datos al buffer
      {        
        inputBuffer[bytesRecvd] = byte_from_app;     //añadimos el byte leido en el buffer
        bytesRecvd++;                                //incrementamos bytes redibidos (indice)
        if (bytesRecvd == buffSize) 
        {    //comprobacion de que el buffer no se ha llenado por seguridad
          bytesRecvd = buffSize - 1;    //si los bytes recibidos son mas grandes que el buffer lo ponemos más pequeño
        }
      }
  }
}
