#!/usr/bin/python3
import time
import sys
import socket


def main():
    number_of_pings = 15
    time_out = 2
    sleep_time = 1
    min_rtt = 10e9
    max_rtt = 0
    count = 0
    total = 0
    if len(sys.argv) != 3:
        print("Invalid input")
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
        if host == "localhost":
            host = "127.0.0.1"
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientSocket.settimeout(time_out)
        sequence_number = 3331
        for i in range(number_of_pings):
            start = time.time()
            message = b'f"Ping {sequence_number+i} {start} \r\n"'
            try:
                clientSocket.sendto(message, (host, port))
                data, server = clientSocket.recvfrom(1024)
                end = time.time()
                rtt = round((end - start), 3)*1000
                if rtt > 600:

                    print(
                        f"ping to {host}, seq = {sequence_number+i}, rtt = Timeout")
                else:
                    print(
                        f"ping to {host}, seq = {sequence_number+i}, rtt = {rtt}")
                    count += 1
                    total += rtt
                    if rtt > max_rtt:
                        max_rtt = rtt
                    if rtt < min_rtt:
                        min_rtt = rtt
                time.sleep(sleep_time)
            except socket.timeout:
                print(
                    f"ping to {host}, seq = {sequence_number+i}, rtt = Timeout")

    print(
        f"minimum rtt is {min_rtt}, maximum rtt is {max_rtt}, and average rtt is {round(total/count,3)}")


if __name__ == "__main__":
    main()
