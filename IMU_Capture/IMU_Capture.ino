 *  ----------------------------------
 *  When starting up the M5StickC, hold it still
 *  while it runs a short calibration routin (3 seconds).
 *  Ideally, set it on a steady surface.

 * Note: calibration and arrangement of acceleration/gyro data designed 
 *       to be wrist worn

 */

#include <WiFi.h>
#include <WiFiUdp.h>
#include <OSCBundle.h>
#include <Adafruit_Sensor_Calibration.h>
#include <Adafruit_AHRS.h>
#include <M5StickCPlus.h>

float accX, accY, accZ, gyroX, gyroY, gyroZ;

float gyroXoffset = 0;
float gyroYoffset = 0;
float gyroZoffset = 0;
float accXoffset = 0;
float accYoffset = 0;
float accZoffset = 0;

Adafruit_Mahony filter;

bool screenState = 1;
unsigned long microsPerReading, microsPrevious;
int refreshRate = 50;

// WiFi network name and password:
const char * networkName = "conductorRX";
const char * networkPswd = "12345679";
unsigned int localPort =  9000; // local port to listen on
unsigned int remotePort = 8000; // remote port to send to
char packetBuffer[255]; //buffer to hold incoming packet
bool waitingForIP = true;

//Send UDP packets using network broadcast address
IPAddress udpAddress (192,168,50,255);

boolean connected = false; //Are we currently connected?
WiFiUDP udp; //The udp library class

void setup() {

  M5.begin();
  M5.IMU.Init();
  M5.Lcd.setRotation(1);
  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setCursor(0, 0, 2);
  M5.Lcd.print("Send IMU to Router");
  M5.Lcd.print(" @ "); M5.Lcd.print(refreshRate);
  M5.Lcd.println(" Hz");
  delay(1000);
  M5.Lcd.println("Calibrating Gyrscope...");

  calibrateIMU(300, 10); //take 300 samples, 10 ms per sample

  filter.begin(refreshRate);

  //Connect to the WiFi network
  connectToWiFi(networkName, networkPswd);
  udp.begin(localPort);

  microsPerReading = 1000000 / refreshRate;
  microsPrevious = micros();
  
  delay(4000); //Let things settle
  M5.Lcd.println("Waiting for remote IP...");
}

void loop() {

  // while(waitingForIP == true) {
  //   getRemoteIP();
  // }

  unsigned long microsNow = micros();
  if(microsNow - microsPrevious >= microsPerReading) {

    M5.IMU.getAccelData(&accX,&accY,&accZ);
    M5.IMU.getGyroData(&gyroX,&gyroY,&gyroZ);

    offsetCorrect(); //Remove noise from sensor readings
    orientationCorrect(); //Rotate orientation 90 degs for wristband use
    filter.updateIMU(gyroX, gyroY, gyroZ, accX, accY, accZ);

    float pitch = filter.getPitch();
    float roll = filter.getRoll();
    float yaw = filter.getYaw();
    float vbat = M5.Axp.GetVbatData() * 1.1 / 1000;

    //invert roll and yaw
    yaw = 360 - yaw;
    if(yaw >= 360) yaw -= 360; if(yaw <= 0) yaw += 360;
    roll = -roll;

    OSCMessage msg("/m5");
    // msg.add(pitch);    
    // msg.add(roll);
    // msg.add(yaw);
    msg.add(accX);
    msg.add(-accY);    
    msg.add(accZ);
    msg.add(-gyroX);  
    msg.add(gyroY);
    msg.add(-gyroZ);
    // TODO: add quaternion data

    udp.beginPacket(udpAddress,remotePort); 
    msg.send(udp);
    udp.endPacket();
    msg.empty();

    microsPrevious += microsPerReading;
  }

  M5.update();

  if(M5.BtnA.wasPressed()) {
    //toggle screen on/off
    screenState = !screenState;
    M5.Axp.SetLDO2(screenState);
  }

  if(M5.BtnB.wasPressed()) {
    //Flash screen to indicate calibration will begin
    M5.Axp.SetLDO2(0); delay(750); M5.Axp.SetLDO2(1); delay(750);
    M5.Axp.SetLDO2(0);
    calibrateIMU(300, 10); //take 300 samples, 10 ms per sample
    //Put screen in on-state
    screenState = 1;
    M5.Axp.SetLDO2(screenState);
  }
}

