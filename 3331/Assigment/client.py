import socket
import select # the way to manage many connections
import datetime
import sys


HEADER_LENGTH = 10
SERVER_IP = 'localhost'
SERVER_PORT = 1234
BLOCK_DURATION  = 60
LOGIN_SUCCESSFUL = "Welcome to the BlueTrace Simulator!"
LOGIN_WRONG_PASSWORD =  "Invalid Password. Please try again"
LOGIN_BLOCK = "Invalid Password. Your account has been blocked. Please try again later"
INVALID_USER = "Invalid user"


BLOCK_MESSAGE= "Your account is blocked due to multiple login failures. Please try again later"
INVALID_COMMAND = "Error.Invalidcommand"
LOGOUT = "Logoutsuccessfully"

DOWNLOAD = "TempID:"
SUCCESSFUL_LOGIN = False
#Helper functions for client
#This function is used to process message
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())

        return {"header": message_header,"data":client_socket.recv(message_length)}
    except:
        return False 
def request_command(client_socket, command):
    message = command.encode('utf-8')
    message_header =  f"{len(command):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(message_header+message)

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client_socket.connect((SERVER_IP,SERVER_PORT))

client_socket.setblocking(False)


sockets_list = [client_socket]

username = input("Username: ").strip() 
password = input("Password: ").strip() 
length = len(username + " " + password)
login_info = (username + " " + password).encode('utf-8')
login_info_header = f"{length:<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(login_info_header + login_info)
# username = input("Username: ").strip()
# password = input("Password: ").strip() 
# credentials = username + ' ' + password
# print(f'Entered >> username:{username} and pwd: {password}')
# lenght = len(credentials)
# username = username.encode()
# credentials = credentials.encode()
# user_header = f"{lenght:<{HEADER_LENGTH}}".encode()
# client_socket.send(user_header + credentials)


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list,[],sockets_list)
  
    for notified_socket in read_sockets:
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
                command = input().strip()
                request_command(notified_socket,command)
           
            
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
                print(server_message['data'].decode('utf-8'))
                command = input().strip()
                request_command(notified_socket,command)
            elif server_reply == INVALID_COMMAND:
                print("Error. Invalid command")
                command = input().strip()
                request_command(notified_socket,command)