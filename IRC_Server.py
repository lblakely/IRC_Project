#!/usr/bin/python
#################################################################################################
#                                                                                               #
# Logan Blakely                                                                                 #
# 6/1/17                                                                                        #
# Internetworking Protocols - IRC Project                                                       #
#                                                                                               #
# IRC Server                                                                                    #
#                                                                                               #
# This progrom implements the server process of an IRC, full specifications can be found in the #
#    accompanying RFC document.                                                                 #
#                                                                                               #
#################################################################################################

from datetime import datetime
import socket
import sys
import select
import Queue

###############################################        Command Functions     #########################

#nickFunc            NNICK
#
#In response to NNICK command, this function assigns a new nickname to a client
def nickFunc():
    if msgContent == 'none':
        message = 'ERR_INVALIDCOMMANDFORMAT'
        message = message.encode()
        message_queues[currentClient].put(message)
        if currentClient not in outputs:
            outputs.append(currentClient)
    elif len(msgContent) > 10:
        message = 'ERR_INVALIDNICK - Nicknames must be less than 10 characters'
        message = message.encode()
        message_queues[currentClient].put(message)
        if currentClient not in outputs:
            outputs.append(currentClient)
    else:
        clients[currentClient] = msgContent
        message = 'Congratulations, your new username is ' + clients[currentClient]
        message = message.encode()
        message_queues[currentClient].put(message)
        if currentClient not in outputs:
            outputs.append(currentClient)
#End of nickFunc
#######################################################################


#commandListFunc                     COMMANDS
# 
#In response to COMMANDS, this functions lists the availabe IRC commands
def commandListFunc():
    message = 'Commands\t\t\t\tUsage Examples\t\t\t\tDescription \n NNICK\t\t\t\tNNICK %John\t\t\t\tCreates a new nickname\nCREATE\t\t\t\tCREATE %OregonFishing\t\t\t\tCreates a new room\nJOIN\t\t\t\tJOIN %OregonFishing\t\t\t\tJoins an existing room\nLEAVE\t\t\t\tLEAVE %OregonFishing\t\t\t\tLeave an existing room\nSEND\t\t\t\tSEND %roomname %message content\t\t\t\tSends a message to a room\nLIST\t\t\t\tLIST\t\t\t\t\tList all available rooms\nWHO\t\t\t\tWHO %OregonFishing\t\t\t\tLists the users in a room\nNICKS\t\t\t\tNICKS\t\t\t\t\tLists all users\nPVTMSG\t\t\t\tPVTMSG %John %Hi John\t\t\t\tSends a private message to a user\nQUIT\t\t\t\tQUIT\t\t\t\t\tQuits the chatroom\n\n'
    message = message.encode()
    message_queues[currentClient].put(message)
    if currentClient not in outputs:
        outputs.append(currentClient)

#End of commandListFunc
#################################################################################################################


###########
#sendFunc                SEND
#
#In response to SEND command, this function sends a message to all clients in the given room
def sendFunc():
    if room not in roomDict:
        message = 'ERR_ROOMNOTEXIST'
        message = message.encode()
        message_queues[currentClient].put(message)
        if currentClient not in outputs:
            outputs.append(currentClient)

    elif clients[currentClient] not in roomDict[room]:
        message = 'ERR_NOTAMEMBER'
        message = message.encode()
        message_queues[currentClient].put(message)
        if currentClient not in outputs:
            outputs.append(currentClient)

        #ADD ERR_NOTAMEMBER
    else:
        for ctr in clients:
            if clients[ctr] in roomDict[room]:
                message = 'In ' + room + ', ' + clients[currentClient] + 'says:  ' + msgContent
                message = message.encode()
                message_queues[ctr].put(message)
                if ctr not in outputs:
                    outputs.append(ctr)

#End of sendFunc()
###################################################################3


#nickLIstFunc               NICKS
#
#In response to NICKS command, this function lists all users in the chatroom (in all rooms)
def nickListFunc():
    message = 'List of Users:  '
    for ctr in clients:
        message = message + clients[ctr] + ', '

    message = message.encode()
    message_queues[currentClient].put(message)
    if currentClient not in outputs:
        outputs.append(currentClient)

#End of nickListFunc
##############################################################33

