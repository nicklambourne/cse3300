"""
Author: Nicholas Lambourne
CSE 3300  - Computer Networks and Data Communication
Professor: Dr Bing Wang
Assignment 1: HTTP Client
"""

from sys import argv, exit
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

DEFAULT_PORT = 80
CRLF = '\r\n'


class BasicHTTPClient(object):
    """
    A custom class defining a basic HTTP client capable of requesting documents from a
    specified host over a specific port, with custom headers provided as command line
    arguments.
    """
    def __init__(self):
        self.host, self.obj, self.port, self.headers = self.parse_arguments()
        self.request = self.construct_request()
        self.sock = self.initiate_connection()

    def parse_arguments(self):
        """
        Takes the command line arguments and provides the information required for the HTTP
        request (host, object, port, and headers).
        :return: a tuple including the host (string), object (string), port (int) and headers
         [(string, string), ...]
        """
        if len(argv) < 3:
            self.print_usage_message('Incorrect number of arguments!')
            exit(1)
        host = argv[1]  # Host to connect to
        obj = argv[2]  # Object to retrieve
        port = DEFAULT_PORT  # Default to DEFAULT port (80: HTTP) if none provided.
        headers = []  # Headers to send
        #
        if len(argv) == 3:
            return host, obj, port, headers
        if ':' in argv[3]:  # Check if second argument is a header
            try:  # Loop through headers, adding to list
                for pair in argv[3:]:
                    header, value = pair.split(':')
                    headers.append((header, value))
            except ValueError:
                self.print_usage_message('Error parsing headers!')
                exit(2)
        else:  # Headers not provided first, so get port.
            try:
                port = int(argv[3])  # Accept any port for client
            except TypeError:
                print('Client startup failed!\n'
                      'Port provided was not an integer!')
                exit(3)
            if len(argv) == 4:  # No headers
                return host, obj, port, headers
            try:
                for pair in argv[4:]:  # Get rest of CLAs
                    header, value = pair.split(':')
                    headers.append((header, value))
            except ValueError:
                self.print_usage_message('Error parsing headers!')
                exit(4)
        return host, obj, port, headers

    def print_usage_message(self, message_header):
        """
        Prints a custom error message to the terminal based on a provided specific message
        and a generic base message with usage instructions.
        :param message_header: a string representing the specific error that caused the problem.
        :return: None
        """
        base_message = 'Client startup failed!\n' \
                       'Usage: python3 http-client.py <source> <object> [port] [headers...]\n' \
                       'N.B: Headers must be provided in the form HeaderName:HeaderValue\n' \
                       '(space separated, but not between Name and Value).'
        print(message_header + '\n' + base_message)

    def construct_request(self):
        """
        Constructs a properly formatted HTTP request based on the object and headers specified
        in the command-line arguments.
        :return: a string representation of the HTTP request.
        """
        request = 'GET %s HTTP/1.0%s' % (self.obj if self.obj[0] == '/' else '/' + self.obj, CRLF)
        for (header, value) in self.headers:  # Add all headers to request
            request += header + ': ' + value + CRLF
        request += CRLF
        return request

    def initiate_connection(self):
        """
        Attempts to connect to the host over the provided port.
        :return: the TCP socket connection object.
        """
        try:
            sock = socket(AF_INET, SOCK_STREAM)  # TCP, IPV4
            sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Release socket immediately on termination
            sock.connect((self.host, self.port))  # Attempt connection
        except Exception:
            self.print_usage_message('Connection failed, are you sure of your host?')
            exit(7)
        return sock

    def make_request(self):
        """
        Given a connected socket, make the HTTP request given by construct_request to the
        socket given by initiate_connection.
        :return:
        """
        self.sock.send(self.request.encode('utf-8'))  # Send request
        while True:  # Loop through until there is no more data, printing as it is received.
            data = self.sock.recv(1024).decode()
            if data == '':
                break
            print(data, end='')
        self.sock.close()  # Clean up/close socket.


if __name__ == "__main__":
    client = BasicHTTPClient()  # Instantiate client.
    client.make_request()  # Make request.





