import os
import socket
import argparse
from app.event_loop import EventLoop
import app.persistence as persistence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir")
    parser.add_argument("--dbfilename")
    args = parser.parse_args()

    persistence_enabled = False

    if args.dir and args.dbfilename:
        persistence.dir = args.dir
        persistence.dbfilename = args.dbfilename
        persistence_enabled = True

    event_loop = EventLoop(persistence_enabled)
    event_loop.run_server([socket.AF_INET, socket.SOCK_STREAM], ("localhost", 6379))


if __name__ == "__main__":
    main()
