import sys
import socket


def generate_headers(code):
    header = ""
    if code == 200:
        header += "HTTP/1.1 200 OK\n"
    elif code == 404:
        header += "HTTP/1.1 404 Not Found\n"
    return header


def mySocket():
    if len(sys.argv) != 2:
        print("Invalid input")
    else:
        port = int(sys.argv[1])

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    serverSocket.bind(("localhost", port))

    serverSocket.listen(1)

    while 1:
        client, address = serverSocket.accept()

        data = client.recv(1024).decode('utf-8')
        if not data:
            break
        request_method = data.split(' ')[0]
        print(f"Method: {request_method}")
        print(f"Request {data}")

        file_request = data.split(" ")[1]
        file_request = "."+file_request

        try:
            f = open(file_request, 'rb')
            if request_method == "GET":
                response_data = f.read()
            f.close()
            response_header = generate_headers(200)
            print("Success")
        except Exception:
            print("404 not found")
            response_header = generate_headers(404)
            response_data = b"<html><body>Error 404: File not found</body></html>"
        response = response_header.encode('utf-8')

        response += response_data
        client.send(response)
        client.close()
        break


if __name__ == "__main__":
    mySocket()
