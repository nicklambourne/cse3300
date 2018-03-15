#!/usr/bin/env python3

from sys import argv, exit
from socket import socket, AF_INET, SOCK_STREAM

CRLF = "\r\n\r\n"

# Check the number of command line arguments
if len(argv) not in [4, 5]:
    print("Client startup failed!\n"
          "Usage: ./client <source> <object> [port]")
    exit(1)

# Parse command line arguments
host = argv[1].strip()
obj = argv[2].strip()
port = 80
if len(argv) == 5:
    try: 
        port = int(argv[3])
        if port < 5000:
            print("Client startup failed!\n"
                  "Port must be >5000 to avoid clashes with critical ports")
            exit(2)
    except TypeError:
        print("Client startup failed!\n"
              "Port provided was not an integer!")

print("Host: %s\nObj: %s\nPort:%s" % (host, obj, str(port)))

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, port))

sock.send(("GET / HTTP/1.0%s" % (CRLF)).encode('utf-8'))

data = sock.recv(8192)

sock.close()

print(data)

