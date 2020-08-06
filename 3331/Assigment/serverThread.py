import socket
import select # the way to manage many connections
import datetime
import sys
import string
from random import choice
import threading
import time
HEADER_LENGTH = 10
SERVER_IP = 'localhost'
SERVER_PORT = 1234
BLOCK_DURATION  = 60
LOGIN_SUCCESSFULL = "Welcome to the BlueTrace Simulator!"
LOGIN_WRONG_PASSWORD =  "Invalid Password. Please try again"
LOGIN_BLOCK = "Invalid Password. Your account has been blocked. Please try again later"
INVALID_USER = "Invalid user"

BLOCK_MESSAGE= "Your account is blocked due to multiple login failures. Please try again later"
INVALID_COMMAND = "Error.Invalidcommand"
LOGOUT = "Logoutsuccessfully"
CONTACT_LOG_CHECKING = "contactISBeingChecked"

TEMPID_DURATION = 15
#Create a server socket
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)


server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

server_socket.bind((SERVER_IP,SERVER_PORT))

server_socket.listen()

# Manage a list of sockets that connecting to the server
sockets_list = [server_socket]

# A dictionary stores  current online clients information socket as a key.
clients = {}

#A database for all clients 
database_clients = {}
# A dicitonary stores blocked clients
blocked_clients = {}

def update_tempID(filename, database_clients):
    """
    This function is used to check every tempID in the tempIDs.txt file
    If a tempID expires, this function will provide that user a new tempID with duration of TEMPID_DURATION minutes
    
    Parameters
    ----------
    filename: str
        the name of the file that contains all the tempIDs information
    database_clients:   
    """
    tempID_file = open(filename,'r')
    lines = tempID_file.readlines()
    new_file_content = ""
    for line in lines:
        try:
            line.strip()
            current_time = datetime.datetime.now()
            infor = line.strip().split()
            user = database_clients[infor[0]]
            start_time = user['tempID']['start_time'] 
            different = (current_time - start_time).total_seconds()/60
            if different > TEMPID_DURATION:
                new_tempID = ''.join(choice(string.digits) for i in range(20))
                user['tempID']['ID'] = new_tempID
                user['tempID']['start_time'] = current_time
                duration = current_time + datetime.timedelta(minutes=TEMPID_DURATION)
                new_start_time = current_time.strftime('%d/%m/%Y %H:%M:%S') 
                new_line = infor[0]+ " " + new_tempID + " " + new_start_time + " " + duration.strftime('%d/%m/%Y %H:%M:%S') + "\n"
                new_file_content += new_line
            else:
                new_file_content = new_file_content + line 
        except:
            continue
    tempID_file.close()
    writing_new_tempID_file = open(filename,'w')
    writing_new_tempID_file.write(new_file_content)
    writing_new_tempID_file.close()

def display_contact_log(contact, isChecking):
    """
    This is the helper function for server.
    This is called when ever a client command Upload_contact_log

    Parameters
    ----------
    contact: str
        The content of the contact file from the client
    isChecking: bool
        A flag used to determine whether the tempID need to replaced by the user real ID
    """
    contact_infor = contact.split('\n')
    map_contact = {}
    if isChecking:
        #If the server is checking the contact,
        #We compute the dictionary to store tempID and realID   
        tempID_file = open("tempIDs.txt",'r')
        lines = tempID_file.readlines()
        for line in lines:
            try:
                infor = line.strip().split()
                realID, tempID = infor[0], infor[1]
                map_contact[tempID] = realID    
            except:
                continue
            
    for each in contact_infor:
        infor = each.split()
        if isChecking:
            print(f"{map_contact[infor[0]]}, {infor[1]} {infor[2]}, {infor[0]};")
        else:
            print(f"{infor[0]}, {infor[1]} {infor[2]}, {infor[3]} {infor[4]};")
            


def update_User_information(pure_user_information, user_name):
    pure_user_information['data'] = user_name
    pure_user_information['header'] = f"{len(pure_user_information['data']):<{HEADER_LENGTH}}"


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())

        return {"header": message_header,"data":client_socket.recv(message_length)}
    except:
        return False


def login_verification(client_name, password):
    database = open("credentials.txt",'r')
    lines = database.readlines()
    for line in lines:
        correct_client_name, correct_password = line.strip().split()
        if(correct_client_name==client_name and password==correct_password):
            return LOGIN_SUCCESSFULL
        elif(correct_client_name==client_name and correct_password!=password):
            return LOGIN_WRONG_PASSWORD
    return INVALID_USER
            
def update_tempID_file(client_name, tempID,start_time):
    tempID_file = open("tempIDs.txt",'a')
    line = client_name+" " + tempID
    duration = start_time + datetime.timedelta(minutes=TEMPID_DURATION)
    string_time = start_time.strftime('%d/%m/%Y %H:%M:%S') 
    line = line + " " + string_time + " " +duration.strftime('%d/%m/%Y %H:%M:%S') + "\n"
    tempID_file.write(line)

