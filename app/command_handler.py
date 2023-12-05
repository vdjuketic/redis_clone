from app.storage import Storage
import app.persistence as persistence

storage = Storage()


def handle_set_command(key, value, ttl=None):
    if ttl:
        storage.set_with_ttl(key, value, ttl)
        return b"+OK\r\n"
    else:
        storage.set(key, value)
        return b"+OK\r\n"


def handle_get_command(key):
    value = storage.get(key)
    if value:
        return b"+" + value + b"\r\n"
    else:
        return b"$-1\r\n"


def handle_config_command(command, key):
    if command.lower() == b"get":
        if key.lower() == b"dir":
            return f"*2\r\n$3\r\ndir\r\n${len(persistence.dir)}\r\n{persistence.dir}\r\n".encode()
        elif key.lower() == b"dbfilename":
            return f"*2\r\n$3\r\ndir\r\n${len(persistence.dbfilename)}\r\n{persistence.dbfilename}\r\n".encode()
        else:
            return b"+ERR\r\n"
