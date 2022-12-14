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
import matplotlib.pyplot as plt
from datetime import datetime
from termcolor import colored
from colorama import init
from time import sleep
from threading import Thread

# task that runs at a fixed interval
def background_task(interval_sec):
    # run forever
    while True:
        # block for the interval
        sleep(interval_sec)
        # perform the task
        print('Background task!')

# -------------------------------------------------------------------------
# General
# -------------------------------------------------------------------------
filelog = 'dataDSP6001.txt'
titlelog = "#\tTime\tSpeed\tTorque\tRotation\n"
com_menu = 1
cmd_menu = 1
com_port = ''
# Answer format 'S    0T0.488R\r\n'

class dsp6001:
    def __init__(self, prog, time, speed, torque, rotation, freq):
        self.prog = prog
        self.time = time
        self.speed = speed
        self.torque = torque
        self.rotation = rotation
        self.freq = freq
        
# -------------------------------------------------------------------------
# DSP6001 COMMAND SET
# -------------------------------------------------------------------------
dsp6001_cmd = [
    "*IDN?",         # Returns Magtrol Identification and software revision
    "OD",            # Prompts to return speed-torque-direction data string
    "PR",            # 
    "Q#",            # 
    "N#",            # 
    "Custom",        # 
    "Quit"           # Exit
    ]
dsp6001_end = "\r\n"

#print('Starting background task...')
#daemon = Thread(target=background_task, args=(3,), daemon=True, name='Background')
#daemon = Thread(target=data_acquisition, args=(),daemon=True, name='data_acquisition')
#daemon.start()
            


# -------------------------------------------------------------------------
# Data acquisition
# -------------------------------------------------------------------------
def data_acquisition():
    global sample_number
    global com_port
    valid = False
    while not valid: #loop until the user enters a valid int
        try:
            print('-------------------------------------------------');
            print(colored('Enter number of samples:  ', 'green'), end='\b')
            sample_number = int(input())
            break
            valid = True
        except ValueError:
            print('Please only input digits')

    TX_messages = [cmd_menu+dsp6001_end]
    #write_filedata(com_port, sample_number, TX_messages)
    daemon = Thread(target=write_filedata, args=(com_port, sample_number, TX_messages), daemon=True, name='write_filedata')
    daemon.start()
# -------------------------------------------------------------------------
# Write data in the file
# -------------------------------------------------------------------------
def write_filedata(com_port, sample_number, TX_messages):
    sample = []
    with open(filelog, 'w') as f:
        f.write(titlelog)

    serialPort = open_serial_port(com_port)
    
    with open(filelog, 'a') as f:
        for x in range(1, int(sample_number)+1):
            print('Message',x,'of',sample_number, end='\r')
            for msg in TX_messages:
                serialPort.write( msg.encode() )
                data = serialPort.readline().decode()
                data = "S    0T0.488R\r\n"      # fake message
                if re.search("^S.+T.+R.+",data):
                    dps6001_data = re.split("[S,T,R,L]", ''.join(data))
                    date = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    sample.append(dsp6001(repr(x), date, dps6001_data[1], dps6001_data[2], data[12], "f"))
                    f.write(sample[x-1].prog + '\t' + sample[x-1].time + '\t' + sample[x-1].speed + '\t' + sample[x-1].torque + '\t' + sample[x-1].rotation + '\t' + sample[x-1].freq + '\n')
    close_serial_port(serialPort, com_port)            
    print('\n',filelog,'ready')
    #plot_data(sample)
    #daemon.stop()

# -------------------------------------------------------------------------
# Plot data
# -------------------------------------------------------------------------
def plot_data(var):
    time = []
    torque = []
    speed = []
    for obj in var: time.append(obj.time)
    for obj in var: speed.append(obj.speed)
    for obj in var: torque.append(obj.torque)
    
    plt.plot(time, speed, label = "speed")
    plt.plot(time, torque, label = "torque")
    plt.xlabel('time [s]')
    plt.ylabel('[Nmm]')
    plt.title('MAGTROL data')
    plt.legend()
    plt.grid(True)
    plt.draw()
    plt.pause(2.001)
    #input("Press [enter] to continue.")
    #plt.show(block=False)  
    
# -------------------------------------------------------------------------
# Send command to Magtrol
# -------------------------------------------------------------------------
def send_cmd_magtrol(com_menu):
    global com_port
    TX_messages = [com_menu+dsp6001_end]
    serialPort = open_serial_port(com_port)
    for msg in TX_messages:
        serialPort.write(msg.encode())
        print(colored('\nMagtrol says:', 'yellow'), serialPort.readline().decode())
    close_serial_port(serialPort, com_port) 
    
# -------------------------------------------------------------------------
# Open serial port
# -------------------------------------------------------------------------
def open_serial_port(com_port):
    # Set up serial port for read
    ser = serial.Serial()
    ser.baudrate = 19200
    ser.port = com_port
    ser.bytesize = 8
    ser.timeout = 1
    ser.stopbits = serial.STOPBITS_ONE
    #serialPort = serial.Serial(port=com_port, baudrate=19200, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)
    if(ser.isOpen() == False):
        ser.open()
    #print('-------------------------------------------------');
    #print('Starting Serial Port', com_port)
    return ser
# -------------------------------------------------------------------------
# Close serial port
# -------------------------------------------------------------------------
def close_serial_port(serialPort, com_port):
    #print('Closing Serial Port',com_port)
    #print('-------------------------------------------------')
    serialPort.close()

# -------------------------------------------------------------------------
# Scan COM ports
# -------------------------------------------------------------------------
def scan_com_port():
    global com_port
    global com_menu
    com_list = []
    print('-------------------------------------------------');
    print('Scan COM ports...')
    ports = list(portlist.comports())
    for p in ports:
      print('[',com_menu,']: ', p)
      com_menu+=1
      com_list.append(p.device)
    com_port = input_keyboard(com_list)
    
# -------------------------------------------------------------------------
# Input command
# -------------------------------------------------------------------------
def input_command():
    global cmd_menu
    cmd_menu=1
    print('-------------------------------------------------');
    print('List of commands:')
    for p in dsp6001_cmd:
      print('[',cmd_menu,']: ', p)
      cmd_menu+=1
    cmd_menu = input_keyboard(dsp6001_cmd)
    
# -------------------------------------------------------------------------
# Keyboard input
# -------------------------------------------------------------------------
def input_keyboard(list):
    valid = False
    #menu = 1
    while not valid: #loop until the user enters a valid int
        try:
            print(colored('Choose menu:  ', 'green'), end='\b')
            menu = int(input())
            if menu>=1 and menu<=len(list):
                menu = list[menu-1]
                return menu
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
    init()
    try:
        if len(sys.argv) == 1:
            global cmd_menu   
            print('-------------------------------------------------');
            print(colored('         MAGTROL DSP6001 control script          ', 'white', 'on_green'))
            scan_com_port()
            while cmd_menu!='Quit': 
                input_command()
                if cmd_menu == 'OD':
                    data_acquisition()
                elif cmd_menu == 'Custom':
                    print(colored('Type the command to send:  ', 'green'), end='\b')
                    message_send = input()
                    send_cmd_magtrol(message_send)
                else:
                    send_cmd_magtrol(cmd_menu)
            #daemon.stop()
        elif sys.argv[1] == '--auto':
            null
    except IndexError:
        print(colored('Working in progress for other features...', 'red'), end='\b')
if __name__ == "__main__":
    main()