#createFunc         CREATE
#
#In response to the CREATE command, this function creates a new room and gives an error if the room already exists
def createFunc():
    print('Creating a new room')
    if msgContent in roomDict:
        message = 'ERR_ROOMEXISTS'
        message = message.encode()
        message_queues[currentClient].put(message)
        if currentClient not in outputs:
            outputs.append(currentClient)
    else:
        roomDict[msgContent] = set()
        roomDict[msgContent].add(clients[currentClient])
        roomList.append(msgContent)

#End of createFunc()
###########################################################


#joinFunc         JOIN
#
#In response ot the Join command, this function joins a room and gives an error if the room does not exist
def joinFunc():
    print('attempting to join a room')
    if msgContent not in roomDict:
        message = 'ERR_ROOMNOTEXIST'
        message = message.encode()
        message_queues[currentClient].put(message)
        if currentClient not in outputs:
            outputs.append(currentClient)

    else:
        roomDict[msgContent].add(clients[currentClient])
 
        for ctr in clients:
            if clients[ctr] in roomDict[msgContent]:
                message = clients[currentClient] + ' has joined ' + msgContent
                message = message.encode()
                message_queues[ctr].put(message)
                if ctr not in outputs:
                    outputs.append(ctr)

#End of joinFunc
##############################################################


#listRoomsFunc          LIST
#
#In response to the LIST command, this function lists all rooms in existence. 
def listRoomsFunc():
    message = 'Existing Rooms:  '
    #totalRooms = len(roomList)
    for ctr in range(0, len(roomList)):
        message = message + roomList[ctr] + ' '

    message = message.encode()
    message_queues[currentClient].put(message)
    if currentClient not in outputs:
        outputs.append(currentClient)
#End of listRoomsFunc()
##################################################################

#whoFunc               WHO
#
#In response to the WHO command, this function lists who is in the given room
def whoFunc():
    if msgContent not in roomList:
        message = 'ERR_ROOMNOTEXIST'
        message = message.encode()
        message_queues[currentClient].put(message)
        if currentClient not in outputs:
            outputs.append(currentClient)
    else:
        print(roomDict[msgContent])
        message = ' '
        for ctr in roomDict[msgContent]:
            message = message + ctr + ' / '
        message = message  + ' are in ' + msgContent
        message = message.encode()
        message_queues[currentClient].put(message)
        if currentClient not in outputs:
            outputs.append(currentClient)

#End of whoFunc()
#####################################################################


#leaveFunc                LEAVE
#
#In response to the LEAVE command, this function removes a user from the given room and informs the other members of the room of his departure
def leaveFunc():

    message = clients[currentClient] + ' has left ' + msgContent
    message = message.encode()
    if clients[currentClient] in roomDict[msgContent]:
        for ctr in clients:
            if clients[ctr] in roomDict[msgContent]:
                message_queues[ctr].put(message)
                if ctr not in outputs:
                    outputs.append(ctr)
 
        roomDict[msgContent].remove(clients[currentClient])
    else:
        message = 'ERR_NOTAMEMBER'
        message = message.encode()
        message_queues[currentClient].put(message)
        if currentClient not in outputs:
            outputs.append(currentClient)



#end of leaveFunc
########################################################################

#pvtMsgFunc                   PVTMSG
#
#In response ot PVTMSG, this function sends a private message to the given user
def pvtMsgFunc():

    foundFlag = 0
    for ctr in clients:
        if clients[ctr] == room:
            message ='Private Message - ' + clients[currentClient] + ' says: ' + msgContent
            message = message.encode()
            message_queues[ctr].put(message)
            if currentClient not in outputs:
                outputs.append(ctr)
            foundFlag = 1
            break

    if foundFlag == 0:
        message = 'ERR_NICKNOTEXIST'
        message = message.encode()
        message_queues[currentClient].put(message)
        if currentClient not in outputs:
            outputs.append(currentClient)


#end of pvtMsgFunc
############################################################################################################


################################################    Interior Server Functions       ###################################

#clientLeaving
#
#This function takes the client out of the chat room and informs users in that client's rooms of his departure
def clientLeaving():
    print('inside clientLeaving')
    
    for rooms in roomDict:
        message = clients[currentClient] + ' has left ' + rooms
        message = message.encode()
        if clients[currentClient] in roomDict[rooms]:
            roomDict[rooms].remove(clients[currentClient])
            for ctr in clients:
                if clients[ctr] in roomDict[rooms]:
                    message_queues[ctr].put(message)
                    if ctr not in outputs:
                        outputs.append(ctr)

    del clients[currentClient]
            
