/*
  Copyright (c) 2015 Daniele Denaro.  All right reserved.

  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.
*/

/******************************************************************************/
/* Class LORA. 
*  It semplifies class SX1278 in case of LoRa protocol using.
*  Just use begin function and sendMess or receiveMessMode to communicate.
*  Principal functions:
*  - begin() : initialize shield for LoRa protocol (default power: 10dBm).
*    If shield is not here it returns false.
*  - sendMess() : send message (as null terminated string or byte array) 
*  - receiveMessMode() and dataRead() to receive message.
*    receiveMessMode() set shield in continuous receving mode and then you have 
*    to poll message coming with dataRead() in a loop. 
*    
* Author: Daniele Denaro 2015
*/

#include <libraries/LORA.h>


/******* With AES256 cryptography and sender/destination addresses ***********/

/********* Initializing ********/

/* Start shield in LoRa mode and prepare 32 byte key for AES256 crypto*/
bool LORA::begin(unsigned int keyval)
{
  if (!begin()) return false;
  SX.createKey(keyval);
  return true;
}

/* Change shield in LoRa mode, if it was already started in different mode
   with AES256 key creation */
void LORA::setModeLora(unsigned int keyval)
{
  setModeLora();
  SX.createKey(keyval);
}

/* Set a network address if you like to create a network with net address and
*  a range of device addresses. In this case device adresses range must be a
*  2 power value (8,16,32,64,128,256 ecc.). Besides net address value must be 
*  lower than 0xFFFF/device_range (I.E. 0x1FFF,0xFFF,0x7FF,0x3FF,0x1FF,0xFF ecc) 
*  This function MUST be called before calling sender and receiver functions that
*  use sub-net adressess!
*/
bool LORA::setNetAddress(unsigned int netAdd, unsigned int devRange)
{
    r2p=log(devRange)/log(2);
    unsigned int devR=1<<r2p;
    if (devR<devRange) {r2p++;}
    devRange=1<<r2p;
    mask=devRange-1;
    long net=netAdd << r2p;
    if (net>0xffff) return false;
    netAddress=net;
    return true;
}

/******** Sending **********/
/* Send buffer mess adding a word as addressee (destAdd) and a word as sending 
*  address. 
*  A random byte is added just to make message unique.
*  Sending address, random byte and message are encoded with AES256 cryptography
*  using predefined 32 key. Length of encoded segment is a multiple of 16 bytes
*  blocks.
*  Destination word (two bytes) is not encoded.
*/
int LORA::sendMess(unsigned int destAdd, unsigned int sendAdd, byte *mess, int lmess)
{
  int lenEnc=lmess+2+1;                  //len of buffer segment to encode 
  int nbk=int(ceil((float)lenEnc/16));
  lenEnc=nbk*16;
  int lenBuff=lenEnc+2;                  //len of total buffer to send
  byte *buff=(byte *)calloc(lenBuff,1);  //buffer to send
  buff[0]=highByte(destAdd);buff[1]=lowByte(destAdd);  //dest address plain
  byte *buffEnc=&buff[2];                //buffer segment to encode
  
  buffEnc[0]=random(256);                //just to make message univocal
  buffEnc[1]=highByte(sendAdd);buffEnc[2]=lowByte(sendAdd); //sender address
  byte *buffMess=&buffEnc[3];            //message segment
  memcpy(buffMess,mess,lmess);           //fill with message
  if (SX.encryptBuff(buffEnc,nbk)==NULL) Serial.println("Errore!!!");
  int ret=sendMess(buff,lenBuff);
  free(buff);
  return ret;
}

/* As previous function but using predefined network address and device address
*  range. So, devAdd is the subaddress of device inside the network dominion and
*  sendSubAdd is the subaddress of sender.
*/
int LORA::sendNetMess(unsigned int devSubAdd, unsigned int sendSubAdd, byte *mess, int lmess)
{
  unsigned int destAdd=netAddress+devSubAdd;
  unsigned int sendAdd=netAddress+sendSubAdd;
  return sendMess(destAdd,sendAdd,mess,lmess);
}
/*********** Receiving **********/

