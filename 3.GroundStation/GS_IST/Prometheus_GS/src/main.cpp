
#include "Arduino.h"
#include "WiFi.h"
#include "ESPAsyncWebServer.h"
#include "AsyncWebSocket.h"
#include "libraries/decoder.h"
#include <libraries/LORA.h>
#include <SPI.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h>
#include <sstream>
#include "kaitai/kaitaistruct.h"
#include <iostream>
#include <cstring>
#include <StreamString.h>


#define pingo 34          // pin for push-button
#define pinf  2          // pin for signaling led
#define azimuth_pin 25
#define elevation_pin 27

#define MESS "Simple test message"    // message to send and receive
#define RXTIMEOUT 500    // tens of milliseconds (I.E. RXTIMEOUT*10=milliseconds)
#define inplen 64        // sending buffer len 
#define reclen 255        // receiving buffer len 



LORA LR;                 // Class LORA instance

unsigned dest;
char msg[inplen];
char inpbuff[inplen];    // sending buffer
char recbuff[reclen];    // receiving buffer
int cnt=0;
float azimuth, elevation;
Servo servoAzimuth, servoElevation;
char data[64];           // buffer for RSSI and SNR
#define format "|Rssi: %d RssiPk: %d SnrPk %d|  "

int SF=9;  //Spreading factor value (if changed for test)
int BW=6;  //Bandwidth value (if changed for test)

int PWR=5; //transmit power (100mW)

boolean SHIELD=true;
boolean getInput();
void sendBuff();
void getReplay();
void blinkpinf(int time,int n);
void showConfig();
boolean getSerialMsg();
boolean sendSerialMsg();
boolean sendWifiMsg();
int nb;
void onWsEvent_rot(AsyncWebSocket* server, AsyncWebSocketClient* client, AwsEventType type, void* arg, uint8_t* data, size_t len);
void onWsEvent_cmd(AsyncWebSocket* server, AsyncWebSocketClient* client, AwsEventType type, void* arg, uint8_t* data, size_t len);

char terminal_buffer[1024];

void readPayload(prometheus_t* datastream);

// Access Point 
const char* ssid = "PROMETHEUS";
const char* password = "VerySecurePW";
AsyncWebServer server(80);
AsyncWebSocket ws_rotator("/rot_ws");
AsyncWebSocket ws_command("/cmd_ws");
WiFiClient client;
bool wifi_flag = false;
bool angle_flag = false;



const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <title>Prometheus GS</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <style>
  html {
    font-family: Arial, Helvetica, sans-serif;
    text-align: center;
  }
  h1 {
    font-size: 1.8rem;
    color: white;
  }
  h2{
    font-size: 1.5rem;
    font-weight: bold;
    color: #143642;
  }
  .topnav {
    overflow: hidden;
    background-color: #143642;
  }
  body {
    margin: 0;
  }
  .content {
    padding: 30px;
    max-width: 600px;
    margin: 0 auto;
  }
  .card {
    background-color: #F8F7F9;;
    box-shadow: 2px 2px 12px 1px rgba(140,140,140,.5);
    padding-top:10px;
    padding-bottom:20px;
  }
  .button {
    padding: 15px 50px;
    font-size: 24px;
    text-align: center;
    outline: none;
    color: #fff;
    background-color: #0f8b8d;
    border: none;
    border-radius: 5px;
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
    -webkit-tap-highlight-color: rgba(0,0,0,0);
   }
   /*.button:hover {background-color: #0f8b8d}*/
   .button:active {
     background-color: #0f8b8d;
     box-shadow: 2 2px #CDCDCD;
     transform: translateY(2px);
   }
   .cmd-label{
    font-size: 1.1rem;
    color:#143642;
    font-weight: bold;
   }
   input.cmd{
    background: #ecf0f3;
    padding-top: 5px;
    padding-left: 10px;
    height: 30px;
    width: 300px;
    font-size: 14px;
    border-radius: 50px;
    }
    input.submit{
    background: #0f8b8d;
    text-align: center;
    padding: auto;
    height: 30px;
    width: 70px;
    font-size: 14px;
    border-radius: 50px;
    }
    .angles{
      display: flex;
      font-size: 1.5rem;
      color:#8c8c8c;
      font-weight: bold;
    }
    .angle{
      flex: 1;
    }
    .angle-number{
      font-size: 3rem;
    }
  </style>
