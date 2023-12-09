from __future__ import print_function
from contextlib import contextmanager
import socket
import select

from app.command_handler import (
    handle_set_command,
    handle_get_command,
    handle_config_command,
    handle_keys_command,
)


@contextmanager
def socketcontext(*args, **kwargs):
    """Context manager for a socket."""
    s = socket.socket(*args, **kwargs)
    try:
        yield s
    finally:
        print("Close socket")
        s.close()


@contextmanager
def epollcontext(*args, **kwargs):
    """Context manager for an epoll loop."""
    e = select.epoll()
    e.register(*args, **kwargs)
    try:
        yield e
    finally:
        print("\nClose epoll loop")
        e.unregister(args[0])
        e.close()


def init_connection(server, connections, requests, responses, epoll):
    """Initialize a connection."""
    connection, _ = server.accept()
    connection.setblocking(0)

    fd = connection.fileno()
    epoll.register(fd, select.EPOLLIN)
    connections[fd] = connection
    requests[fd] = b""
    responses[fd] = b""


def receive_request(fileno, requests, connections, responses, epoll):
    """Receive a request and add a response to send.
    Handle client closing the connection.
    """
    requests[fileno] += connections[fileno].recv(1024)

    if requests[fileno] == "quit\n" or requests[fileno] == "":
        print("[{:02d}] exit or hung up".format(fileno))
        epoll.unregister(fileno)
        connections[fileno].close()
        del connections[fileno], requests[fileno], responses[fileno]
        return

    elif requests[fileno].startswith(b"*") and requests[fileno].endswith(b"\n"):
        epoll.modify(fileno, select.EPOLLOUT)
        msg = requests[fileno]
        print("[{:02d}] says: {}".format(fileno, msg))

        split = msg.split(b"\r\n")
        print(split)

        match split[2].lower():
            case b"ping":
                responses[fileno] = b"+PONG\r\n"

            case b"echo":
                responses[fileno] = b"+" + split[4] + b"\r\n"

            case b"set":
                if len(split) > 8:
                    responses[fileno] = handle_set_command(
                        split[4], split[6], int(split[10])
                    )
                else:
                    responses[fileno] = handle_set_command(split[4], split[6])

            case b"get":
                responses[fileno] = handle_get_command(split[4])

            case b"config":
                responses[fileno] = handle_config_command(split[4], split[6])

            case b"keys":
                responses[fileno] = handle_keys_command()

            case _:
                responses[fileno] = b"+ERR\r\n"

        print(responses)
        requests[fileno] = b""


def send_response(fileno, connections, responses, epoll):
    """Send a response to a client."""
    byteswritten = connections[fileno].send(responses[fileno])
    responses[fileno] = responses[fileno][byteswritten:]
    epoll.modify(fileno, select.EPOLLIN)


def run_server(socket_options, address):
    """Run a simple TCP server using epoll."""
    with socketcontext(*socket_options) as server, epollcontext(
        server.fileno(), select.EPOLLIN
    ) as epoll:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(address)
        server.listen(5)
        server.setblocking(0)
        server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        print("Listening")

        connections = {}
        requests = {}
        responses = {}
        server_fd = server.fileno()

        while True:
            events = epoll.poll(1)

            for fileno, event in events:
                if fileno == server_fd:
                    init_connection(server, connections, requests, responses, epoll)
                elif event & select.EPOLLIN:
                    receive_request(fileno, requests, connections, responses, epoll)
                elif event & select.EPOLLOUT:
                    send_response(fileno, connections, responses, epoll)
