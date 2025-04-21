//Required libraries:
// - Micro OSC 0.1.7 (https://github.com/thomasfredericks/MicroOsc)
// - Adafruit_MPR121 1.1.3 (Adafruit)

// Pots connected to A2, A3, A4, A5
// Buttons connected to 13, 12, 27
// Two MPR121 modules connected to i2c, one on channel 0x5A, one on 0x5C

#include <MicroOscSlip.h>
#include "plant-sense.h"

// THE NUMBER 64 BETWEEN THE < > SYMBOLS  BELOW IS THE MAXIMUM NUMBER OF BYTES RESERVED FOR INCOMMING MESSAGES.
// MAKE SURE THIS NUMBER OF BYTES CAN HOLD THE SIZE OF THE MESSAGE YOUR ARE RECEIVING IN ARDUINO.
// OUTGOING MESSAGES ARE WRITTEN DIRECTLY TO THE OUTPUT AND DO NOT NEED ANY RESERVED BYTES.
MicroOscSlip<64> myMicroOsc(&Serial);  // CREATE AN INSTANCE OF MicroOsc FOR SLIP MESSAGES

typedef struct
{
  int pin;
  int currentValue;
  int lastValue;
} Input;

//--------------   TOUCH VARIABLES
#define NUMTOUCHES 12 
Input touchInputsOne[NUMTOUCHES];
Input touchInputsTwo[NUMTOUCHES];


//--------------   MPR121 CapTouch Breakout Stuff
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
// ------------------------------------------  OSC HOOKS
// ------------------------------------------  OSC HOOKS
void onOscMessageReceived(MicroOscMessage& oscMessage) {


// /ping (int)0-1
  if (oscMessage.checkOscAddressAndTypeTags("/ping", "i")) {   
    int intArgument = oscMessage.nextAsInt();
    myMicroOsc.sendMessage("/ping", "i", intArgument);
  } 

// /ffi [MPRIndex] (int)0-3
  else if (oscMessage.checkOscAddressAndTypeTags("/ffi", "ii")) {   
    int MPRIndex = oscMessage.nextAsInt(); 
    int value = oscMessage.nextAsInt();
    if(MPRIndex == 0)
      plants.config(PlantSense::MPR_ONE, PlantSense::FIRST_FILTER_ITERATION, value);
    else if(MPRIndex == 1)
      plants.config(PlantSense::MPR_TWO, PlantSense::FIRST_FILTER_ITERATION, value);
    //echo change
    myMicroOsc.sendMessage("/rpt/ffi", "ii", MPRIndex, value);
  } 



// todo: implement sensor config via osc

// void setCDC(OSCMessage &msgIn){
//   // /cdc [MPRIndex] (int)1-63
// }

// void setCDT(OSCMessage &msgIn){
//   // /cdc [MPRIndex] (int)1-63
// }

// void setSFI(OSCMessage &msgIn){
//   // /sfi [MPRIndex] (int)0-3
// }

// void ESI(OSCMessage &msgIn){
//   // /esi [MPRIndex] (int)0-7
// }


}




//-------------------- -------------------- -------------------- --------------------SETUP
//-------------------- -------------------- -------------------- --------------------SETUP
//-------------------- -------------------- -------------------- --------------------SETUP
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
  // myMicroOSC attaches to Serial
  Serial.begin(115200);
  
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
  plants.config(PlantSense::MPR_ONE, PlantSense::SECOND_FILTER_ITERATION, 0);
  plants.config(PlantSense::MPR_ONE, PlantSense::ELECTRODE_SAMPLE_INTERVAL, 2); 
  
  plants.config(PlantSense::MPR_TWO, PlantSense::FIRST_FILTER_ITERATION, 3);
  plants.config(PlantSense::MPR_TWO, PlantSense::CHARGE_DISCHARGE_CURRENT, 18); 
  plants.config(PlantSense::MPR_TWO, PlantSense::CHARGE_DISCHARGE_TIME, 4);
  plants.config(PlantSense::MPR_TWO, PlantSense::SECOND_FILTER_ITERATION, 0);
  plants.config(PlantSense::MPR_TWO, PlantSense::ELECTRODE_SAMPLE_INTERVAL, 2); 
}

//-------------------- -------------------- -------------------- -------------------- MAIN LOOP
//-------------------- -------------------- -------------------- -------------------- MAIN LOOP
//-------------------- -------------------- -------------------- -------------------- MAIN LOOP
void loop() {
  delay(25);
  myMicroOsc.onOscMessageReceived(onOscMessageReceived);
  readTouchesOne();
  readTouchesTwo();
  readButtons();
  readPots();
  readOSC();
}


//-------------------- READ SERIAL OSC
void readOSC(){
  // TRIGGER onOscMessageReceived() IF AN OSC MESSAGE IS RECEIVED :
  myMicroOsc.onOscMessageReceived(onOscMessageReceived);
}



//-------------------- BUTTONS
void readButtons(){
    bool changeDetected = false;

    //get values
    for(int i = 0; i < NUMBUTTONS; i++){
      buttonInputs[i].currentValue = digitalRead(buttonPins[i]);

      if(buttonInputs[i].currentValue != buttonInputs[i].lastValue){
        changeDetected = true;
      }
    }
    
    if(changeDetected){
      myMicroOsc.sendMessage("/b", "iii", 
      buttonInputs[0].currentValue, 
      buttonInputs[1].currentValue, 
      buttonInputs[2].currentValue);
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
      myMicroOsc.sendMessage("/p", "iii", 
      potInputs[0].currentValue, 
      potInputs[1].currentValue, 
      potInputs[2].currentValue);
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

  int thisMPR = 0;

  myMicroOsc.sendMessage("/traw", "iiiiiiiiiiiii", 
  thisMPR, 
  touchInputsOne[0].currentValue, 
  touchInputsOne[1].currentValue, 
  touchInputsOne[2].currentValue,
  touchInputsOne[3].currentValue, 
  touchInputsOne[4].currentValue, 
  touchInputsOne[5].currentValue,
  touchInputsOne[6].currentValue, 
  touchInputsOne[7].currentValue,
  touchInputsOne[8].currentValue, 
  touchInputsOne[9].currentValue,
  touchInputsOne[10].currentValue, 
  touchInputsOne[11].currentValue);

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

  int thisMPR = 1;

  myMicroOsc.sendMessage("/traw", "iiiiiiiiiiiii", 
  thisMPR, 
  touchInputsTwo[0].currentValue, 
  touchInputsTwo[1].currentValue, 
  touchInputsTwo[2].currentValue,
  touchInputsTwo[3].currentValue, 
  touchInputsTwo[4].currentValue, 
  touchInputsTwo[5].currentValue,
  touchInputsTwo[6].currentValue, 
  touchInputsTwo[7].currentValue,
  touchInputsTwo[8].currentValue, 
  touchInputsTwo[9].currentValue,
  touchInputsTwo[10].currentValue, 
  touchInputsTwo[11].currentValue);

  // -----
  // SEND normalised data...

}