#end of clientLeaving
#########################################################################################################################
#getAction
#
#this fucntion determines which command was given and replies with an error if the command is not found
def getAction(command):
    if (command != 'NNICK') and (clients[currentClient] == 'none'):
        errMsg = 'You must create a user name before doing anything else.\n'
        errMsg = errMsg.encode()
        message_queues[currentClient].put(errMsg)
        if currentClient not in outputs:
            outputs.append(currentClient)
        func = 0;
        return func

    else:
        if command in commandDict:
            func = commandDict[command]
        else:
            func = 0

    return func

#End of getAction
###########################################################################################################################3




commandDict = {'NNICK':nickFunc,'SEND': sendFunc, 'NICKS': nickListFunc, 'CREATE': createFunc, 'JOIN': joinFunc, 'LIST': listRoomsFunc, 'WHO': whoFunc, 'LEAVE': leaveFunc, 'COMMANDS': commandListFunc,'PVTMSG':pvtMsgFunc}
roomDict = {}
roomList = []

max_size = 1000
print('Starting the server at', datetime.now())
print('Waiting for a client to call')

#Create TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)

#Bind the socket to the port
server_address = ('localhost', 6000)
print('starting up on {} port{}' .format(*server_address))
server.bind(server_address)

#Listen for incoming connections
server.listen(5)

#sockets from which we expect to read
inputs = [server]

#sockets to which we expect to write
outputs = []

# outgoing message Queues (socket:queue)
message_queues = {}

#Client list
clients = {}

#
welcomeMsg = 'Welcome to THE GREATEST IRC\n Please set a username\n'
welcomeMsg = welcomeMsg.encode()


#Server loops forever waiting for new connections
while inputs:

    # wait for at least on of the sockets to be ready for processing
    print('\nwaiting for the next event')
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    for currentClient in readable:

        if currentClient is server:
            # A "readable" server socket is ready to accept a connection
            connection, client_address = currentClient.accept()
            print('new connection from', client_address)
            connection.setblocking(0)
            inputs.append(connection)
            clients[connection] = 'none'

            #give the connection a queue for data we want to send
            message_queues[connection] = Queue.Queue()
            connection.send(welcomeMsg)
        else:
            data = currentClient.recv(1024)
            if data:
                # a readable client socket has data
                print('received {!r} from {}' .format(data, currentClient.getpeername()))
               
                #Parse the data into command and parameters
                fullMsg = data
                if (data.find('%') == -1):        #Command only
                    command = data
                    msgContent = 'none'
                else:
                    fullMsg = data.split('%')

                    if len(fullMsg) == 2      : #Comand + 1 parameters
                        command = fullMsg[0]
                        command = command.strip()
                        msgContent = fullMsg[1]
                    else:                       #Command + 2 parameters
                        command = fullMsg[0]
                        command = command.strip()
                        room = fullMsg[1]
                        room = room.strip()
                        msgContent = fullMsg[2]

                command = command.strip()

                actionFunc = getAction(command)
                if actionFunc == 0:
                    errMsg = 'ERR_COMMANDNOTFOUND'
                    errMsg = errMsg.encode()
                    message_queues[currentClient].put(errMsg)
                    if currentClient not in outputs:
                        outputs.append(currentClient)
                else:
                    actionFunc()

            else:
                #interpret empty result as closed connection
                print('closing', client_address)
                clientLeaving()
                #stop listening for input on the connection
                if currentClient in outputs:
                    outputs.remove(currentClient)
                inputs.remove(currentClient)
                currentClient.close()

                #remove message queue
                del message_queues[currentClient]

    #handle outputs
    for currentClient in writable:
        try: next_msg = message_queues[currentClient].get_nowait()
        except Queue.Empty:
            #no message waiting to be sent to this client, so remove them from the 'outputs' list
            print(' ', currentClient.getpeername(), 'queue empty')
            outputs.remove(currentClient)

        #Send the next message in the current client's message queue
        else:
            print('sending {!r} to {}' .format(next_msg, currentClient.getpeername()))
            currentClient.send(next_msg)    

    for currentClient in exceptional:
        print('handling exceptional condition for', currentClient.getpeername())
        # stop listening for input on the connection
        inputs.remove(currentClient)
        if currentCient in outputs:
            outputs.remove(currentClient)
        currentClient.close()

        #Remove message queue
        del message_queues[currentClient]