def sockets_handler():
    global server_socket
    global clients
    global sockets_list
    global database_clients
    global blocked_clients
    while True:
        # print("runnign while loop")

        
        read_sockets, _, _ = select.select(sockets_list,[],sockets_list)
        #check is there any tempID expires
        #if it expires, we need to change the file and the infor of that user in database_clients

        for notified_socket in read_sockets:

            # print("runnign while loop")

            #someone just connected, and server need to accept the connection 
            if notified_socket == server_socket:

                #A new connection from a client try to login to the server with user name and password
                #bringing that connection 
                client_socket, client_address = server_socket.accept()
                # print("Connection has been established")
                count = 0
                while True:
                    #Read the authentication information (username and password) of client_socket
                    user = receive_message(client_socket)
                    if user is False:
                        break
                    #Extract the username and password
                    # print(user['data'].decode('utf-8'))
                
                    client_name, client_password = user['data'].decode('utf-8').split()
                    #Check if the client_name in the blocked_clients
                    if client_name in blocked_clients.keys():
                        user = blocked_clients[client_name]
                        current_time = datetime.datetime.now()
                        different = (current_time - user['blocked']).total_seconds()
                        if different < BLOCK_DURATION:
                            message = BLOCK_MESSAGE.encode('utf-8')
                            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                            client_socket.send(message_header+message)
                            break
                        else:
                            #Remove the block client
                            del blocked_clients[client_name]
                    output_login = login_verification(client_name,client_password)
                    #Login verification step
                    if output_login == LOGIN_SUCCESSFULL:
                        #adding this client socket into the sockets_list
                        sockets_list.append(client_socket)
                        #If the database_clients does not contain this user
                        #It means the client does not have tempID yet
                        update_User_information(user, client_name)
                        if(client_name not in database_clients.keys()):
                            start_time = datetime.datetime.now()
                            tempID = ''.join(choice(string.digits) for i in range(20))
                            update_tempID_file(client_name,tempID,start_time)
                            user['tempID'] = {"ID": tempID,"start_time":start_time}
                            database_clients[client_name] = user
                        else:
                            user = database_clients[client_name]
                        # add this client into current clinents connecting to this server
                
                        clients[client_socket] = user
                        #print(f"Accepted new connection from {client_address[0]}:{client_address[1]}  username: {user['data'].decode('utf-8')}")
                        #Ater successfully login, the sever send successfull message
                        message = LOGIN_SUCCESSFULL.encode('utf-8')
                        message_header = f"{len(LOGIN_SUCCESSFULL):<{HEADER_LENGTH}}".encode('utf-8')
                        client_socket.send(message_header+message)
                            
                        #Need to check whether this client already has tempID or not
                        break
                    elif output_login == LOGIN_WRONG_PASSWORD:
                        count+=1
                        if  count == 3:
                            update_User_information(user, client_name)
                            user['blocked'] = datetime.datetime.now()
                            message = LOGIN_BLOCK.encode('utf=8')
                            message_header = f"{len(LOGIN_BLOCK):<{HEADER_LENGTH}}".encode('utf-8')
                            # add this client into blocked_clients
                            blocked_clients[client_name] = user
                            client_socket.send(message_header+message)
                    

                        else:
                            message = LOGIN_WRONG_PASSWORD.encode('utf-8')
                            message_header = f"{len(LOGIN_WRONG_PASSWORD):<{HEADER_LENGTH}}".encode('utf-8')
                            client_socket.send(message_header+message)
                        
                    #Invalid username
                    else:
                        message = INVALID_USER.encode('utf-8')
                        message_header = f"{len(INVALID_USER):<{HEADER_LENGTH}}".encode('utf-8')
                        client_socket.send(message_header+message)
                        # client_socket.close()

                    
            #when the notified_socket is not the server_socket
            #it means one of the client sends command to the server
            elif notified_socket in clients.keys():

                message = receive_message(notified_socket)
                #check for wheter message is valid or not
                if message is False:
                    
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue
                user = clients[notified_socket]

                #get command from the client
                command = message['data'].decode('utf-8').strip().split()[0]
                if command == "Download_tempID":
                    tempID = user['tempID']['ID']
                    message = f"TempID: {tempID}"
                    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                    notified_socket.send(message_header+message.encode('utf-8'))
                    #Server print out to the console
                    print(f"> user: {user['data']}")
                    print(f"> TempID: {user['tempID']['ID']}")
                    break

                elif command == "Upload_contact_log":
                #For this command, the client send two packets, first packet is about command, 
                #second packet is about the message (the file's content)
                    file_content = receive_message(notified_socket)
                    if file_content is False:
                        continue
                    else:
                        contact_log = file_content['data'].decode('utf-8').strip()
                        print(f"> received contact log from {user['data']}")
                        display_contact_log(contact_log,False)
                        print("> Contact log checking")
                        display_contact_log(contact_log,True)
                    
                        message = CONTACT_LOG_CHECKING.encode('utf-8')
                        message_header = f"{len(CONTACT_LOG_CHECKING):<{HEADER_LENGTH}}".encode('utf-8')
                        notified_socket.send(message_header+message)
                    break
                elif command == "logout":
                    print("> "+user['data'] + " logout")
                    message = LOGOUT.encode('utf-8')
                    message_header = f"{len(LOGOUT):<{HEADER_LENGTH}}".encode('utf-8')
                    notified_socket.send(message_header+message)
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    break
                else:
                    message = INVALID_COMMAND.encode('utf-8')
                    message_header = f"{len(INVALID_COMMAND):<{HEADER_LENGTH}}".encode('utf-8')
                    notified_socket.send(message_header+message)
                    break


def database_handler():
    """
    This function is used to update all tempIDs that have expired
    This function execuate the update_tempID function every minute    
    """
    global server_socket
    global clients
    global sockets_list
    global database_clients
    while True:
        time.sleep(60)
        if len(database_clients.keys())!=0:
            update_tempID("tempIDs.txt",database_clients)
            


recv_thread=threading.Thread(name="RecvHandler", target=sockets_handler)
recv_thread.daemon=True
recv_thread.start()

send_thread=threading.Thread(name="SendHandler",target=database_handler)
send_thread.daemon=True
send_thread.start()
while True:
    time.sleep(0.1)