/* Set shield in continuous receiving mode. Use dataRead function to 
   to verify if data is arrived */
void LORA::receiveMessMode()
{
  SX.setState(STDBY);
  digitalWrite(TxEN, LOW);
  digitalWrite(RxEN, HIGH);
  SX.setState(FSRX);
  SX.clearAllLoraFlag();
  SX.setState(RXCONT);
}

/* Receive incoming message into the buffer buff
*  If no message is incoming, return 0.
*  If message is incoming compare addressee (that is plain) with destAdd. 
*  If addressee is not correct return 0. (I.E is not a message for the receiver)
*  Then decode message and compare sender with sendAdd. If sender is not correct
*  return -1. But if sendAdd parameter is 0 all messages are accepted.
*  Finally, return the length of the sole message (without addresses).
*  The message pointer can be obtained by getMess() function.
*  The sender address can be obtained by getSender() function. 
* 
*/
int LORA::receiveMess(unsigned int destAdd, unsigned int sendAdd, byte *buff, byte maxlen )
{
  int len=0;
  if ((len=dataRead(buff,maxlen))==0) return 0;

  if (buff[0]!=highByte(destAdd)) return 0;
  if (buff[1]!=lowByte(destAdd)) return 0;
  
  int lenEnc=len-2;
  byte *buffEnc=&buff[2];
  int nbk=int(ceil((float)lenEnc/16));
  
  SX.decryptBuff(buffEnc,nbk);
  
  marker=buffEnc[0];
  senderAddress=word(buffEnc[1],buffEnc[2]);
  receivedMessage=&buffEnc[3];
  receivedMessLen=lenEnc-3;
  if (sendAdd!=0) {if (senderAddress!=sendAdd) return -1;}
  return len-5;
}

/* As previous function but using predefined network address and device address
*  range. So, devAdd is the subaddress of device inside the network dominion and
*  sendSubAdd is the subaddress of sender.
*/
int LORA::receiveNetMess(unsigned int devSubAdd, unsigned int sendSubAdd, byte *buff, byte maxlen )
{
  unsigned int destAdd=netAddress+devSubAdd;
  int ret=receiveMess(destAdd,0,buff,maxlen);
  if (ret<=0) return ret;
  subNetSenderAddress=senderAddress & mask;
  unsigned int senderNet=(senderAddress>>r2p)<<r2p;
  if (senderNet!=netAddress) return -2;
  if (sendSubAdd!=0) {if (subNetSenderAddress!=sendSubAdd) return -1;}
  return ret;
}

/* Get sender address of last message received */
unsigned int LORA::getSender() {return senderAddress;}
/* Get sender sub-address in case of network address system */
unsigned int LORA::getSubNetSender() {return subNetSenderAddress;}
/* Get the clean message buffer (without any other prefix) of last message 
   received */ 
byte* LORA::getMessage(){return receivedMessage;} 

byte LORA::getMarker(){return marker;}

/***************** Basic function (no crypto) **************************/

/* Start shield in LoRa mode without crypto*/
bool LORA::begin()
{
  if (!SX.begin()) return false;
  delay(1);
  setModeLora();
  return true;
}

/* Change shield in LoRa mode, if it was already started in different mode 
  (no crypto)*/
void LORA::setModeLora()
{
  SX.setState(SLEEP);
  SX.startModeLORA();
  //SX.SPIwrite(0x06,0x6C);SX.SPIwrite(0x07,0x80); //default freq. 
  SX.setFreq(433);
  setConfig(7,7,1);
  SX.setState(STDBY);
}

/* Send message (packet) mlen long (or null terminated string).
   Return 0 if ok (sent) or -1 if problem (not sent) */
int LORA::sendMess(char mess[])
{ char packet[255];
  char header[4] = {0xab, 0xba, 0x01, 0x01};
  int plen=strlen(mess) + 4;
  memcpy(packet, header, 4);
  memcpy(&packet[4], mess, strlen(mess));
  Serial.printf("\n packet (%dB->%dB): ", strlen(mess), plen);
  Serial.println(packet);
  return sendMess((byte*)packet,plen);}


