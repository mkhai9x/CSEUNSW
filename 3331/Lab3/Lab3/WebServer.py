import sys
import socket


def generate_headers(code):
    header = ""
    if code == 200:
        header += "HTTP/1.1 200 OK\r\n\n"
    elif code == 404:
        header += "HTTP/1.1 404 Not Found\r\n\n"
    return header


def mySocket():
    if len(sys.argv) != 2:
        print("Invalid input")
    else:
        port = int(sys.argv[1])

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    serverSocket.bind(('', port))

    serverSocket.listen(1)

    while 1:
        client, address = serverSocket.accept()

        data = client.recv(1024).decode('utf-8')
        if not data:
            break
        request_method = data.split('\r\n')[0]
        print(f"Method: {request_method}")
        print(f"Request {data}")

        file_request = request_method.split(" ")[1][1:]

        try:
            f = open(file_request, 'rb')

            response_data = f.read()

            response_header = generate_headers(200)
            print("Success")
        except Exception:
            print("404 not found")
            response_header = generate_headers(404)
            response_data = b"<html><body>Error 404: File not found</body></html>"
        response = response_header.encode('utf-8')

        client.send(response)
        client.send(response_data)
        client.close()
        break


if __name__ == "__main__":
    mySocket()
# import sys
# import argparse
# import socket


# def main():
#     port = int(sys.argv[1])
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind(('', port))

#     server_socket.listen(1)

#     while 1:
#         conn, addr = server_socket.accept()

#         try:
#             data = conn.recv(1024).decode('utf-8')
#             request = data.split('\r\n')[0]
#             request_file = request.split(' ')[1][1:]
#             file_content = open(request_file, 'rb')
#             response_header = "HTTP/1.1 200 OK\r\n\n".encode('utf-8')
#             response_body = file_content.read()

#             conn.send(response_header)
#             conn.send(response_body)
#         except IOError:
#             response_header = "HTTP/1.1 404 NOT FOUND\r\n\n".encode('utf-8')
#             response_body = b"<html><body>404 NOtFound</body></html>"
#             conn.send(response_header)
#             conn.send(response_body)
#         conn.close()


# if __name__ == "__main__":
#     main()
