"""
Zid: z5168080
Used the sample code as reference from 
https://www.youtube.com/watch?v=ytu2yV3Gn1I

Usage: 
python3 client.py <server_IP> <server_port> <client_udp_port>
"""
import socket
import select # the way to manage many connections
import datetime
import sys
import threading
import time

HEADER_LENGTH = 10
SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
UDP_PORT = int(sys.argv[3])
LOGIN_SUCCESSFUL = "Welcome to the BlueTrace Simulator!"
LOGIN_WRONG_PASSWORD =  "Invalid Password. Please try again"
LOGIN_BLOCK = "Invalid Password. Your account has been blocked. Please try again later"
INVALID_USER = "Invalid user"


BLOCK_MESSAGE= "Your account is blocked due to multiple login failures. Please try again later"
INVALID_COMMAND = "Error.Invalidcommand"
LOGOUT = "Logoutsuccessfully"

CONTACT_LOG_CHECKING = "contactISBeingChecked"
DOWNLOAD = "TempID:"
SUCCESSFUL_LOGIN = False

LOG_DURATION = 3
TEMPID_DURATION = 15
LOG_FILE = "z5168080_contactlog.txt"
#The tempID of the most recent call Download_tempID
CURRENT_TEMPID = "-1"
SPACE_ENTER = "spaceEnter"

  

#------------Implement socket for client-server TCP protocol-----------##
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client_socket.connect((SERVER_IP,SERVER_PORT))

client_socket.setblocking(False)


client_tempIDs = {}
log_table = {}
#----------------------------------------------------------------------##


#-------------Implement socket for p2p UDP protocol--------------------##

udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
udp_sender_socket =  socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

udp_socket.bind((SERVER_IP,UDP_PORT))


#----------------------------------------------------------------------##

sockets_list = [client_socket,udp_socket]
#------------------LOGIN WHEN WE RUN THE the file client.py------------## 
username = input("Username: ").strip() 
password = input("Password: ").strip() 
length = len(username + " " + password)
login_info = (username + " " + password).encode('utf-8')
login_info_header = f"{length:<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(login_info_header + login_info)
#----------------------------------------------------------------------##


#Helper functions for client
def send_file(filename,client_socket):
    """
    This function is used for uploading the log file purposes
    It will extract all the contents of the log file and send the message to the server
    Parameters:
    -----------
    filename: str
        The name of the log file
    client_socket: socket
        The client socket is used to send the message to the server
    """
    message = ''
    file_object = open(filename,'r')
    lines = file_object.readlines()
    for line in lines:
        #Diplays the log to the console in the client's terminal
        infor = line.split()
        print(f"{infor[0]}, {infor[1]}, {infor[2]}, {infor[3]}, {infor[4]};")
        message+=line
    message_length = len(message)
    message = message.encode('utf-8')
    message_header = f"{message_length:<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(message_header+message)

#This function is used to process message
def receive_message(client_socket):
    """
    This function is used to the analyse the message from server to this client
    Using buffering method
    The packet normally includes two parts:
        - Header: the length of the message
        - Date: the data of the message
    """
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())

        return {"header": message_header,"data":client_socket.recv(message_length)}
    except:
        return False 