<title>PROMETHEUS GroundStation</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
</head>
<body>
  <div class="topnav">
    <h1>PROMETHEUS GroundStation</h1>
  </div>
  <div class="content">
    <div class="card">
      <h2>Terminal</h2>
      <div id="cmd_box" style="height:150px;width:500px;border:1px solid #ccc;font:16px/26px;font-family: 'Courier New', monospace;overflow:auto;margin: auto;text-align: left;">
        <span id="strings"><br></span>  
      </div><br>
      <form id="cmd-form">
        <label class="cmd-label"> Command: </label>
        <input class="cmd" type="text" name="cmd" id="cmd-input">
        <input class="submit" type="submit" value="Send" onclick="getCmd()">
      </form><br>  
      <div class="angles" style="margin: auto;">
        <div class="angle">
          <span id="az" class="angle-number"></span>
          <br><label>Azimuth</label>
        </div>
        <div class="angle">
          <span id="el" class="angle-number"></span>
          <br><label>Elevation</label>
        </div>
      </div>
    </div>
    
  </div>
  
<script>
  var terminal = "---";
  var rot_gateway = `ws://${window.location.hostname}/rot_ws`;
  var cmd_gateway = `ws://${window.location.hostname}/cmd_ws`;
  var rot_websocket, cmd_websocket;
  window.addEventListener('load', onLoad);
  function initWebSocket() {
    console.log('Trying to open a WebSocket connection...');
    
    rot_websocket = new WebSocket(rot_gateway);
    rot_websocket.onopen    = onOpen;
    rot_websocket.onclose   = onClose;
    rot_websocket.onmessage = onRotMessage;

    cmd_websocket = new WebSocket(cmd_gateway);
    cmd_websocket.onopen    = onOpen;
    cmd_websocket.onclose   = onClose;
    cmd_websocket.onmessage = onCmdMessage;
  }
  function onOpen(event) {
    console.log('Connection opened');
  }
  function onClose(event) {
    console.log('Connection closed');
    setTimeout(initWebSocket, 2000);
  }
  function onRotMessage(event) {
    var angles = event.data.split(" ");
    
    document.getElementById('az').innerHTML = angles[0];
    document.getElementById('el').innerHTML = angles[1];
  }

  function onCmdMessage(event) {
    document.getElementById('strings').innerHTML += event.data + '<br>';
    var objDiv = document.getElementById("cmd_box");
    objDiv.scrollTop = objDiv.scrollHeight;
  }
  function onLoad(event) {
    initWebSocket();
    initButton();
  }
  
  function getCmd() {
    var prompt = document.getElementById("cmd-input").value;
    document.getElementById('strings').innerHTML += ('<a style="color:#4673a3";>$ ' + prompt + '</a> <br>');
    cmd_websocket.send(prompt);

    var objDiv = document.getElementById("cmd_box");
    objDiv.scrollTop = objDiv.scrollHeight;
  }

  var form = document.getElementById("cmd-form");
  
  form.addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent the form from submitting normally
    //getCmd();
    document.getElementById("cmd-input").value = "";
  });


</script>
</body>
</html>
)rawliteral";


bool ledState = 0;

void updateRotators() {
  ws_rotator.textAll(String(azimuth)+' '+String(elevation));
}

void updateTerminal(String str) {
  ws_command.textAll(str);
}

void WsMsgHandler_rot(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo*)arg;
  int i=0;
  String s;
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, data);
  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
      Serial.printf("DATA---> %s\n", data);
      if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
        return;
      } else {
        const float az_val = doc["azimuth"];
        const float el_val = doc["elevation"];
        Serial.println(az_val);
        Serial.println(el_val);

        azimuth = az_val;
        elevation = el_val;
      }

      updateRotators();
      angle_flag = true;
  }
}

void WsMsgHandler_cmd(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo*)arg;
  char buff[64];
  snprintf(buff, len+1, "%s", data, len);
  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
      Serial.printf("DATA---> %s          [%d]\n", buff, len);
  }
  strlcpy(msg, buff, inplen);
  Serial.println(msg);
  wifi_flag = true;
}

String processor(const String& var){
  Serial.println(var);
  if(var == "STATE"){
    if (ledState){
      return "ON";
    }
    else{
      return "OFF";
    }
  }
  return String();
}


