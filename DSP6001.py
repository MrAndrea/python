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

# -------------------------------------------------------------------------
valid = False
com_menu = 1
com_list = []
print('\n-------------------------------------------------');
print('Checking COM ports...')
ports = list( portlist.comports() )
for p in ports:
  print('[',com_menu,']: ', p)
  com_menu+=1
  com_list.append(p.device)

while not valid: #loop until the user enters a valid int
    try:
        print('\n-------------------------------------------------');
        com_menu = int(input("Choose the COM port: "))
        if com_menu>=1 and com_menu<=len(com_list):
            com_port = com_list[com_menu-1]
            break
            valid = True #if this point is reached, x is a valid int
        else: 
            print('Please only input number in the brackets')
    except ValueError:
        print('Please only input digits')

# -------------------------------------------------------------------------
print('\n-------------------------------------------------');
sample_number = input("Enter number of samples: ")

filelog = 'dataDSP6001.txt'
titlelog = "#\tTime\tSpeed\tTorque\tRotation\n"
TX_messages = ["OD\r\n"]

with open(filelog, 'w') as f:
	f.write(titlelog)

# Set up serial port for read
serialPort = serial.Serial( port=com_port, baudrate=19200, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE )

print('\n-------------------------------------------------');
print('Starting Serial Port', com_port)

with open(filelog, 'a') as f:
    for x in range(1, int(sample_number)+1):
        print('Message',x,'of',sample_number, end='\r')
        for msg in TX_messages:
            serialPort.write( msg.encode() )
            data = serialPort.readline()
            if len(data) == 15:
                dps6001_data = re.split("[S,T,R,L]", ''.join(data.decode()))
                from datetime import datetime
                date = datetime.now().strftime("%H:%M:%S,%f")[:-3]
                f.write(repr(x) + '\t' + date + '\t' + dps6001_data[1] + '\t' + dps6001_data[2] + '\t' + data.decode()[12] + '\n')
            
print('\nClosing Serial Port',com_port,'\n')
print('-------------------------------------------------')
print(filelog,'ready\n')
serialPort.close()

