//Required libraries:
// - AutoConnect (Hieromon Ikasamo)
// - OSC (Adrian Freed)
// - Adafruit_MPR121 (Adafruit)

// Pots connected to A2, A3, A4, A5
// Buttons connected to 13, 12, 27
// Two MPR121 modules connected to i2c, one on channel 0x5A, one on 0x5C

typedef struct
{
  int pin;
  int currentValue;
  int lastValue;
} Input;

#include <WiFi.h>
// #include <WebServer.h>
// #include <AutoConnect.h>

// WebServer Server;
// AutoConnect Portal(Server);

#ifdef BOARD_HAS_USB_SERIAL
#include <SLIPEncodedUSBSerial.h>
SLIPEncodedUSBSerial SLIPSerial( thisBoardsSerialUSB );
#else
#include <SLIPEncodedSerial.h>
SLIPEncodedSerial SLIPSerial(Serial); // Change to Serial1 or Serial2 etc. for boards with multiple serial ports that don’t have Serial
#endif

//----------------- OSC STUFF
#include <WiFiUdp.h>
#include <OSCMessage.h>
#include <OSCBundle.h>
#include <OSCData.h>

OSCErrorCode error;
unsigned int ledState = LOW;              // LOW means led is *on*

WiFiUDP Udp;                                // A UDP instance to let us send and receive packets over UDP
const IPAddress outIp(255, 255, 255, 255);     // remote IP of your computer
const unsigned int outPort = 8000;          // remote port to receive OSC
const unsigned int localPort = 9000;        // local port to listen for OSC packets
String macString = "";
String oscAddress;

//--------------   TOUCH VARIABLES
#define NUMTOUCHES 8 // THIS SHOULD BE 12 INPUTS PER MPR
Input touchInputs[NUMTOUCHES];
// int touchPins[NUMTOUCHES] = {4, 15, 13, 12, 14, 27, 32, 33};

// MPR121 CapTouch Breakout Stuff
#include <Wire.h>
#include "Adafruit_MPR121.h"
int i2cADDR[] = {0x5A, 0x5C};
Adafruit_MPR121 capLeft = Adafruit_MPR121();  // ADDR not connected: 0x5A
Adafruit_MPR121 capRight = Adafruit_MPR121(); // ADDR tied to SDA:   0x5C

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
#define POT_PIN4 4
#define NUMPOTS 4
Input potInputs[NUMPOTS];
int potPins[NUMPOTS] = {POT_PIN1, POT_PIN2, POT_PIN3};

// void rootPage() {
//   char content[] = "Hello, world";
//   Server.send(200, "text/plain", content);
// }

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
    // touchInputs[i].pin = touchPins[i];
    touchInputs[i].currentValue = 0;
    touchInputs[i].lastValue = 1;
  }



  //SERIAL
  Serial.begin(115200);
  //begin SLIPSerial just like Serial
  SLIPSerial.begin(115200);   // set this as high as you can reliably run on your platform
  Serial.println("setting up pins...");
  SLIPSerial.println("setting up pins...");


 
  //INIT MPR121
  bool capLeft_connected = false;
  while (!capLeft_connected) {
    if (!capLeft.begin(0x5A)) {
      Serial.println("Left MPR121 not found, check wiring?");
      delay(100);
    } else {
      Serial.println("Left MPR121 found!");
      capLeft_connected = true;
    }
  }

  bool capRight_connected = false;
  while (!capRight_connected) {
    if (!capRight.begin(0x5C)) {
      Serial.println("Right MPR121 not found, check wiring?");
      delay(100);
    } else {
      Serial.println("Right MPR121 found!");
      capRight_connected = true;
    }
  }


  Serial.println("done :)");


  // NETWORKING
  //get mac
  byte macBytes[6];
  WiFi.macAddress(macBytes);
  char macChars[19];
  sprintf(macChars, "%02X-%02X-%02X-%02X-%02X-%02X", macBytes[0], macBytes[1], macBytes[2], macBytes[3], macBytes[4], macBytes[5]);
  macString = String(macChars);
  Serial.println("hey there.  I am " + macString);
  oscAddress = "/" + macString + "/touches";
  Serial.println("I will output osc to " + oscAddress + " on port 8000 as well as over serial.");

  // Server.on("/", rootPage);
  // if (Portal.begin()) {
  //   Serial.println("WiFi connected: " + WiFi.localIP().toString()); //this line was hanging

  //   Serial.println("Starting UDP");
  //   Udp.begin(localPort);
  //   Serial.println("Started!");
  // }
}



//-------------------- MAIN LOOP
void loop() {
  // Portal.handleClient();
  delay(25);

  readTouches();
  readButtons();
  readPots();
}

//-------------------- BUTTONS
void readButtons(){

}

//-------------------- POTS
void readPots(){}

//-------------------- MPR TOUCH SENSORS
void readTouches(){
    bool changeDetected = false;

  // Read Touch Inputs from Left and Right MPR121 boards
  touchInputs[0].currentValue = capLeft.filteredData(0);
  touchInputs[1].currentValue = capRight.filteredData(0);

  // Check for Changes
  if ( touchInputs[0].currentValue != touchInputs[0].lastValue ||
        touchInputs[1].currentValue != touchInputs[1].lastValue) {
    changeDetected = true;
  }

  // Update History Value
  touchInputs[0].lastValue = touchInputs[0].currentValue;
  touchInputs[1].lastValue = touchInputs[1].currentValue;

  if (changeDetected) {
    OSCMessage msg(oscAddress.c_str());
    for (int i = 0; i < NUMTOUCHES; i++) msg.add( (unsigned int)touchInputs[i].currentValue );
    // Udp.beginPacket(outIp, outPort);
    // msg.send(Udp);
    // Udp.endPacket();
    SLIPSerial.beginPacket();
    msg.send(SLIPSerial);
    SLIPSerial.endPacket();
    msg.empty();
  }
}
