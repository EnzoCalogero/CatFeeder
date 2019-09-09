#include <Arduino.h>
#include "HX711.h"
#include <WiFi.h>

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 25;
const int LOADCELL_SCK_PIN = 26;
long int reading;
HX711 scale;
#include "esp32-mqtt.h"

void setup() {
  // put your setup code here, to run once:
  
  Serial.begin(115200);
  
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  pinMode(LED_BUILTIN, OUTPUT);
  setupCloudIoT();
}

unsigned long lastMillis = 0;
void loop() {
 
  mqttClient->loop();
  delay(20);  // <- fixes some issues with WiFi stability

  if (!mqttClient->connected()) {
    connect();
  }
  else {

        if (scale.is_ready()) {
          reading = scale.read();
          Serial.print("HX711 reading: ");
          Serial.println(reading);
        } else {
          reading= 999999;
        //  Serial.println("HX711 not found.");
        }
          
      //phase 2
      
          
          char buffer[26];
          struct tm* tm_info;
          time_t timer;
          time(&timer);
          tm_info = localtime(&timer);

          strftime(buffer, 26, "%Y-%m-%d %H:%M:%S", tm_info);
          String payload = String("{\"device\":\"") + device_id + String("\"") +
                          String(", \"time\":\"") + buffer + String("\"") +
                          String(", \"sensor\":\"Weight\"")  +
                          String(", \"val\":") + reading +
                          String(", \"extra\":\"esp01\"")  +
                          String("}");
          Serial.println(payload);
        
          publishTelemetry(payload);
          delay(180000);
   }
}
