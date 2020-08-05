import socket
import select # the way to manage many connections
import datetime
import sys
import string
from random import choice
print("Serve is running")

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
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)


server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

server_socket.bind((SERVER_IP,SERVER_PORT))

server_socket.listen()

# Manage a list of socket

sockets_list = [server_socket]

# A dictionary stores clients information socket as a key.
clients = {}

#A database for all clients
database_clients = {}
# A dicitonary stores blocked clients
blocked_clients = {}


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
    duration = start_time + datetime.timedelta(minutes=15)
    string_time = start_time.strftime('%d/%m/%y %H:%M:%S') 
    line = line + " " + string_time + " " +duration.strftime('%d/%m/%y %H:%M:%S')+ "\n"
    tempID_file.write(line)

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list,[],sockets_list)

    for notified_socket in read_sockets:
        #someone just connected, and server need to accept the connection 
        if notified_socket == server_socket:

            #A new connection from a client try to login to the server with user name and password
            #bringing that connection 
            client_socket, client_address = server_socket.accept()
            print("Connection has been established")
            count = 0
            while True:
                #Read the authentication information (username and password) of client_socket
                user = receive_message(client_socket)
                if user is False:
                    break
                #Extract the username and password
                print(user['data'].decode('utf-8'))
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
                print(f"user: {user['data']}")
                print(f"TempID: {user['tempID']['ID']}")

            elif command == "Upload_contact_log":
                pass
            elif command == "logout":
                print(user['data'] + " logout")
                message = LOGOUT.encode('utf-8')
                message_header = f"{len(LOGOUT):<{HEADER_LENGTH}}".encode('utf-8')
                notified_socket.send(message_header+message)
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
            else:
                message = INVALID_COMMAND.encode('utf-8')
                message_header = f"{len(INVALID_COMMAND):<{HEADER_LENGTH}}".encode('utf-8')
                notified_socket.send(message_header+message)

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]