int LORA::sendMess(byte mess[],byte mlen)
{
  SX.setState(STDBY);
  SX.setState(FSTX);
  delayMicroseconds(100);  

  digitalWrite(RxEN, LOW);
  digitalWrite(TxEN, HIGH);

  SX.setLoraDataToSend(mess,mlen);
  SX.clearLoraFlag(TxDone);
  SX.setState(TX);
  delayMicroseconds(100);  
  int i;
  int n=((mlen+SX.getLoraPreambleLen())*20)/SX.getSRate()+40;
//  Serial.println(n);
  for(i=0;i<n;i++) {if (SX.getLoraFlag(TxDone)) return 0; else delay(100);}
  SX.setState(STDBY);

  digitalWrite(TxEN, LOW);

  return -1;
}

/*** continuous receiving mode ***/

/* Data arrived ? If yes, data are copied into mess buffer and function 
   returns number of bytes and mess is a null terminated string.
   If not, function returns 0 (mess = 0 length string)*/
int LORA::dataRead(char mess[],byte maxlen)
{int nc=dataRead((byte*)mess,maxlen);mess[nc]=0;return nc;}

/* Buff is a byte array and is not null terminated */
int LORA::dataRead(byte buff[],byte blen)
{
  if (!SX.getLoraFlag(RxDone)) return 0;
  SX.clearAllLoraFlag();
  if (SX.getLoraFlag(PayloadCrcError)) {SX.discardLoraRx();return -2;}
  return SX.readLoraData(buff,blen);
}

/*** single packet receiving mode ***/

/* CAD monitor for sec seconds and receive message if coming. It returns 0 or
   message length (or -1 if header invalid or -2 il CRV invalid)*/
int LORA::waitForMess(char mess[],byte mlen, float sec)
{int nc=waitForMess((byte*)mess,mlen,sec);mess[nc]=0;return nc;}

int LORA::waitForMess(byte buff[],byte blen, float sec)
{
  if (!CADmonitor(sec)) return 0;
  SX.setLoraRxByteTout(300);
  SX.clearAllLoraFlag();

  digitalWrite(TxEN, LOW);
  digitalWrite(RxEN, HIGH);

  SX.setState(FSRX);
  SX.setState(RXSING);
  int fend=-1;
  int i;
  for (i=0;i<100;i++)
  {if ((fend=SX.getLoraRxEndFlag())==0) delay(100); else break;}
  SX.setState(STDBY);
  if (fend<=0) return -1; 
  if (SX.getLoraFlag(PayloadCrcError)) {SX.discardLoraRx();return -2;}
  return SX.readLoraData(buff,blen);
}

/* Monitor channel for sec seconds. Return true if preamble is detected */
bool LORA::CADmonitor(float sec)
{
  SX.setState(STDBY);
  SX.clearAllLoraFlag();
  bool f=false;
  unsigned int n=int(sec*1000);
  unsigned int i;
  for (i=0;i<n;i++) 
   {
     SX.setState(CAD);while (!SX.getLoraFlag(CadDone)) delay(1);
     if (SX.getLoraFlag(CadDetected)) {f=true;break;} 
   }
  return f; 
}

/* Set timeout (in milliseconds) for each listen period. (Def.: 100)*/ 
void LORA::setRxTimeout(int tmillis)
{SX.setLoraRxTimeout(tmillis);}

int LORA::getRxTimeout()
{return SX.getLoraRxTimeout();}

/*Configuration 
  Spreading Factor sprf: 6 to 12 (def.: 7) 
  Bandwidth bw: 0 to 9 (def.: 7 (125kHz))
  Coding Rate cr: 1 to 4 (def.: 1)
*/   
void LORA::setConfig(byte sprf, byte bw, byte cr)
{
  SX.setLoraSprFactor(sprf);
  SX.setLoraBw(bw);
  SX.setLoraCr(cr);
}

/* Set on/off automatic payload CRC computation/detection  (def.: off)*/
void LORA::setPayloadCRC(byte yesno)
{
  SX. setLoraCrc(yesno);
}

