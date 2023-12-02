import socket


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    conn, _ = server_socket.accept()  # wait for client

    message = conn.recv(1024).decode()
    print(f"received message: {message}")

    if message == "*1\r\n$4\r\nping\r\n":
        conn.sendall("PONG\r\n".encode())


if __name__ == "__main__":
    main()
