#!/usr/bin/env python3

from signal import signal, SIGINT
from random import randrange, shuffle
from socket import gethostbyname, socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from sys import exit
from time import ctime, time
from _thread import start_new_thread

CRLF = '\r\n\r\n'
PORT = 50007

F = open('wordlist.txt')
words = F.readlines()
F.close()


def graceful_shutdown(signum, frame):
    print('\nReceived interrupt: Shutting down...')
    connections = []
    for connection in connections:
        try:
            connection.close()
        except Exception:
            pass
    exit(1)


def jumble_word(word):
    letters = list(word)
    shuffle(letters)
    jumble = ''
    for letter in letters:
        jumble += letter + ' '
    return jumble


def get_word(word_list):
    word = word_list[randrange(len(words))]
    while len(word) > 5 or len(word) == 0:
        word = word_list[randrange(0, len(words))]
    return word.strip()


def handle_client(conn):
    while True:
        data = conn.recv(1024).decode()
        print(data)
        if data == '':
            conn.close()
            print('Connection closed.')
            break
        reply = 'ACCEPTED'
        conn.send(reply.encode())
        print('response sent')
        while True:
            word = get_word(words)
            jumble = jumble_word(word)
            conn.send(jumble.encode())
            print('jumble sent')
            guess = conn.recv(1024).decode()
            print('Guess: ', guess)
            if guess == word:
                conn.send('YES'.encode())
            else:
                conn.send(word.encode())
        

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
