#!/usr/bin/env/ python3

from time import sleep
from signal import signal, SIGINT
from sys import argv, exit
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR


def graceful_shutdown(signum, frame):
    print('\nReceived interrupt: Shutting down...')
    sock.close()
    exit(101)


signal(SIGINT, graceful_shutdown)

# Check the number of command line arguments
if len(argv) not in [2, 3]:
    print('Client startup failed!\n'
          'Incorrect number of arguments\n'
          'Usage: ./http-client <server-address> [port]')
    exit(1)

server_addr = argv[1].strip()
port = 80  # Default to port 80 (HTTP) if no port is provided.
try:
    port = int(argv[2])
    if port < 5000:
        print('Client startup failed!\n'
              'Port must be >5000 to avoid clashes with critical ports')
        exit(2)
except TypeError:
    print('Client startup failed!\n'
          'Port provided was not an integer!')

print('Connecting to Jumble Server at ', server_addr, "on port", str(port))

sock = socket(AF_INET, SOCK_STREAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Release socket immediately on termination
sock.connect((server_addr, port))

print('Connected!')

sock.send('START'.encode())


def game_loop(comm_sock):
    while True:
        word_enc = comm_sock.recv(1024)
        word_dec = word_enc.decode().strip()
        guess = input("Jumble: " + word_dec + "\nGuess: ")
        comm_sock.send(guess.encode())
        correct = comm_sock.recv(1024)
        if correct.decode() == "YES":
            print("You win.")
        else:
            correct = correct.decode()
            print("The answer is ", correct)


while True:
    data = sock.recv(1024)
    message = data.decode()
    if message == "":
        print("Connection closed.")
        exit(0)
    elif message == "ACCEPTED":
        game_loop(sock)
    sleep(1)







