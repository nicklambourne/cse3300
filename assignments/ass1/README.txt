Program Version: 0.1.0

HTTP CLIENT
Usage: python3 http-client.py <source> <object> [port] [headers...]
N.B: Headers must be provided in the form HeaderName:HeaderValue
e.g. python3 http-client.py gaia.umass.edu /index.html 80 Connection:Close

HTTP SERVER
Usage: python3 http-server.py <port> <root_directory>
N.B: root_directory must be provided as an absolute path.
e.g. python3 http-server.py 80 /usr/nickl93/home/

JUMBLE CLIENT
Usage: python3 jumble-client.py <server-address> [port]
N.B: port is optional, default is 80.
e.g. python3 jumble-client.py 0.0.0.0 50007

JUMBLE SERVER
Usage: python jumble-server.py [port]
N.B. port is optional, default is 50007
e.g. python3 jumble-server.py 50007
