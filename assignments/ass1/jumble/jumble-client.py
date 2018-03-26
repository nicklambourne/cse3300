#!/usr/bin/env/ python3

from time import sleep
from signal import signal, SIGINT
from sys import argv, exit
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR


class JumbleClient(object):
    """
    Custom class describing a client for connecting to an instance of JumbleServer and
    playing the game jumble continuously until interrupted.
    """
    def __init__(self):
        self.server_address, self.port = self.parse_arguments()
        self.sock = self.start_connection()  # socket.socket object for communication with server

    def play_game(self):
        """
        Starts a game with an already connected server.
        :return: None
        """
        self.sock.send('START'.encode())
        while True:
            data = self.sock.recv(1024)
            message = data.decode()
            if message == "":
                print("Connection closed.")
                exit(0)
            elif message == "ACCEPTED":
                self.game_loop()
            sleep(1)

    def start_connection(self):
        """
        Initiates the connection to the server described in the command line arguments using sockets.
        :return: A connected socket.socket object.
        """
        print('Connecting to Jumble Server at ', self.server_address, "on port", str(self.port))
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Release socket immediately on termination
        sock.connect((self.server_address, self.port))
        print('Connected!')
        return sock

    def parse_arguments(self):
        """
        Parses the command line arguments and returns the values as a tuple.
        Will cause the process to exit if an invalid number of arguments or port number are provided.
        :return: A tuple representing the server address and a port number for connection.
        """
        # Check the number of command line arguments
        if len(argv) not in [2, 3]:
            print('Client startup failed!\n'
                  'Incorrect number of arguments\n'
                  'Usage: ./http-client <server-address> [port]')
            exit(1)

        server_address = argv[1].strip()
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
        return (server_address, port)

    def game_loop(self):
        """
        Continuously communicates with the server, requesting words and sending guesses.
        Will not exit until forcibly interrupted.
        :return: None
        """
        while True:
            word_enc = self.sock.recv(1024)
            word_dec = word_enc.decode().strip()
            guess = input("Jumble: " + word_dec + "\nGuess: ")
            self.sock.send(guess.encode())
            correct = self.sock.recv(1024)
            if correct.decode() == "YES":
                print("You win.")
            else:
                correct = correct.decode()
                print("The answer is ", correct)

    def graceful_shutdown(self, signum, frame):
        """
        Closes the connection safely before exiting when the program is given a keyboard interrupt.
        :param signum: Not used
        :param frame: Not used
        :return: None
        """
        print('\nReceived interrupt: Shutting down...')
        self.sock.close()
        exit(3)


if __name__ == '__main__':
    client = JumbleClient()
    signal(SIGINT, client.graceful_shutdown)
    client.play_game()

















