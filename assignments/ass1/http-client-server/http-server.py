"""
Author: Nicholas Lambourne
CSE 3300  - Computer Networks and Data Communication
Professor: Dr Bing Wang
Assignment 1: HTTP Server
"""

from os.path import isdir, isfile
from os import chdir
from signal import signal, SIGINT
from socket import gethostbyname, socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from sys import argv, exit
from time import ctime, time
from _thread import start_new_thread

CRLF = '\r\n'
DEFAULT_PORT = 50007
DEFAULT_FILE = 'index.html'
NOT_FOUND_FILE = 'not_found.html'
HTML_HEADER_FORMAT = '''HTTP/1.0 {}
Connection: close
Content-Type: text/html
Content-Length: {}

'''


class BasicHTTPServer(object):
    """
    Custom class defining a basic HTTP server with the ability to serve static files to
    multiple clients concurrently (threaded).
    """

    def __init__(self):
        self.port, self.root_directory = self.parse_arguments()
        chdir(self.root_directory)  # Change into given root directory.
        print("Changed cwd to:" + self.root_directory)
        self.host = '127.0.0.1'  # Equivalent to localhost.
        self.connections = []  # For keeping tract of connected clients.

    def parse_arguments(self):
        """
        Parses the provided command line arguments and returns the port number provided.
        N.B. Will exit the process if the provided port number is not an integer.
        :return:
        """
        port = DEFAULT_PORT
        if len(argv) != 3:
            self.print_usage_message('Incorrect number of arguments!')
            exit(5)
        try:  # Port provided, attempt to read.
            port = int(argv[1])
            if not 5000 < port < 65536:  # Check inside allowable port range.
                self.print_usage_message('Provided port must be greater than 5000 to avoid conflicts!')
                exit(2)
        except ValueError:  # If provided port is not parsable.
            self.print_usage_message('Provided port is not an integer!')
            exit(3)
        root_directory = argv[2]
        if not isdir(root_directory):  # If directory is invalid, exit.
            self.print_usage_message('Provided root directory is invalid!')
            exit(6)
        return port, root_directory

    def print_usage_message(self, message_header):
        """
        Prints a custom error message to the terminal based on a provided specific message
        and a generic base message with usage instructions.
        :param message_header: a string representing the specific error that caused the problem.
        :return: None
        """
        base_message = 'Server startup failed!\n' \
                       'Usage: python3 http-server.py <port> <root_directory>\n'
        print(message_header + '\n' + base_message)

    def graceful_shutdown(self, signum, frame):
        """
        Shuts down the server on KeyboardInterrupt, closing any open sockets.
        :param signum: not used
        :param frame: not used
        :return: None
        """
        print('\nReceived interrupt: Shutting down...')
        for connection in self.connections:  # Try to shut down any active connections
            try:
                connection.shutdown()
            except Exception:  # Skip any that are already closed.
                pass
        exit(1)

    def run_server(self):
        """
        Starts the server listening and continuously serves clients until deliberately
        interrupted by user.
        :return: None
        """
        sock = socket(AF_INET, SOCK_STREAM)  # TCP, IPV4
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Free port immediately on exit
        sock.bind((self.host, self.port))
        sock.listen(10)  # 10 pending connections allowed
        print('Server started, (listening on {}:{}) waiting for connection...'
              .format(gethostbyname(self.host), self.port))
        while True:
            connection, address = sock.accept()
            self.connections.append(connection)
            print('Server connected to {} at {}'.format(address, ctime(time())))
            start_new_thread(self.handle_client, (connection,))  # Start thread for each client.

    def is_valid_file(self, path):
        """
        Tests if a file exists in the server file system, relative to the working directory.
        Makes an exception for '/' which is interpreted as a request for index.html, which
        is assumed to exist.
        :param path: a string representation of a (potential) file path.
        :return: a boolean indicator of whether the provided file path is valid/exists.
        """
        if path[0] != '/':  # Must lead with slash.
            return False
        if path == '/':  # Slash is an accepted corner case (translated to index.html).
            return True
        else:
            try:
                return isfile(path[1:])  # Check file, without leading slash.
            except IsADirectoryError:  # Do not accept directories
                return False

    def get_file_contents(self, path):
        """
        Takes a file path and returns the contents of that file as a string.
        :param path: the file path, represented as a string
        :return: A string representation of the contents of the requested file.
        """
        if path == '/':  # Accept
            path = DEFAULT_FILE
        else:
            if not self.is_valid_file(path):  # If file not found, choose 404 file.
                path = NOT_FOUND_FILE
            else:
                path = path[1:]  # Strip leading slash.
        contents = ''
        with open(path) as file:
            contents += file.read()
        return contents

    def handle_client(self, connection):
        """
        This method is called when a new thread is spawned by run_server and provides
        a HTTP response to the user with the requested file.
        :param connection:
        :return: None
        """
        while True:  # read, write a client socket
            data = connection.recv(1024)
            if not data:
                break
            request = data.decode().split('\n')[0]  # Get first line of request.
            file_path = request.split(' ')[1]  # Get requested file path.
            body = self.get_file_contents(file_path)
            body_length = len(body.encode())  # Get length for content length header.
            reply = HTML_HEADER_FORMAT.format("200 OK" if self.is_valid_file(file_path)
                                              else "404 Not Found", body_length) + body
            connection.sendall(reply.encode())  # Send until no more data.
        connection.close()


if __name__ == '__main__':
    server = BasicHTTPServer()  # Instantiate server.
    signal(SIGINT, server.graceful_shutdown)  # Set up KeyboardInterrupt handling.
    server.run_server()  # Run server until interrupt.