typedef struct{
  uint8_t header[4];
  uint8_t packet_id;
  uint8_t payload[250];
}packet_t;

void printKStreamBytes(kaitai::kstream* ks, size_t numBytes) {
    for (int i = 0; i < numBytes; ++i) {
        uint8_t byteValue = ks->read_u1();
        //std::cout << "Byte " << i << ": " << std::hex << static_cast<int>(byteValue) << std::endl;
        Serial.printf("Byte %d: 0x%x\n", i, byteValue);
    }
}

void setup() 
{
  Serial.begin(115200);
  pinMode(pingo,INPUT);
  pinMode(pinf,OUTPUT); digitalWrite(pinf,0);
  servoAzimuth.attach(azimuth_pin);
  servoElevation.attach(elevation_pin);

  Serial.print("Setting AP (Access Point)…");
  // Remove the password parameter, if you want the AP (Access Point) to be open
  WiFi.softAP(ssid, password);

  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);

//....................................................................
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(200, "text/html", index_html); 
  });

  server.on("/get", HTTP_GET, [] (AsyncWebServerRequest *request) {
    String inputMessage;
    String inputParam;
    
    // GET cmd value on <ESP_IP>/get?cmd=<inputMessage>
    if (request->hasParam("cmd")) {
      inputMessage = request->getParam("cmd")->value();
      inputParam = "cmd";
      //ws_command.textAll(inputMessage);
      wifi_flag = true;
    }
    else if (request->hasParam("az")) {
      inputMessage = request->getParam("az")->value();
      inputParam = "az";
      azimuth = inputMessage.toFloat();
      Serial.print("AZIMUTH: ");
      Serial.println(azimuth);
      angle_flag = true;
    } 
    else if (request->hasParam("el")) {
      inputMessage = request->getParam("el")->value();
      inputParam = "el";
      elevation = inputMessage.toFloat();
      Serial.print("ELEVATION: ");
      Serial.println(elevation);
      angle_flag = true;
    } 
    else {
      inputMessage = "No message sent";
      inputParam = "none";
    }

    strcpy(msg, inputMessage.c_str());
    //Serial.println(inputMessage);
    
    //request->send(200, "text/html", "HTTP GET request sent to your ESP on input field (" 
    //                                 + inputParam + ") with value: " + inputMessage +
    //                                 "<br><a href=\"/\">Return to Home Page</a>");
    
    request->redirect("/");
  });


  server.addHandler(&ws_rotator);
  ws_rotator.onEvent(onWsEvent_rot);

  server.addHandler(&ws_command);
  ws_command.onEvent(onWsEvent_cmd);

  server.begin();


//....................................................................


  if (!LR.begin()) 
    {Serial.println("No LoRa shield detected! Stop!");SHIELD=false;return;}
  Serial.println("LoRa echo transmitter.");
  SX.setPower(PWR);
//LR.setConfig(SF,BW,4);       // if you want test different configuration (def: 9,6,4)
  showConfig();
  strlcpy(inpbuff,MESS,inplen);
  Serial.print("Close pin ");Serial.print(pingo);Serial.println(" to ground to send message");  
  LR.receiveMessMode();
}

