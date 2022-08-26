# -------------------------------------------------------------------------
# IIT - iCub Tech 2022
# Python script for acquiring data from DSP6001 Dynamometer Controller
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
# General
# -------------------------------------------------------------------------
filelog = 'dataDSP6001.txt'
titlelog = "#\tTime\tSpeed\tTorque\tRotation\n"
com_menu = 1
cmd_menu = 1
com_port = ''

# -------------------------------------------------------------------------
# DSP6001 COMMAND SET
# -------------------------------------------------------------------------
dsp6001_cmd = [
    "*IDN?",        # Returns Magtrol Identification and software revision
    "OD",           # Prompts to return speed-torque-direction data string
    "PR"            # 
    ]
dsp6001_end = "\r\n"

# -------------------------------------------------------------------------
# Data acquisition
# -------------------------------------------------------------------------
def data_acquisition():
    print('-------------------------------------------------');
    sample_number = input("Enter number of samples: ")

    TX_messages = [cmd_menu+dsp6001_end]

    with open(filelog, 'w') as f:
        f.write(titlelog)

    # Set up serial port for read
    serialPort = serial.Serial( port=com_port, baudrate=19200, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE )

    print('-------------------------------------------------');
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
                
    print('\nClosing Serial Port',com_port)
    print('-------------------------------------------------')
    print(filelog,'ready')
    serialPort.close()

# -------------------------------------------------------------------------
# Scan COM ports
# -------------------------------------------------------------------------
def scan_com_port():
    global com_port
    global com_menu
    valid = False
    com_list = []
    print('-------------------------------------------------');
    print('Scan COM ports...')
    ports = list( portlist.comports() )
    for p in ports:
      print('[',com_menu,']: ', p)
      com_menu+=1
      com_list.append(p.device)

    while not valid: #loop until the user enters a valid int
        try:
            print('-------------------------------------------------');
            com_menu = int(input("Choose the COM port: "))
            if com_menu>=1 and com_menu<=len(com_list):
                com_port = com_list[com_menu-1]
                break
                valid = True
            else: 
                print('Please only input number in the brackets')
        except ValueError:
            print('Please only input digits')

# -------------------------------------------------------------------------
# Input command
# -------------------------------------------------------------------------
def input_command():
    global cmd_menu
    valid = False
    print('-------------------------------------------------');
    for p in dsp6001_cmd:
      print('[',cmd_menu,']: ', p)
      cmd_menu+=1
    while not valid: #loop until the user enters a valid int
        try:
            print('-------------------------------------------------');
            cmd_menu = int(input("Choose the command to send: "))
            if cmd_menu>=1 and cmd_menu<=len(dsp6001_cmd):
                cmd_menu = dsp6001_cmd[cmd_menu-1]
                break
                valid = True
            else: 
                print('Please only input number in the brackets')
        except ValueError:
            print('Please only input digits')

# -------------------------------------------------------------------------
# main
# -------------------------------------------------------------------------
def main():
    scan_com_port()
    input_command()
    if cmd_menu == 'OD':
        data_acquisition()

if __name__ == "__main__":
    main()

