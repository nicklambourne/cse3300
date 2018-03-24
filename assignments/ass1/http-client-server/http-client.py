#!/usr/bin/env/ python3

from sys import argv, exit
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

CRLF = '\r\n\r\n'

# Check the number of command line arguments
if len(argv) not in [4, 5]:
    print('Client startup failed!\n'
          'Usage: ./http-client <source> <object> [port]')
    exit(1)

# Parse command line arguments
host = argv[1].strip()
obj = argv[2].strip()
obj = obj if obj[0] == '/' else '/' + obj
port = 80  # Default to port 80 (HTTP) if no port is provided.

if len(argv) == 5:
    try: 
        port = int(argv[3])
        if port < 5000:
            print('Client startup failed!\n'
                  'Port must be >5000 to avoid clashes with critical ports')
            exit(2)
    except TypeError:
        print('Client startup failed!\n'
              'Port provided was not an integer!')

sock = socket(AF_INET, SOCK_STREAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Release socket immediately on termination
sock.connect((host, port))

print('GET %s HTTP/1.0%s' % (obj, CRLF))
sock.send(('GET %s HTTP/1.0%s' % (obj, CRLF)).encode('utf-8'))

while True:
    data = sock.recv(1024).decode()
    if data == '':
        break
    print(data, end='')

sock.close()
