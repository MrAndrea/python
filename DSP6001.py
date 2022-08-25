# -------------------------------------------------------------------------
# IIT - iCub Tech 2022
# Basic script for acquiring data from DSP6001 Dynamometer Controller
#
# Written by A. Mura
# <andrea.mura@iit.it>
# -------------------------------------------------------------------------

import sys, time
import serial.tools.list_ports as portlist
import serial
import logging
import datetime
import re

print('\n-------------------------------------------------\nChecking COM ports...')
ports = list( portlist.comports() )
for p in ports:
  print(p)

sample_number = input("\n-------------------------------------------------\nEnter number of sample: ")

filelog = 'dataDSP6001.txt'
titlelog = "#\tTime\tSpeed\tTorque\tRotation\n"
COMport = 'COM3'
TX_messages = ["OD\r\n"]

with open(filelog, 'w') as f:
	f.write(titlelog)

# Set up serial port for read
serialPort = serial.Serial( port=COMport, baudrate=19200, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE )

print('\n-------------------------------------------------\nStarting Serial Port', COMport)

with open(filelog, 'a') as f:
    for x in range(0, int(sample_number)):
        print('Message',x,'of',sample_number, end='\r')
        for msg in TX_messages:
            serialPort.write( msg.encode() )
            data = serialPort.readline()
            if len(data) == 15:
                dps6001_data = re.split("[S,T,R,L]", ''.join(data.decode()))
                from datetime import datetime
                date = datetime.now().strftime("%H:%M:%S,%f")[:-3]
                f.write(repr(x) + '\t' + date + '\t' + dps6001_data[1] + '\t' + dps6001_data[2] + '\t' + data.decode()[12] + '\n')
            
print('\nClosing Serial Port',COMport,'\n')
print('-------------------------------------------------\n')
print(filelog,'ready\n')
serialPort.close()