void calibrateIMU(int calibrationSamples, int delayInterval) {
  
  for(int i = 0; i<calibrationSamples; i++) {
    
    M5.IMU.getAccelData(&accX,&accY,&accZ);
    M5.IMU.getGyroData(&gyroX,&gyroY,&gyroZ);

    accXoffset += accX;
    accYoffset += accY;
    accZoffset += (accZ - 1);
    gyroXoffset += gyroX;
    gyroYoffset += gyroY;
    gyroZoffset += gyroZ;
    
    delay(delayInterval);
  }

  accXoffset = accXoffset / calibrationSamples;
  accYoffset = accXoffset / calibrationSamples;
  accZoffset = accZoffset / calibrationSamples;
  gyroXoffset = gyroXoffset / calibrationSamples;
  gyroYoffset = gyroYoffset / calibrationSamples;
  gyroZoffset = gyroZoffset / calibrationSamples;

  Serial.print("accX Offset: "); Serial.println(accXoffset);
  Serial.print("accY Offset: "); Serial.println(accYoffset);
  Serial.print("accZ Offset: "); Serial.println(accZoffset);
  Serial.print("gyroX Offset: "); Serial.println(gyroXoffset);
  Serial.print("gyroY Offset: "); Serial.println(gyroYoffset);
  Serial.print("gyroZ Offset: "); Serial.println(gyroZoffset);
}

void offsetCorrect() {
  //accX  -= accXoffset;
  //accY  -= accYoffset;
  //accZ  -= accZoffset;
  gyroX -= gyroXoffset;
  gyroY -= gyroYoffset;
  gyroZ -= gyroZoffset;
}

void orientationCorrect() {

  float temporaryAccX = accX;
  float temporaryGyroX = gyroX;
  accX = -accY;
  accY = temporaryAccX;
  gyroX = -gyroY;
  gyroY = temporaryGyroX;
}

void getRemoteIP() {
  // if there's data available, read a packet
  int packetSize = udp.parsePacket();
  
  if (packetSize) {
    udpAddress = udp.remoteIP();
    M5.Lcd.print("RemoteIP: " + String(udpAddress.toString()));
    M5.Lcd.print(" : "); M5.Lcd.println(remotePort);
    int len = udp.read(packetBuffer, 255);
    if (len > 0) packetBuffer[len] = 0;
    waitingForIP = false;
    }
}

void connectToWiFi(const char * ssid, const char * pwd){

  M5.Lcd.println("Connecting to: " + String(ssid));
  delay(2000);
  WiFi.disconnect(true);   // delete old config
  WiFi.onEvent(WiFiEvent); //register event handler
  WiFi.begin(ssid, pwd);   //Initiate connection
}

//wifi event handler
void WiFiEvent(WiFiEvent_t event){
    switch(event) {
      case SYSTEM_EVENT_STA_GOT_IP:
          M5.Lcd.println("WiFi connected!");
          M5.Lcd.println("LocalIP: " + String(WiFi.localIP().toString()));
          //initializes the UDP state
          //This initializes the transfer buffer
          udp.begin(WiFi.localIP(),localPort);
          connected = true;
          break;
      case SYSTEM_EVENT_STA_DISCONNECTED:
          M5.Lcd.fillScreen(BLACK);
          M5.Lcd.setCursor(0, 0, 1);
          M5.Lcd.println("WiFi lost connection");
          connected = false;
          break;
      default: break;
    }
}
