import socket
import ssl
import h11

################################################################
# Setup
################################################################

h11conn = h11.Connection(our_role=h11.CLIENT)
ctx = ssl.create_default_context()
sock = ctx.wrap_socket(socket.create_connection(("httpbin.org", 443)),
                       server_hostname="httpbin.org")

################################################################
# Sending a request
################################################################

def send(event):
    print("Sending event:")
    print(event)
    print()
    # Pass the event through h11's state machine and encoding machinery
    # Send the resulting bytes on the wire
    sock.sendall(h11conn.send(event))


send(h11.Request(method="GET",
                 target="/get",
                 headers=[("Host", "httpbin.org"),
                          ("Connection", "close")]))
send(h11.EndOfMessage())

################################################################
# Receiving the response
################################################################

def next_event():
    while True:
        # Check if an event is already available
        event = h11conn.next_event()
        if event is h11.NEED_DATA:
            # Nope, so fetch some data from the socket...
            # ...and give it to h11 to convert back into events...
            h11conn.receive_data(sock.recv(2048))
            # ...and then loop around to try again.
            continue
        return event


while True:
    event = next_event()
    print("Received event:")
    print(event)
    print()
    if isinstance(event, h11.EndOfMessage):
        break

################################################################
# Clean up
################################################################

sock.close()

# Copyed and adapted from https://github.com/python-hyper/h11/blob/master/examples/basic-client.py
