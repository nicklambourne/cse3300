#!/usr/bin/env python3

from signal import signal, SIGINT
from socket import gethostbyname, socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from sys import exit
from time import ctime, time, sleep
from _thread import start_new_thread

CRLF = '\r\n\r\n'
PORT = 50007


def graceful_shutdown(signum, frame):
    print('\nReceived interrupt: Shutting down...')
    connections = []
    for connection in connections:
        try:
            connection.close()
        except Exception:
            pass
    exit(101)


def handle_client(connection):
    while True:
        data = connection.recv(1024)
        if len(data) == 0:
            connection.close()
            print("Connection closed.")
            break
        print(data.decode(), end='')
        reply = "HTTP/1.0 200 OK\n"+CRLF+"<html><body>Hello World</body></html>\n"
        print(reply)
        connection.sendall(reply.encode())
        print("response sent")


if __name__ == '__main__':
    signal(SIGINT, graceful_shutdown)
    host = ''  # Equivalent to localhost
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((host, PORT))
    sock.listen(10)  # 10 pending connections allowed
    print('Server started, (listening on {}:{}) waiting for connection...'.format(gethostbyname(''), PORT))
    while True:
        connection, address = sock.accept()
        print('Server connected to {} at {}'.format(address, ctime(time())))
        start_new_thread(handle_client, (connection,))
