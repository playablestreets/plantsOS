//Required libraries:
// - OSC (Adrian Freed)
// - Adafruit_MPR121 (Adafruit)

// Pots connected to A2, A3, A4, A5
// Buttons connected to 13, 12, 27
// Two MPR121 modules connected to i2c, one on channel 0x5A, one on 0x5C

#include <Wire.h> // is this actually required??
#include "plant-sense.h"
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
#define NUMTOUCHES 12 
Input touchInputsOne[NUMTOUCHES];
Input touchInputsTwo[NUMTOUCHES];

// MPR121 CapTouch Breakout Stuff
PlantSense plants = PlantSense();

//------------------  BUTTONS AND POTS
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



// ------------------------------------------  OSC HOOKS
void ping(OSCMessage &msgIn){

  oscAddress = "/ping";
  OSCMessage msgOut(oscAddress.c_str());

  msgOut.add( (unsigned int) 1);

  SLIPSerial.beginPacket();
  msgOut.send(SLIPSerial);
  SLIPSerial.endPacket();
  msgOut.empty();

}

void setFFI(OSCMessage &msgIn){
  // /ffi [MPRIndex] (int)0-3
}

void setCDC(OSCMessage &msgIn){
  // /cdc [MPRIndex] (int)1-63
}

void setCDT(OSCMessage &msgIn){
  // /cdc [MPRIndex] (int)1-63
}

void setSFI(OSCMessage &msgIn){
  // /sfi [MPRIndex] (int)0-3
}

void ESI(OSCMessage &msgIn){
  // /esi [MPRIndex] (int)0-7
}




// ------------------------------------------  SETUP
// ------------------------------------------  SETUP
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

  for (int i = 0; i < NUMTOUCHES; i++) {
    touchInputsOne[i].currentValue = 0;
    touchInputsOne[i].lastValue = 1;
  
    touchInputsTwo[i].currentValue = 0;
    touchInputsTwo[i].lastValue = 1;
  }


  //SERIAL
  Serial.begin(115200);
  //begin SLIPSerial just like Serial
  SLIPSerial.begin(115200);   // set this as high as you can reliably run on your platform
  
  Serial.println("connecting and configuring to MPRs...");

  plants.init(); 
  Serial.println("done :)");
  
  /* CONFIG1 and CONFIG2 registers parameterized here
   * Attach your OSC stuff to this
   * All the enums are at the top of the header file :-) 
   */

  plants.config(PlantSense::MPR_ONE, PlantSense::FIRST_FILTER_ITERATION, 3);
  plants.config(PlantSense::MPR_ONE, PlantSense::CHARGE_DISCHARGE_CURRENT, 18); 
  plants.config(PlantSense::MPR_ONE, PlantSense::CHARGE_DISCHARGE_TIME, 4);
  plants.config(PlantSense::MPR_ONE, PlantSense::SECOND_FILTER_ITERATION, 0); ;
  plants.config(PlantSense::MPR_ONE, PlantSense::ELECTRODE_SAMPLE_INTERVAL, 2); 
  
  plants.config(PlantSense::MPR_TWO, PlantSense::FIRST_FILTER_ITERATION, 3);
  plants.config(PlantSense::MPR_TWO, PlantSense::CHARGE_DISCHARGE_CURRENT, 18); 
  plants.config(PlantSense::MPR_TWO, PlantSense::CHARGE_DISCHARGE_TIME, 4);
  plants.config(PlantSense::MPR_TWO, PlantSense::SECOND_FILTER_ITERATION, 0); ;
  plants.config(PlantSense::MPR_TWO, PlantSense::ELECTRODE_SAMPLE_INTERVAL, 2); 
}

//-------------------- MAIN LOOP
void loop() {
  delay(25);

  readTouchesOne();
  readTouchesTwo();
  readButtons();
  readPots();
  // readOSC();
}


//-------------------- READ SERIAL OSC
void readOSC(){
  OSCBundle bundleIN;
  int slipsize;

  while(!SLIPSerial.endofPacket()){
    if( (slipsize =SLIPSerial.available()) > 0)
    {
       while(slipsize--)
          bundleIN.fill(SLIPSerial.read());
     }
  }
  if(!bundleIN.hasError()){

    // -------------------------------- OSC HOOKS
    bundleIN.dispatch("/ping", ping);
    bundleIN.dispatch("/ffi", setFFI);
    bundleIN.dispatch("/cdc", setCDC);
    bundleIN.dispatch("/cdt", setCDT);
    bundleIN.dispatch("/sfi", setSFI);
    bundleIN.dispatch("/esi", ESI);
  }
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
      oscAddress = "/b";
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
      oscAddress = "/p";
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
void readTouchesOne(){

  // -----
  // SENDING "RAW" (not normalized) DATA
  for(int i = 0; i < NUMTOUCHES; i++){
    touchInputsOne[i].lastValue = touchInputsOne[i].currentValue;
    touchInputsOne[i].currentValue = plants.read(PlantSense::MPR_ONE, i);
  }

  oscAddress = "/traw";
  OSCMessage msg(oscAddress.c_str());
  
  //MPR #1
  msg.add( (unsigned int)0 );

  for (int i = 0; i < NUMTOUCHES; i++){
    msg.add( (unsigned int)touchInputsOne[i].currentValue );
  }

  SLIPSerial.beginPacket();
  msg.send(SLIPSerial);
  SLIPSerial.endPacket();
  msg.empty();

  // -----
  // SEND normalised data...

}

void readTouchesTwo(){

  // -----
  // SENDING "RAW" (not normalized) DATA
  for(int i = 0; i < NUMTOUCHES; i++){
    touchInputsTwo[i].lastValue = touchInputsTwo[i].currentValue;
    touchInputsTwo[i].currentValue = plants.read(PlantSense::MPR_TWO, i);
  }

  oscAddress = "/traw";
  OSCMessage msg(oscAddress.c_str());

  //MPR #2
  msg.add( (unsigned int)1 );

  for (int i = 0; i < NUMTOUCHES; i++){
    msg.add( (unsigned int)touchInputsTwo[i].currentValue );
  }

  SLIPSerial.beginPacket();
  msg.send(SLIPSerial);
  SLIPSerial.endPacket();
  msg.empty();

  // -----
  // SEND normalised data...

}
