const int Trigger = 2; //Pin digital 2 para el Trigger del sensor
const int Echo = 3;    //Pin digital 3 para el Echo del sensor
long anterior = 4;  

void setup()
{
  Serial.begin(9600);         //iniciailzamos la comunicación
  pinMode(Trigger, OUTPUT);   //pin como salida
  pinMode(Echo, INPUT);       //pin como entrada
  digitalWrite(Trigger, LOW); //Inicializamos el pin con 0
}

void loop()
{
  /*long d; //distancia en centimetros
  long t; //timepo que demora en llegar el eco

  digitalWrite(Trigger, HIGH);
  delayMicroseconds(10); //Enviamos un pulso de 10us
  digitalWrite(Trigger, LOW);

  t = pulseIn(Echo, HIGH); //obtenemos el ancho del pulso
  d = t / 59;              //escalamos el tiempo a una distancia en cm
  if (d != anterior || true)
  {
    anterior = d;
    //String resultado = "Distancia: " + d + "cm"; //Enviamos serialmente el valor de la distancia
    //Serial.print("Puerta abierta ");
    */

    for(int d=0;d<4;d++){
      Serial.print('4');
      delay(1000);
    }

    for(int d=0;d<3;d++){
      Serial.print('5');
      delay(1000);
    }
    
    /* code */
  

  delay(1000); //Hacemos una pausa de 100ms
}
