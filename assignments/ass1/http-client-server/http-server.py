#!/usr/bin/env python3

from os.path import isfile
from signal import signal, SIGINT
from socket import gethostbyname, socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from sys import argv, exit
from time import ctime, time
from _thread import start_new_thread

CRLF = '\r\n'
DEFAULT_PORT = 50007


class BasicHTTPServer(object):
    """
    Custom class defining a basic HTTP server with the ability to serve static files to
    multiple clients concurrently (threaded).
    """
    def __init__(self):
        self.port = self.parse_arguments()
        self.host = '127.0.0.1'  # Equivalent to localhost
        self.connections = []

    def parse_arguments(self):
        """
        Parses the provided command line arguments and returns the port number provided.
        N.B. Will exit the process if the provided port number is not an integer.
        :return:
        """
        if len(argv) == 1:  # No port provided, so use the default port (above).
            return DEFAULT_PORT
        try:  # Port provided, attempt to read.
            port = int(argv[1])
            if not 5000 < port < 65536:  # Check inside allowable port range
                self.print_usage_message('Provided port must be greater than 5000 to avoid conflicts!')
                exit(2)
            return port
        except ValueError:  # If provided port is not parsable.
            self.print_usage_message('Provided port is not an integer!')
            exit(3)

    def print_usage_message(self, message_header):
        """
        Prints a custom error message to the terminal based on a provided specific message
        and a generic base message with usage instructions.
        :param message_header: a string representing the specific error that caused the problem.
        :return: None
        """
        base_message = 'Server startup failed!\n' \
                       'Usage: python3 http-server.py <port>\n'
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
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(10)  # 10 pending connections allowed
        print('Server started, (listening on {}:{}) waiting for connection...'
              .format(gethostbyname(self.host), self.port))
        while True:
            connection, address = sock.accept()
            self.connections.append(connection)
            print('Server connected to {} at {}'.format(address, ctime(time())))
            start_new_thread(self.handle_client, (connection,))

    def is_valid_file(self, path):
        return isfile(path)

    def get_file_contents(self, path):
        contents = ''
        with open('my_file.txt') as file:
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
            if not data: break
            length = len("""<html>
<body>
<h1>Hello, World!</h1>
</body>
</html>""".encode())
            print("Length: " + str(length))
            reply = '''HTTP/1.0 200 OK
Connection: close
Content-Type: text/html
Content-Length: {}

<html>
<body>
<h1>Hello, World!</h1>
</body>
</html>
'''.format(length)
            print(reply)
            connection.sendall(reply.encode())
        connection.close()


if __name__ == '__main__':
    server = BasicHTTPServer()
    signal(SIGINT, server.graceful_shutdown)
    server.run_server()





