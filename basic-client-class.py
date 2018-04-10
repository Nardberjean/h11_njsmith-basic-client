import socket
import ssl
import h11

class BasicClient:
    """A simple example class"""
    h11conn = h11.Connection(our_role=h11.CLIENT)

    # def __init__(self, host, port=443):
    #     ctx = ssl.create_default_context()
    #     self.sock = ctx.wrap_socket(
    #         socket.create_connection((host, port)),
    #         server_hostname=host
    #     )
    def __init__(self, socket):
        self.sock = socket

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        print("Closing socket")
        self.sock.close()

    def send(self, event):
        print("Sending event:")
        print(event)
        print()
        # Pass the event through h11's state machine and encoding machinery
        # Send the resulting bytes on the wire
        self.sock.sendall(self.h11conn.send(event))

    def next_event(self):
        while True:
            # Check if an event is already available
            event = self.h11conn.next_event()
            if event is h11.NEED_DATA:
                # Nope, so fetch some data from the socket...
                # ...and give it to h11 to convert back into events...
                self.h11conn.receive_data(self.sock.recv(2048))
                # ...and then loop around to try again.
                continue
            return event

################################################################
# Setup
################################################################

with BasicClient(ssl.create_default_context().wrap_socket(
    socket.create_connection(("httpbin.org", 443)),
    server_hostname="httpbin.org"
    )) as client:

    ################################################################
    # Sending a request
    ################################################################

    client.send(
        h11.Request(
            method="GET",
            target="/get",
            headers=[
                ("Host", "httpbin.org"),
                ("Connection", "close")
            ]
        )
    )
    client.send(h11.EndOfMessage())

    ################################################################
    # Receiving the response
    ################################################################

    while True:
        nevent = client.next_event()
        print("Received event:")
        print(nevent)
        print()
        if isinstance(nevent, h11.EndOfMessage):
            break

################################################################
# Clean up
################################################################

print("The End")

# Copyed and adapted from https://github.com/python-hyper/h11/blob/master/examples/basic-client.py