def request_command(command):
    """
    This function is used to send command to server or other clients
    Depend what kind of the command, this function will use appropriate socket (udp_sender_socket or client_socket)
    Parameter:
    ----------
    command: str
        The client's command
    """
    global client_tempIDs
    global udp_sender_socket
    global client_socket
    if("Beacon" in command):
        #Start sending messge to other client using beacon command
        command_list = command.split()
        other_client_IP = command_list[1]
        other_client_port = int(command_list[2])
        beacon_tempID = CURRENT_TEMPID.encode('utf-8')
        beacon_start_time = client_tempIDs[CURRENT_TEMPID].strftime('%d/%m/%Y %H:%M:%S').encode('utf-8')
        beacon_end_time  = (client_tempIDs[CURRENT_TEMPID] + datetime.timedelta(minutes=TEMPID_DURATION)).strftime('%d/%m/%Y %H:%M:%S').encode('utf-8')
        beacon_BlueTrace_version = "1".encode('utf-8')
        message = beacon_tempID +beacon_start_time + beacon_end_time + beacon_BlueTrace_version
        udp_sender_socket.sendto(message,(other_client_IP,other_client_port))
        print(f"{beacon_tempID.decode('utf-8')}, {beacon_start_time.decode('utf-8')}, {beacon_end_time.decode('utf-8')}.")
        command = input("> ").strip()
        request_command(command)

    else:
        command = command.encode('utf-8')
        command_header =  f"{len(command):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(command_header+command)
        #Check if the command is Upload_contact_log, we need to send the information of the file
        if(command.decode('utf-8') == "Upload_contact_log"):
            send_file("z5168080_contactlog.txt",client_socket)

def adding_log_file(filename, tempID, startTime, expiryTime):
    """
    This function is used to add a log to the log file whenever the beacon is valid from another client
    Parameters:
    -----------
    filename: str
        The name of the log file
    tempID: str
        The temporary ID of the client who send the valid beacon
    startTime: datetime
        The start time of the temporary ID
    expiryTime: datetime
        The expiry time of the temporary ID
    """
    log_file = open(filename,'a')
    line = ""
    startTime = startTime.strftime('%d/%m/%Y %H:%M:%S') 
    expiryTime = expiryTime.strftime('%d/%m/%Y %H:%M:%S') 
    line = tempID +" "+  startTime + " " +expiryTime +"\n"
    log_file.write(line)

def update_log_file(filename):
    """
    This function is used to check is there any log is over 3 minutes since its starting time
    If it is over 3 minutes we delete that log out of the log file
    Parameters:
    -----------
    filename: str
        The name of the log file in form of <zID>_contactlog.txt
    """
    try:
        log_file = open(filename,'r')
        new_cotent = ""
        lines = log_fil.readlines()
        for line in lines:
            try:
                line.strip()
                current_time = datetime.datetime.now()
                infor = line.split()
                old_start_time = ' '.join(infor[1:3])
                old_start_time = datetime.datetime.strptime(old_start_time,'%d/%m/%Y %H:%M:%S')
                duration = (current_time - old_start_time).total_seconds()/60
                if duration < LOG_DURATION:
                    new_cotent += line
                

            except:
                continue
        log_file.close()
        writing_new_log_file = open(filename,'w')
        writing_new_log_file.write(new_cotent)
        writing_new_log_file.close()
    except:
        pass