void loop() 
{
  delay(200);
  if (!SHIELD) return;
  if (getInput()) {sendBuff();getReplay();}
  if ((nb=getSerialMsg())>0) {
    Serial.println("OK");
    if (sendSerialMsg())getReplay();
    //updateTerminal(recbuff);
  }
  if (wifi_flag){
    wifi_flag = false;
    if (sendSerialMsg())getReplay();
    //updateTerminal(recbuff);
  } 
  else if (LR.dataRead(recbuff,reclen)>0){
    Serial.println("Got something: ");
    //std::istringstream is(recbuff);
    //kaitai::kstream ks(&is);
    //kaitai::kstruct kst(&ks);
//    char buffer[] = {171, 186, 10, 10, 0, 204, 204, 204, 61, 204, 204, 76, 62, 152, 153, 153, 62, 204, 204, 204, 61, 204, 204, 76, 62, 152, 153, 153, 62, 204, 204, 204, 61, 204, 204, 76, 62, 152, 153, 153, 62, 0, 0, 240, 65, 21, 0, 22, 0, 23, 0, 11, 0, 12, 0, 13, 0, 100, 102, 134, 64, 48, 51, 243, 65};
    //char buffer[] = {171, 186, 0, 0, 10, 1, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85};
    //char* buffer; strcpy(buffer, recbuff);
    //size_t buffer_size = sizeof(buffer);

    for(int i=0; i<reclen; i++){
      Serial.printf("%x, ", recbuff[i]);
    }

    for(int i=0; i<reclen; i++){
      Serial.printf("%x, ", recbuff[i]);
    }

    std::istringstream stream(std::string(recbuff, reclen));

    // Create a kaitai::kstream from the Stream
    kaitai::kstream ks(&stream);
    //printKStreamBytes(&ks, buffer_size);

  
    packet_t *pckt = (packet_t *) recbuff;   
    Serial.printf("LENGTH: %d\n", reclen); 
    Serial.printf("Header[%x,%x,%x,%x] ID:%x \n", pckt->header[0], pckt->header[1], pckt->header[2], pckt->header[3], pckt->header[4], pckt->packet_id);

    delay(100); Serial.println("Parsing Packet ");
    
    Serial.println("------------------------");

    prometheus_t* datastream = NULL;

    try {
      datastream = new prometheus_t(&ks);

      Serial.printf("HEADER DESTINATION: 0x%x\n", datastream->header()->destination());
      Serial.printf("HEADER NODE:        0x%x\n", datastream->header()->node());
      Serial.printf("HEADER IDENTIFIER:  0x%x\n", datastream->header()->identifier());
      Serial.printf("HEADER FLAGS:       0x%x\n", datastream->header()->flags());
      Serial.printf("PACKET ID: %d\n", datastream->packet_id());

    } catch(const std::exception& e){
      Serial.println(e.what());
    }
    
    readPayload(datastream);
    
    Serial.println("------------------------");
    
    //int id = packet.packet_id();
    
    //for(int i=0; i < buffer_size; i++){
    //  Serial.printf("%x,", recbuff[i]);
    //}
    //updateTerminal(recbuff);
  }

  if (angle_flag){
    angle_flag = false;
    if (azimuth>180){azimuth = 180;} 
    else if (azimuth < 0) {azimuth = 0;}
    if (elevation>180){elevation = 180;} 
    else if (elevation < 0) {elevation = 0;}
    servoAzimuth.write((int)azimuth);
    servoElevation.write((int)elevation);
    updateRotators();
  }
  
  ws_rotator.cleanupClients();
}




void onWsEvent_rot(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
             void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.printf("WebSocket client #%u connected from %s\n", client->id(), client->remoteIP().toString().c_str());
      break;
    case WS_EVT_DISCONNECT:
      Serial.printf("WebSocket client #%u disconnected\n", client->id());
      break;
    case WS_EVT_DATA:
      WsMsgHandler_rot(arg, data, len);
      Serial.printf("DATA on the websocket\n");
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
}



void onWsEvent_cmd(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
             void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.printf("WebSocket client #%u connected from %s\n", client->id(), client->remoteIP().toString().c_str());
      break;
    case WS_EVT_DISCONNECT:
      Serial.printf("WebSocket client #%u disconnected\n", client->id());
      break;
    case WS_EVT_DATA:
      WsMsgHandler_cmd(arg, data, len);
      Serial.printf("DATA on the websocket\n");
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
}


boolean getInput()
{
  if (digitalRead(pingo)) return false;
  return true;
}

void sendBuff()
{
  blinkpinf(100,10);
  digitalWrite(pinf,LOW);
  sprintf(inpbuff, "%s:%3d\n", MESS, cnt++);
  Serial.print("> ");Serial.println(inpbuff);
  int f=LR.sendMess(inpbuff); 
  if (f<0) Serial.println("Error in transmission!");

  SX.setState(STDBY);
}

boolean sendSerialMsg()
{
  Serial.print("To ");Serial.print(dest);Serial.print(" > ");Serial.println(msg);
  char packet[64];
  char header[5];
  /*header[0] = 0xab;
  header[1] = 0xba;
  header[2] = '0';
  header[3] = '0';
  header[4] = 0;
  strcpy(packet, header);
  strcat(packet, msg);*/
  Serial.print(strlen(msg));
  int f=LR.sendMess(msg); 
  if (f<0) Serial.println("Error in transmission!");
  else Serial.println("Sent...");
  SX.setState(STDBY);
  return true;
}


