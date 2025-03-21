//Required libraries:
// - OSC (Adrian Freed)
// - Adafruit_MPR121 (Adafruit)

// Pots connected to A2, A3, A4, A5
// Buttons connected to 13, 12, 27
// Two MPR121 modules connected to i2c, one on channel 0x5A, one on 0x5C

// #include <Wire.h> // is this actually required??
// #include "Adafruit_MPR121.h"
// #include <WiFiUdp.h>
#include <OSCMessage.h>
#include <OSCBundle.h>
#include <OSCData.h>


typedef struct
{
  int pin;
  int currentValue;
  int lastValue;
} Input;


#ifdef BOARD_HAS_USB_SERIAL
#include <SLIPEncodedUSBSerial.h>
SLIPEncodedUSBSerial SLIPSerial( thisBoardsSerialUSB );
#else
#include <SLIPEncodedSerial.h>
SLIPEncodedSerial SLIPSerial(Serial); // Change to Serial1 or Serial2 etc. for boards with multiple serial ports that don’t have Serial
#endif

//----------------- OSC STUFF

OSCErrorCode error;
unsigned int ledState = LOW;              // LOW means led is *on*

String macString = "";
String oscAddress;

//--------------   TOUCH VARIABLES
// #define NUMTOUCHES 12 // THIS SHOULD BE 12 INPUTS PER MPR
// Input touchInputsOne[NUMTOUCHES];
// Input touchInputsTwo[NUMTOUCHES];

// MPR121 CapTouch Breakout Stuff
// int i2cADDR[] = {0x5A, 0x5C};
// Adafruit_MPR121 MPROne = Adafruit_MPR121();  // ADDR not connected: 0x5A
// Adafruit_MPR121 MPRTwo = Adafruit_MPR121(); // ADDR tied to SDA:   0x5C

//------------------  BUTTONS AND POTS
//--------------   TOUCH VARIABLES
#define BUTTON_PIN1 13
#define BUTTON_PIN2 12
#define BUTTON_PIN3 27
#define NUMBUTTONS 3
Input buttonInputs[NUMBUTTONS];
int buttonPins[NUMBUTTONS] = {BUTTON_PIN1, BUTTON_PIN2, BUTTON_PIN3};

#define POT_PIN1 34
#define POT_PIN2 39
#define POT_PIN3 36
#define POT_PIN4 32 //jump pin 15 to pot 4 wiper on TTP 0.1 boards 
#define NUMPOTS 4
Input potInputs[NUMPOTS];
int potPins[NUMPOTS] = {POT_PIN1, POT_PIN2, POT_PIN3, POT_PIN4};


// ------------------------------------------  SETUP
void setup() {
  delay(1000);

  //INIT INPUTS
  pinMode(BUTTON_PIN1, INPUT_PULLUP);
  pinMode(BUTTON_PIN2, INPUT_PULLUP);
  pinMode(BUTTON_PIN3, INPUT_PULLUP);

  for (int i = 0; i < NUMBUTTONS; i++){
    buttonInputs[i].pin = buttonPins[i];
    buttonInputs[i].currentValue = 0;
    buttonInputs[i].lastValue = 0;
  }

 for (int i = 0; i < NUMPOTS; i++){
    potInputs[i].pin = potPins[i];
    potInputs[i].currentValue = 0;
    potInputs[i].lastValue = 0;
  }

  // for (int i = 0; i < NUMTOUCHES; i++) {
  //   touchInputsOne[i].currentValue = 0;
  //   touchInputsOne[i].lastValue = 1;
  
  //   touchInputsTwo[i].currentValue = 0;
  //   touchInputsTwo[i].lastValue = 1;
  // }



  //SERIAL
  Serial.begin(115200);
  //begin SLIPSerial just like Serial
  SLIPSerial.begin(115200);   // set this as high as you can reliably run on your platform
  Serial.println("setting up pins...");
  SLIPSerial.println("setting up pins...");


 
  //INIT MPR121
  // bool MPROne_connected = false;
  // while (!MPROne_connected) {
  //   if (!MPROne.begin(0x5A)) {
  //     Serial.println("Left MPR121 not found, check wiring?");
  //     delay(100);
  //   } else {
  //     Serial.println("Left MPR121 found!");
  //     MPROne_connected = true;
  //   }
  // }

  // bool MPRTwo_connected = false;
  // while (!MPRTwo_connected) {
  //   if (!MPRTwo.begin(0x5C)) {
  //     Serial.println("Right MPR121 not found, check wiring?");
  //     delay(100);
  //   } else {
  //     Serial.println("Right MPR121 found!");
  //     MPRTwo_connected = true;
  //   }
  // }


  Serial.println("done :)");

  macString = "usb";
  // Serial.println("hey there.  I am not connected to wifi.");
  oscAddress = "/" + macString + "/touches";
  // Serial.println("I will output osc to " + oscAddress + " on port 8000 as well as over serial.");
}



