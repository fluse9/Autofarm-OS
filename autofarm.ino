#include <Wire.h>

#include <uFire_SHT20.h>
uFire_SHT20 sht20;

float eOffset, E, C;

const float pOffSet = 0.483;
float V, P;
#define PressureSensorPin 0

int Liquid_level = 0;
#define LiquidSensorPin 5

unsigned long int avgValue; //Store the average value of the sensor feedback
float b;
int buf[10],temp;
#define phSensorPin A1

#define fiveMinutes (1000UL * 60 * 5)

unsigned long time = millis();

void setup() {
  Serial.begin(115200);
  Wire.begin();
  sht20.begin();
  pinMode(3, OUTPUT);
  pinMode(10, OUTPUT);
}

void loop() {
  V = analogRead(PressureSensorPin) * 5.00 / 1024;
  P = (V - pOffSet) * 400;
 
  Serial.println(millis() / 1000);
  Serial.println(time / 1000);
 
  if ((long)(millis() / 1000 - time / 1000) >= 0 && (long)(millis() / 1000 - time / 1000) <= 25) {
    digitalWrite(10, HIGH);
    digitalWrite(3, HIGH);
  }
  if ((long)(millis() - time) < 0) {
    digitalWrite(10, LOW);
    digitalWrite(3, LOW);
  }
  if ((long)(millis() / 1000 - time / 1000) > 25 && (long)(millis() / 1000 - time / 1000) < 27) {
    time += fiveMinutes;
  }
 
  Liquid_level=digitalRead(LiquidSensorPin);
 
  for(int i=0;i<10;i++)       //Get 10 sample value from the sensor for smooth the value
    {
    analogRead(phSensorPin);
    delay(10);
  }
  for(int i=0;i<9;i++)        //sort the analog from small to large
  {
    for(int j=i+1;j<10;j++)
    {
      if(buf[i]>buf[j])
      {
        temp=buf[i];
        buf[i]=buf[j];
        buf[j]=temp;
      }
    }
  }
  avgValue=0;
  for(int i=2;i<8;i++)                      //take the average value of 6 center sample
    avgValue+=buf[i];
  float phValue=(float)avgValue*5.0/1024/6; //convert the analog into millivolt
  phValue=3.5*phValue;                      //convert the millivolt into pH value
 
  Serial.println("VOLTAGE: ");
  Serial.println(V, 3);
  Serial.println("PRESSURE: ");
  Serial.println(P, 1);
 
  Serial.println("LIQUIDLEVEL: ");
  Serial.println(Liquid_level, DEC);
 
  Serial.println("PH: ");
  Serial.println(phValue,2);
 
  Serial.println("HUMIDITY: ");
  Serial.println(sht20.humidity());
  Serial.println("AIRTEMP: ");
  Serial.println(sht20.temperature());
  Serial.println("DEWPOINT: ");
  Serial.println(sht20.dew_point());
  Serial.println("VPD: ");
  Serial.println(sht20.vpd());
 
  Serial.println("");
}