def send_handler():
    """
    This function is mainly used for this client communication with the server
    The client can command all the available commands.
    """
    global client_socket
    global client_tempIDs
    global log_table
    global sockets_list
    global udp_socket
    global udp_sender_socket
    global SUCCESSFUL_LOGIN
    global CURRENT_TEMPID
    while True:
    
        read_sockets, _,_= select.select(sockets_list,[],sockets_list)
    
        for notified_socket in read_sockets:
            #---------------Receive message from server ------------------##
            #when notified_socket is client_socket
            #it means this client receive a message from server
            if notified_socket == client_socket and not SUCCESSFUL_LOGIN:
                server_message = receive_message(notified_socket)
                if server_message is False:
                    continue
                
                server_reply = server_message['data'].decode('utf-8')
                if server_reply == LOGIN_WRONG_PASSWORD:
                    print(server_reply)
                    password = input("Password: ").strip() 
                    length = len(username + " " + password)
                    login_info = (username + " " + password).encode('utf-8')
                    login_info_header = f"{length:<{HEADER_LENGTH}}".encode('utf-8')
                    client_socket.send(login_info_header + login_info)
                elif server_reply == LOGIN_BLOCK or server_reply == INVALID_USER or server_reply == BLOCK_MESSAGE:
                    print(server_reply)
                    #close the termial for this client
                    client_socket.shutdown(socket.SHUT_RDWR)
                    client_socket.close()
                    sys.exit()
                elif server_reply == LOGIN_SUCCESSFUL:
                    print(LOGIN_SUCCESSFUL)
                    SUCCESSFUL_LOGIN = True
                    command = input("> ").strip()
                    request_command(command)
            
                
            elif notified_socket == client_socket and SUCCESSFUL_LOGIN:
                server_message = receive_message(notified_socket)
                if server_message is False:
                    continue
                server_reply = server_message['data'].decode('utf-8').split()[0]
                if server_reply == LOGOUT:
                    SUCCESSFUL_LOGIN = False
                    client_socket.shutdown(socket.SHUT_RDWR)
                    client_socket.close()
                    sockets_list.remove(client_socket)
                    sys.exit(1)
                elif server_reply == DOWNLOAD:
                    server_message_list = server_message['data'].decode('utf-8').split()
                    start_time = ' '.join(server_message_list[2:])
                    start_time = datetime.datetime.strptime(start_time,'%d/%m/%Y %H:%M:%S')
                    CURRENT_TEMPID = server_message_list[1]
                    client_tempIDs[CURRENT_TEMPID] = start_time
                    print(' '.join(server_message_list[:2]))
                    command = input("> ").strip()
                    request_command(command)
                elif server_reply == INVALID_COMMAND:
                    print("Error. Invalid command")
                    command = input("> ").strip()
                    request_command(command)
                elif server_reply == CONTACT_LOG_CHECKING or server_reply == SPACE_ENTER:
                    command = input("> ").strip()
                    request_command(command)
                
            #-----------------------------------------------------------------##

          
def recv_handler():
    """
    This function is used to read message from beacon of other clients
    If the beacon is valid, this function will add this beacon in to the log file
    Else this funciton do nothing
    """
    global client_socket
    global client_tempIDs
    global log_table
    global sockets_list
    global udp_socket
    global udp_sender_socket
    while True:
        beacon, clientAddress = udp_socket.recvfrom(2048)
        beacon= beacon.decode().strip()
   
        beacon_tempID = beacon[:20]
    
        beacon_startTime = beacon[20:20+19]
        start_time = datetime.datetime.strptime(beacon_startTime,'%d/%m/%Y %H:%M:%S')

        beacon_expiryTime = beacon[20+19:20+19+19]
        expiry_time = datetime.datetime.strptime(beacon_expiryTime,'%d/%m/%Y %H:%M:%S')

        current_time = datetime.datetime.now()

        beacon_BlueTrace_version = beacon[-1]

        print(f"received beacone: \n{beacon_tempID}, {beacon_startTime}, {beacon_expiryTime}.")
        print(f"Current time is: \n{current_time.strftime('%d/%m/%Y %H:%M:%S')}.")
        if current_time > expiry_time or current_time < start_time:
            print("The beacon is invalid.")
        else:
            adding_log_file(LOG_FILE, beacon_tempID,start_time,expiry_time)
            print("The beacon is valid.")


def log_file_handler():
    """
    This function is used to call update_log_file function with the updating purpose
    """
    while True:
        time.sleep(10)
        update_log_file(LOG_FILE)

#------------------Creating three threads--------------------------##
recv_thread=threading.Thread(name="RecvHandler", target=recv_handler)
recv_thread.daemon=True
recv_thread.start()

send_thread=threading.Thread(name="SendHandler",target=send_handler)
send_thread.daemon=True
send_thread.start()

log_file_thread = threading.Thread(name="LogFILEHandler", target=log_file_handler)
log_file_thread.daemon=True
log_file_thread.start()
#this is the main thread
while True:
    time.sleep(0.1)
    if(not send_thread.is_alive()):
        sys.exit()