import socket
from .event_loop import run_server


def main():
    run_server([socket.AF_INET, socket.SOCK_STREAM], ("localhost", 6379))


if __name__ == "__main__":
    main()
