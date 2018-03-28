"""
Author: Nicholas Lambourne
CSE 3300  - Computer Networks and Data Communication
Professor: Dr Bing Wang
Assignment 1: Jumble Server
"""

from signal import signal, SIGINT
from random import randrange, shuffle
from socket import gethostbyname, socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from sys import argv, exit
from time import ctime, time
from _thread import start_new_thread

DEFAULT_PORT = 50007
WORD_LIST_FILE = 'wordlist.txt'


class JumbleServer(object):
    """
    Custom class describing a server for hosting concurrent games of jumble with instances
    of the JumbleClient.
    """
    def __init__(self):
        self.words = self.get_word_list()  # Populate list of words
        self.port = self.parse_arguments()  # Port to host on (from command line or default)
        self.host = ''  # Equivalent to localhost / 0.0.0.0
        self.connections = []  # For storing connection objects (in case of interrupt)

    def start_server(self):
        """
        Starts the server running, allowing for concurrent connections.
        N.B. Will run until explicitly interrupted.
        :return: None
        """
        sock = socket(AF_INET, SOCK_STREAM)  # TCP, IPV4
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Release socket immediately on program exit
        sock.bind((self.host, self.port))
        sock.listen(10)  # 10 pending connections allowed
        print('Server started, (listening on {}:{}) waiting for connection...'.\
              format(gethostbyname(''), self.port))
        while True:
            connection, address = sock.accept()
            self.connections.append(connection)
            print('Server connected to {} at {}'.format(address, ctime(time())))
            start_new_thread(self.handle_client, (connection,))

    def parse_arguments(self):
        """
        Parses the command line arguments passed to the program on initiation, reporting
        incorrect usage.
        N.B. Will exit if an incorrect number of arguments or an invalid port is provided.
        :return: a single integer representing the port number to be used.
        """
        # Check the number of command line arguments
        if len(argv) not in [1, 2]:  # Can accept 0 or 1 arguments.
            print('Client startup failed!\n'
                  'Incorrect number of arguments\n'
                  'Usage: python jumble-server.py [port]')
            exit(1)
        port = DEFAULT_PORT  # Default to port 80 (HTTP) if no port is provided.
        if len(argv) == 2:  # Port has been given, try to parse.
            try:
                port = int(argv[2])
                if port < 5000 or port > 65535:  # Check port is in acceptable range.
                    print('Client startup failed!\n'
                          'Port must be >5000 to avoid clashes with critical ports')
                    exit(2)
            except TypeError:
                print('Client startup failed!\n'
                      'Port provided was not an integer!')
        return port

    def get_word_list(self):
        """
        Provides the list of words from the given WORD_LIST_FILE as an array.
        :return: [string, ...] list of strings of words
        """
        file = open(WORD_LIST_FILE)
        words = file.readlines()  # Read entire contents to memory (may be slow).
        file.close()
        return words

    def jumble_word(self, word):
        """
        Takes a word and provides a jumbled version, space-separated.
        :param word: a string representing a word.
        :return: a string representing a jumbled word, each letter is separated by a space.
        """
        letters = list(word)  # Split into list
        shuffle(letters)  # Randomise
        jumble = ''
        for letter in letters:  # Turn back into string
            jumble += letter + ' '
        return jumble

    def get_word(self, word_list):
        """
        Returns a word from the word list that has length greater than 0 and less than 5.
        :param word_list: [string, ...] list of strings of words to choose from.
        :return: a single word (string) from the provided list.
        """
        word = word_list[randrange(len(self.words))]
        while len(word) > 5 or len(word) == 0:
            word = word_list[randrange(0, len(self.words))]
        return word.strip()

    def graceful_shutdown(self, signum, frame):
        """
        Shuts down all extant connections before exiting the server parent process.
        :param signum: not used
        :param frame: not used
        :return: None
        """
        print('\nReceived interrupt: Shutting down...')
        for connection in self.connections:  # Attempt to close down connections
            try:
                connection.close()
            except Exception:  # Handle connection is already closed (skip).
                pass
        exit(1)

    def handle_client(self, connection):
        """
        This method is provided as the core functionality of each thread created to handle
        a client. It confirms a connection and then runs the game loop until explicitly
        interrupted.
        :param connection: the socket connection to the client.
        :return: None
        """
        while True:  # Loop through received data until there is none left to parse.
            data = connection.recv(1024).decode()
            if data == '':
                connection.close()
                print('Connection closed.')
                break
            reply = 'ACCEPTED'
            connection.send(reply.encode())  # Send confirmation of receipt.
            self.game_loop(connection)

    def game_loop(self, connection):
        """
        Provides words and confirmation/correct answers to a client indefinitely until
        interrupted.
        :param connection: the socket connection to the client.
        :return: None
        """
        while True:
            try:
                word = self.get_word(self.words)  # Get word
                jumble = self.jumble_word(word)  # Jumble word
                connection.send(jumble.encode())  # Send word
                guess = connection.recv(1024).decode()  # Receive guess
                if guess == word:
                    connection.send('YES'.encode())  # Send confirmation
                else:
                    connection.send(word.encode())  # Send rejection (correct spelling)
            except BrokenPipeError:
                print("Client connection lost, shutting down thread...")  # Handle client loss
                break


if __name__ == '__main__':
    server = JumbleServer()  # Instantiate server
    signal(SIGINT, server.graceful_shutdown)  # Set up handler for Keyboard interrupt
    server.start_server()  # Start server loop
