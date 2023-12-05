import os
import socket
import argparse
from app.event_loop import run_server
import app.persistence as persistence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir")
    parser.add_argument("--dbfilename")
    args = parser.parse_args()
    if args.dir and args.dbfilename:
        persistence.dir = args.dir
        persistence.dbfilename = args.dbfilename

    run_server([socket.AF_INET, socket.SOCK_STREAM], ("localhost", 6379))


if __name__ == "__main__":
    main()
