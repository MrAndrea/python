# serial_test.py

import sys, time
import serial.tools.list_ports as portlist
import serial
import logging
import datetime
import re

ports = list( portlist.comports() )
for p in ports:
  print(p)


# This will hold received UART data
data = ""
stopMessage = "STOP\n"

titlelog = "#  Time          Speed  Torque  Rotation\n"
TX_messages = ["OD\r\n"]
#TX_messages = ["S 1728T22.60L"]

with open('dataDSP6001.txt', 'w') as f:
	f.write(titlelog)

# Set up serial port for read
serialPort = serial.Serial( port="COM6", baudrate=19200, bytesize=8, timeout=.5, stopbits=serial.STOPBITS_ONE )

print( '\nStarting Serial Port Send' )

with open('dataDSP6001.txt', 'a') as f:
    for x in range(0, 3):
        for msg in TX_messages:
            serialPort.write( msg.encode() )
            data = serialPort.readline()
            if len(data) == 13:
                dps6001_data = re.split("[S,T,R,L]", ''.join(data.decode()))
                from datetime import datetime
                date = datetime.now().strftime("%H:%M:%S,%f")[:-3]
                f.write(repr(x) + '  ' + date + '  ' + dps6001_data[1] + '   ' + dps6001_data[2] + '  ' + data.decode()[12] + '\n')
            
print('Closing Serial Port Send')
serialPort.close()