void getReplay()
{
  LR.receiveMessMode();
  boolean OK=false;
  int i;
  for (i=0;i<RXTIMEOUT;i++)
    {if (LR.dataRead(recbuff,reclen)>0) {OK=true;break;} delay(10);}
  if (!OK) {Serial.println("No replay!");blinkpinf(50,20);return;}
  snprintf(data,63,format,SX.getLoraRssi(),SX.lastLoraPacketRssi(),SX.lastLoraPacketSnr());
  Serial.println(data);
  Serial.print("< ");Serial.println(recbuff); 
  int inc=strlen(inpbuff);
  if (strncmp(recbuff,inpbuff,inc)==0) {digitalWrite(pinf,HIGH);}
  else {blinkpinf(500,4);}
  updateTerminal(recbuff);
}


void blinkpinf(int time,int n)
{
  int i;
  byte p=1;
  for (i=0;i<n;i++) {digitalWrite(pinf,p);delay(time); p=p^1;}
  digitalWrite(pinf,0);
}

void showConfig()
{
  Serial.print("Replay timeout (millisec.): ");Serial.println(RXTIMEOUT*10); 
  Serial.print("Frequence: ");Serial.println(SX.readFreq()); 
  Serial.print("Transmit power (mW): ");Serial.println(SX.getPower(3)); 
  Serial.print("Preamble bytes: ");Serial.print(SX.getLoraPreambleLen());Serial.println("+4"); 
  snprintf(data,63,"SpFactor: %d BandW: %d Cr: %d",SX.getLoraSprFactor(),SX.getLoraBw(),SX.getLoraCr()); 
  Serial.println(data); 
  Serial.print("Rate (byte/sec): ");Serial.println(SX.getSRate());
}


boolean getSerialMsg()
{
  if (Serial.available()==0) return 0;
  String str = Serial.readString();
  
  const char* str1=str.c_str();
  strcpy(msg, str1); 
  int nb=strlen(str1);
  Serial.println("---------------------" + str + " " + nb + "---------------------------");
  
  return nb;
}


boolean sendWifiMsg()
{
  int f=LR.sendMess(msg); 
  if (f<0) Serial.println("Error in transmission!");
  else Serial.println("Sent WiFi Message...");
  SX.setState(STDBY);
  return true;
}

void readPayload(prometheus_t* datastream){
  kaitai::kstruct* payload = datastream->payload();
  
  if (datastream->packet_id() == 0) {
    prometheus_t::telemetry_t* tlm = (prometheus_t::telemetry_t*) payload;

    Serial.println("===ACCEL===");
    Serial.printf("x: %f\n", tlm->imu()->accel_x());
    Serial.printf("y: %f\n", tlm->imu()->accel_y());
    Serial.printf("z: %f\n", tlm->imu()->accel_z());

    Serial.println("===GYRO===");
    Serial.printf("x: %f\n", tlm->imu()->gyro_x());
    Serial.printf("y: %f\n", tlm->imu()->gyro_y());
    Serial.printf("z: %f\n", tlm->imu()->gyro_z());

    Serial.println("===MAG===");
    Serial.printf("x: %f\n", tlm->imu()->mag_x());
    Serial.printf("y: %f\n", tlm->imu()->mag_y());
    Serial.printf("z: %f\n", tlm->imu()->mag_z());


    Serial.println("\n===SUN SENSORS===");
    Serial.printf("X+: %d \t X-: %d\n", tlm->sun_sensor()->sun_xp(), tlm->sun_sensor()->sun_xn());
    Serial.printf("Y+: %d \t Y-: %d\n", tlm->sun_sensor()->sun_yp(), tlm->sun_sensor()->sun_yn());
    Serial.printf("Z+: %d \t Z-: %d\n", tlm->sun_sensor()->sun_zp(), tlm->sun_sensor()->sun_zn());


    Serial.println();
    Serial.printf("VBATT: %f\n", tlm->vbatt());
    Serial.printf("CPU TEMP: %f\n", tlm->cpu_temp());
  }
  else {
    prometheus_t::image_t* img = (prometheus_t::image_t*) payload;
    Serial.println("THIS IS AN IMAGE SEGMENT");
    //Serial.println(img);
  }

}