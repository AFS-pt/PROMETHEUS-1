#ifndef __AES_H__
#define __AES_H__

//#include <avr/pgmspace.h>

#if (defined(__AVR__))
#include <avr\pgmspace.h>
#else
#include <pgmspace.h>
#endif
/*
 ---------------------------------------------------------------------------
 Copyright (c) 1998-2008, Brian Gladman, Worcester, UK. All rights reserved.

 LICENSE TERMS

 The redistribution and use of this software (with or without changes)
 is allowed without the payment of fees or royalties provided that:

  1. source code distributions include the above copyright notice, this
     list of conditions and the following disclaimer;

  2. binary distributions include the above copyright notice, this list
     of conditions and the following disclaimer in their documentation;

  3. the name of the copyright holder is not used to endorse products
     built using this software without specific written permission.

 DISCLAIMER

 This software is provided 'as is' with no explicit or implied warranties
 in respect of its properties, including, but not limited to, correctness
 and/or fitness for purpose.
 ---------------------------------------------------------------------------
 Issue 09/09/2006

 This is an AES implementation that uses only 8-bit byte operations on the
 cipher state.
 */
 
typedef unsigned char byte ;

#define N_ROW                   4
#define N_COL                   4
#define N_BLOCK   (N_ROW * N_COL)
#define N_MAX_ROUNDS           14
#define KEY_SCHEDULE_BYTES ((N_MAX_ROUNDS + 1) * N_BLOCK)
#define SUCCESS (0)
#define FAILURE (-1)

class AES
{
 public:

/*  The following calls are for a precomputed key schedule

    NOTE: If the length_type used for the key length is an
    unsigned 8-bit character, a key length of 256 bits must
    be entered as a length in bytes (valid inputs are hence
    128, 192, 16, 24 and 32).
*/

/*  Set the cipher key using random generator */
  byte set_key (int keylen) ;
  
/* Encrypt a buffer of n_block blocks (16 bytes long). Buffer plain is overwritten by cipher values. */
  byte encrypt_buff (byte * plain, int n_block);
  
/* Decrypt a buffer of n_block blocks (16 bytes long). Buffer cipher is overwritten by plain values. */
  byte decrypt_buff (byte * cipher,int n_block); 

/***************/  
  byte encrypt (byte plain [N_BLOCK], byte cipher [N_BLOCK]) ;
  byte decrypt (byte cipher [N_BLOCK], byte plain [N_BLOCK]) ;
  void clean () ;  // delete key schedule after use
  void copy_n_bytes (byte * dest, byte * src, byte n) ;
  void start_key (byte * d, byte nn);
  
  byte key_sched [KEY_SCHEDULE_BYTES] ;
  
 private:
  int round ;
//  byte key_sched [KEY_SCHEDULE_BYTES] ;
} ;


#endif