//-------------------- MAIN LOOP
void loop() {
  // Portal.handleClient();
  delay(25);

  // readTouchesOne();
  // readTouchesTwo();
  readButtons();
  readPots();
}



//-------------------- BUTTONS
void readButtons(){
    bool changeDetected = false;

    //get values
    for(int i = 0; i < NUMBUTTONS; i++){
      buttonInputs[i].currentValue = digitalRead(buttonPins[i]);

      if(buttonInputs[i].currentValue != buttonInputs[i].lastValue)
        changeDetected = true;

    }
    
    if(changeDetected){
      oscAddress = "/" + macString + "/buttons";
      OSCMessage msg(oscAddress.c_str());
      for (int i = 0; i < NUMBUTTONS; i++){ 
        msg.add( (unsigned int)(1 - buttonInputs[i].currentValue) );
      }

      SLIPSerial.beginPacket();
      msg.send(SLIPSerial);
      SLIPSerial.endPacket();
      msg.empty();
    }

    for(int i = 0; i < NUMBUTTONS; i++){
      buttonInputs[i].lastValue = buttonInputs[i].currentValue;
    }

}

//-------------------- POTS
void readPots(){
    bool changeDetected = false;

    //get values
    for(int i = 0; i < NUMPOTS; i++){
      potInputs[i].currentValue = analogRead(potPins[i]);

      if(potInputs[i].currentValue != potInputs[i].lastValue){
        changeDetected = true;
      }
    }
    
    if(changeDetected){
      oscAddress = "/" + macString + "/pots";
      OSCMessage msg(oscAddress.c_str());
      for (int i = 0; i < NUMPOTS; i++){ 
        msg.add( (unsigned int)(potInputs[i].currentValue) );
      }

      SLIPSerial.beginPacket();
      msg.send(SLIPSerial);
      SLIPSerial.endPacket();
      msg.empty();
    }

    for(int i = 0; i < NUMPOTS; i++){
      potInputs[i].lastValue = potInputs[i].currentValue;
    }

}

//-------------------- MPR TOUCH SENSORS
// void readTouchesOne(){
//     bool changeDetected = false;

//   for(int i = 0; i < NUMTOUCHES; i++){
//     touchInputsOne[i].currentValue = MPROne.filteredData(i);
    
//     if( touchInputsOne[i].currentValue != touchInputsOne[i].lastValue ){
//       changeDetected = true;
//     } 
    
//     touchInputsOne[i].lastValue = touchInputsOne[i].currentValue;
//   }


//   if (changeDetected) {
//     oscAddress = "/" + macString + "/touchesOne";
//     OSCMessage msg(oscAddress.c_str());

//     for (int i = 0; i < NUMTOUCHES; i++){
//       msg.add( (unsigned int)touchInputsOne[i].currentValue );
//     }

//     SLIPSerial.beginPacket();
//     msg.send(SLIPSerial);
//     SLIPSerial.endPacket();
//     msg.empty();
//   }
// }

// void readTouchesTwo(){
//     bool changeDetected = false;

//   for(int i = 0; i < NUMTOUCHES; i++){
//     touchInputsTwo[i].currentValue = MPRTwo.filteredData(i);
    
//     if( touchInputsTwo[i].currentValue != touchInputsTwo[i].lastValue ){
//       changeDetected = true;
//     } 
    
//     touchInputsTwo[i].lastValue = touchInputsTwo[i].currentValue;
//   }


//   if (changeDetected) {
//     oscAddress = "/" + macString + "/touchesTwo";
//     OSCMessage msg(oscAddress.c_str());

//     for (int i = 0; i < NUMTOUCHES; i++){
//       msg.add( (unsigned int)touchInputsTwo[i].currentValue );
//     }

//     SLIPSerial.beginPacket();
//     msg.send(SLIPSerial);
//     SLIPSerial.endPacket();
//     msg.empty();
//   }
// }
