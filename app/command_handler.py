from app.storage import Storage
import app.persistence as persistence
from app.util.encoder import encode_list


class CommandHandler:
    def __init__(self, persistence_enabled):
        self.storage = Storage()
        if persistence_enabled:
            self.storage.load_from_db_file()

    def handle_set_command(self, key, value, ttl=None):
        key = key.decode()
        value = value.decode()
        if ttl:
            self.storage.set_with_ttl(key, value, ttl)
            return "+OK\r\n"
        else:
            self.storage.set(key, value)
            return "+OK\r\n"

    def handle_get_command(self, key):
        value = self.storage.get(key.decode())
        if value:
            return f"+{value}\r\n"
        else:
            return "$-1\r\n"

    def handle_config_command(self, command, key):
        if command.lower() == b"get":
            if key.lower() == b"dir":
                return f"*2\r\n$3\r\ndir\r\n${len(persistence.dir)}\r\n{persistence.dir}\r\n".encode()
            elif key.lower() == b"dbfilename":
                return f"*2\r\n$3\r\ndir\r\n${len(persistence.dbfilename)}\r\n{persistence.dbfilename}\r\n".encode()
            else:
                return b"+ERR\r\n"

    def handle_keys_command(self):
        databases = persistence.read_file()

        keys = []
        for db_name, data in databases.items():
            for key in data.keys():
                keys.append(key)

        return f"*{encode_list(keys)}".encode()
