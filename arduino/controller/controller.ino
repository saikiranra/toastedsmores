#include <Encoder.h>

int encoderPinA = 2;
int encoderPinB = 3;

int enB = 5; //Speed enable
int in3 = 7; //Motor controller enable
int in4 = 6; //Motor controller enable

float baseP = 100;
float baseI = 1;
float baseD = 0.3;

float iError = 0;
float prevError = 0;


boolean speedSet = false;
boolean runLoop = false;

int baseSetpoint;

String command = "";

unsigned long lastTimeStamp;

Encoder myEnc(encoderPinA , encoderPinB);

void setup() {
  Serial.begin(9600);
  //Assume that the base starts rotated all the way to the right
  //

  pinMode(enB , OUTPUT);
  pinMode(in3 , OUTPUT);
  pinMode(in4 , OUTPUT);
}

long oldPosition  = -999;

int getCurrentAngle(){
  //1440 pules per rotation
  //4 to 1 from encoder to actual movement
  float encoderPosition =(float) myEnc.read();
  encoderPosition = encoderPosition / (float) 1440;
  encoderPosition *= 90.0;
  //Serial.println(encoderPosition);
  return (int) encoderPosition;
}

void updateBaseController(){
  //0 to 255
  unsigned long currentTimeStamp = millis();
  double deltaT = (double)(currentTimeStamp - lastTimeStamp);
  lastTimeStamp = currentTimeStamp;
  
  float error = (float)(getCurrentAngle() - baseSetpoint);
  iError += error * deltaT;
  if(iError > 1000){
    iError = 1000;
  }
  if(iError < -1000){
    iError = -1000;
  }

  float dError = (prevError - error) / deltaT;
  prevError = error;
  
  int output = (int)((baseP * error) + (baseI * iError) + (dError * baseD));
  bool directionForward = true;
  if(output > 255){
    output = 255;
  }
  if(output < -255){
    output = -255;
  }
  if(output != 0){
    String message = "Angle: " + String(getCurrentAngle()) + " Setpoint: " + String(baseSetpoint) + " Out: " + String(output);
    //Serial.println(message);
  }
  if(output < 0){
    output = -output;
    directionForward = false;
  }
  

  setBaseSpeed(output , directionForward);
}

void setBaseSpeed(int value , bool dir){
  //value - int between 0 and 255
  //dir - direction, True is forward, False is backward
  speedSet = true;
  if(value == 0){
    digitalWrite(in3, LOW);
    digitalWrite(in4, LOW);
  }
  else if(dir){
    digitalWrite(in3, HIGH);
    digitalWrite(in4, LOW);
  }
  else{
    digitalWrite(in3, LOW);
    digitalWrite(in4, HIGH);
  }

  analogWrite(enB , value);
}

void loop() {
  speedSet = false;
  String nextCommand = "";
  char character;
  if (Serial.available()) {
    character = Serial.read();
    if(character == ' '){
      nextCommand = command;
      command = "";
    }
    else{
      command.concat(character);
    }
  }

  if(nextCommand != ""){
    //Serial.println(nextCommand);
    if(nextCommand.substring(0 , 4) == "BASE"){
        baseSetpoint = nextCommand.substring(4 , 7).toInt();
        //Serial.println("SETTING BASE TO " + String(baseSetpoint));
        iError = 0;
        runLoop = true;
    }
    if(nextCommand == "STOP"){
      runLoop = false;
    }
  }

  if(runLoop){
    updateBaseController();
  }
  if(!speedSet){
    setBaseSpeed(0 , true);
  }
  delay(20);
}
