/*
  Library for the MMA8452Q
  By: Jim Lindblom and Andrea DeVore
  SparkFun Electronics

  Do you like this library? Help support SparkFun. Buy a board!
  https://www.sparkfun.com/products/14587

  This sketch uses the SparkFun_MMA8452Q library to initialize
  the accelerometer and stream calcuated x, y, z, acceleration
  values from it (in g units).

  Hardware hookup:
  Arduino --------------- MMA8452Q Breakout
    3.3V  ---------------     3.3V
    GND   ---------------     GND
  SDA (A4) --\/330 Ohm\/--    SDA
  SCL (A5) --\/330 Ohm\/--    SCL

  The MMA8452Q is a 3.3V max sensor, so you'll need to do some
  level-shifting between the Arduino and the breakout. Series
  resistors on the SDA and SCL lines should do the trick.

  License: This code is public domain, but if you see me
  (or any other SparkFun employee) at the local, and you've
  found our code helpful, please buy us a round (Beerware
  license).

  Distributed as is; no warrenty given.
*/
// Accerelometer
#include <Wire.h>                 // Must include Wire library for I2C
#include "SparkFun_MMA8452Q.h"    // Click here to get the library: http://librarymanager/All#SparkFun_MMA8452Q

MMA8452Q accel;                   // create instance of the MMA8452 class

// EMG
#include <SparkFun_ADS1015_Arduino_Library.h>
ADS1015 adcSensor;
#define sf 1000 // Abtastfrequenz sf ändern
#define tc (1000/(sf))     // Zeitkonstante
unsigned int ADC_Value = 0;    // aktueller ADC Wert
unsigned long last_time = 0;

//////////////////

void calc_angles(float a_x, float a_y, float a_z) {
  float angle_x = atan(a_x / sqrt((a_y * a_y) + (a_z * a_z)));
  // float angle_y = atan(a_y / sqrt((a_x * a_x) + (a_z * a_z)));
  // float angle_z = atan(a_z / sqrt((a_x * a_x) + (a_y * a_y)));

  // From rad to deegres
  angle_x = angle_x * 180 / M_PI;
  // angle_y = angle_y * 180 / M_PI;
  // angle_z = angle_z * 180 / M_PI;

  Serial.print(angle_x, 3);
  Serial.print("\t");
  // Serial.print(angle_y, 3);
  // Serial.print("\t");
  // Serial.print(angle_z, 3); 
  // Serial.print("\t");
}

void setup() {
  Serial.begin(500000);
  Serial.println("MMA8452Q Basic Reading Code!");
  Wire.begin();

  if (accel.begin() == false) {
    Serial.println("Not Connected. Please check connections and read the hookup guide.");
    while (1);
  }
// emg
  if (adcSensor.begin() == true)
  {
    Serial.println("I2C Verbindung gefunden!.");
  }
  else
  {
    Serial.println("Gerät nicht gefunden");
    while (1);
  }
  
}

void loop() {
  if (accel.available()) {      // Wait for new data from accelerometer
    // Acceleration of x, y, and z directions in g units
    float a_x = accel.getCalculatedX();
    float a_y = accel.getCalculatedY();
    float a_z = accel.getCalculatedZ();

    // Calculation of angles
    calc_angles(a_x, a_y, a_z);
    
    Serial.print(a_x, 3);
    Serial.print("\t");
    Serial.print(a_y, 3);
    Serial.print("\t");
    Serial.print(a_z, 3);
    Serial.print("\t");
  }

  ADC_Value = adcSensor.getSingleEnded(0);
  if (millis() - last_time >= tc) {
    last_time = millis();
    
    
    Serial.print(ADC_Value);
    Serial.print("\t");
    Serial.print(millis());
    Serial.println();
    }
}
