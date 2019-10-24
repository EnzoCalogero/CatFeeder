#include "HX711.h"
#include "esp32-mqtt.h"
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 20,4);  

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 25;
const int LOADCELL_SCK_PIN = 26;
long int reading;
HX711 scale;
 int counter = 0;


unsigned long previousMillis = 0;        
// constants won't change :
const long interval = 180000; //mill sec     
void setup() {
  // put your setup code here, to run once:
  
  Serial.begin(115200);
lcd.init();  

lcd.backlight(); 

lcd.setCursor(0,0); 
lcd.print("Starting");


  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  pinMode(LED_BUILTIN, OUTPUT);
  setupCloudIoT();
 
  mqttClient->loop();
  delay(20);  // <- fixes some issues with WiFi stability
  Serial.println("phase 1");
}
void loop(void){
unsigned long currentMillis = millis();
 

++counter;
if (!mqttClient->connected()) {
    connect();
    delay(50);
  }
 if (currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;
 
  if (!mqttClient->connected()) {
   // Serial.println("... phase 2 .... ");
    connect();
  }
  else {
        Serial.println("phase 3");
        if (scale.is_ready()) {
          reading = scale.read();
          Serial.print("HX711 reading: ");
          Serial.println(reading);
          lcd.setCursor(0,1);
          
          lcd.print(String("Reading: ") + reading);  
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
      }
       //  delay(18000);
// Serial.println("I'm awake, but I'm going into deep sleep mode for 15 seconds");
//  ESP.deepSleep(15e6);
}
if(WiFi.status() != WL_CONNECTED){
  lcd.setCursor(0,0); 
  lcd.print("not connected");
  Serial.println("in if not connected");
  delay(1800);
 }
else {
  counter=0;
  lcd.setCursor(0,0); 
  lcd.print("Connected");
 }

}
