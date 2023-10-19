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
*  - begin() : initialize shield for LoRa protocol (default power=10dBm).
*    If shield is not here it returns false.
*  - sendMess() : send message (as null terminated string or byte array) 
*  - receiveMessMode() and dataRead() to receive message.
*    receiveMessMode() set shield in continuous receving mode and then you have 
*    to poll message coming with dataRead() in a loop. 
*    
* Author: Daniele Denaro 2015
*/

#ifndef LORA_h
#define LORA_h

#include <libraries/SX1278.h>

#define LoraTxTimeout 1000

class LORA
{
  public:

/******* With AES256 cryptography and sender/destination addresses ***********/
  
/**** Initialize ***/

/* Start shield in LoRa mode and prepare 32 byte key for AES256 crypto*/
  bool begin(unsigned int keyval);
/* Change shield in LoRa mode, if it was already started in different mode
   with AES256 key creation */
  void setModeLora(unsigned int keyval);
  
/* Set a network address if you like to create a network with net address and
*  a range of device addresses. In this case device adresses range must be a
*  2 power value (8,16,32,64,128,256 ecc.). Besides net address value must be 
*  lower than 0xFFFF/device_range (I.E. 0x1FFF,0xFFF,0x7FF,0x3FF,0x1FF,0xFF ecc) 
*  This function MUST be called before calling sender and receiver functions that
*  use sub-net adressess!
*/
   bool setNetAddress(unsigned int netAdd, unsigned int devRange);  

/**** Sending ****/

/* Send buffer mess adding a word as addressee (destAdd) and a word as sending 
*  address. 
*  A random byte is added just to make message unique.
*  Sending address, random byte and message are encoded with AES256 cryptography
*  using predefined 32 key. Length of encoded segment is a multiple of 16 bytes
*  blocks.
*  Destination word (two bytes) is not encoded.
*/
  int sendMess(unsigned int destAdd, unsigned int sendAdd, byte *mess, int lmess);      

/* As previous function but using predefined network address and device address
*  range. So, devAdd is the subaddress of device inside the network dominion and
*  sendSubAdd is the subaddress of sender.
*/
   int sendNetMess(unsigned int devSubAdd, unsigned int sendSubAdd, byte *mess, int lmess);

/**** Receiving ****/

/* Set shield in continuous receiving mode. Use dataRead function  
   to verify if data arrived */
  void receiveMessMode();

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
  int receiveMess(unsigned int destAdd, unsigned int sendAdd, byte *buff, byte maxlen); 

/* As previous function but using predefined network address and device address
*  range. So, devAdd is the subaddress of device inside the network dominion and
*  sendSubAdd is the subaddress of sender.
*/
  int receiveNetMess(unsigned int devSubAdd, unsigned int sendSubAdd, byte *buff, byte maxlen );

/* Get sender address of last message received */
  unsigned int getSender(); 
/* Get sender sub-address in case of network address system */
  unsigned int getSubNetSender();
/* Get the clean message buffer (without any other prefix) of last message 
   received */   
  byte* getMessage();
  byte getMarker();

/***************** Basic function (no crypto) **************************/

/* Start shield in LoRa mode */  
  bool begin();
/* Change shield in LoRa mode, if it was already started in different mode */
  void setModeLora();
  
/*** Send ***/

/* Send message (packet) mlen long (or null terminated string).
   Return 0 if ok (sent) or -1 if problem (not sent) */  
  int sendMess(char mess[]);
  int sendMess(byte mess[],byte mlen);

/*** Receive ***/
  
/***************************************************************************/     

/* Data arrived ? If yes, data are copied into mess buffer and function 
   returns number of bytes and mess is a null terminated string.
   If not, function returns 0 (mess = 0 length string)*/
  int dataRead(char mess[],byte maxlen);
/* Buff is a byte array and is not null terminated */
  int dataRead(byte buff[],byte blen);

/*** Further functions ***/

/* CAD monitor for sec seconds and receive message if it is coming. 
   It returns 0 or message length (single packet receiving mode)*/
   int waitForMess(char mess[],byte mlen, float sec);
   int waitForMess(byte buff[],byte blen, float sec);
  
/* Monitor channel for sec seconds. Return true if preamble is detected */
  bool CADmonitor(float sec);  

/* Set timeout (in milliseconds) for each listen period. (Def.: 100)*/  
  void setRxTimeout(int tmillis);
  int getRxTimeout();

/*Configuration 
  Spreading Factor sprf: 6 to 12 (def.: 7) 
  Bandwidth bw: 0 to 9 (def.: 7 (125kHz))
  Coding Rate cr: 1 to 4 (def.: 1)*/   
  void setConfig(byte sprf, byte bw, byte cr);

/* Set on/off automatic payload CRC computation/detection  (def.: off)*/
  void setPayloadCRC(byte yesno);
  
  
  
  private:
  unsigned int senderAddress;
  byte *receivedMessage;
  int receivedMessLen;
  unsigned int subNetSenderAddress;
  byte marker;
  
  unsigned int netAddress;
  byte r2p;
  unsigned int mask;
}; 


#endif
