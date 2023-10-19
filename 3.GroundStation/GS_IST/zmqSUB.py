#!/usr/bin/python3
# Note: use Python 2 for older versions of GR
import pmt
import zmq
import time

# Open a ZeroMQ publisher socket on localhost, port 5555
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:5555")

doppler = 0.1

while(1):
  message = input("Enter message: ")
  msg = pmt.intern(message)
  sb = pmt.serialize_str(msg)
  socket.send(sb)
  doppler = doppler + 0.1
  time.sleep(1)

# Code ends here