#!/usr/bin/python
#########################################################################################
#                                                                                       #
# Logan Blakely                                                                         #
# 6/1/17                                                                                #
#                                                                                       #
# Internetworking Protocols - IRC Project                                               #
# Portland State University 2017                                                        #
#                                                                                       #
# Implements the client side of an IRC.  See accompanying RFC document for complete     #
#     specifications.                                                                   #
#                                                                                       #
#########################################################################################

from datetime import datetime
import socket
import sys
import select


server_address = ('localhost', 6000)
max_size = 1000

#Create a TCP/IP socket
print('Staring the client at', datetime.now())
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connect the socket ot the port where the server is listening
print('connecting to {} port {}' .format(*server_address))
sock.connect(server_address)

#Create the 'inputs' list for select.select
socket_list = [sys.stdin, sock]
shutDownFlag = 0;  #Flag for if the server severs the connection

#Loop waiting for messages from the server
while(1):
    readable, writeable, exceptional = select.select(socket_list, [],[]) 

    for i in readable:
        #Read from the socket (server message)
        if i == sock:
            data = sock.recv(1024)
        
            if not data:     #If the socket is readable, but no data has been received we consider it to be a server malfunction and shutdown
                print('The server has severed the connection, shutting down')
                shutDownFlag = 1
                break
            else:                          #receiving a message from the server
                data = data.decode()
                msgHeader = data[0:4]
                if msgHeader == 'FILET1':     #check for file transfer
                    #Do file transfer stuff
                    sendFileFunc(data)
                elif msgHeader == 'FILET2':   #check for receiving a file
                    #do file receive stuff
                    receiveFileFunc(data)
                else:                          #regular case of receiving chatroom messages
                    print(data)
    
        else:                                   #anything in 'readable' that is not the socket connection to the server is keyboard input
            data = sys.stdin.readline().strip()
            if data == 'QUIT':                    #check for QUIT
                break
            else:                               #standard case, sending data to the server
                data = data.encode()
                sock.send(data)

    if(data == 'QUIT') or (shutDownFlag == 1):   #check for the shutDownFlag (server malfunction) or QUIT (user terminating connection)
        break


print('This client is ending')
sock.close()
