from app.storage import Storage

storage = Storage()


def handle_set_command(key, value, ttl):
    if ttl:
        storage.set_with_ttl(key, value, ttl)
        return b"+OK\r\n"
    else:
        storage.set(key, value, ttl)
        return b"+OK\r\n"


def handle_get_command(key):
    value = storage.get(key)
    if value:
        return b"+" + value + b"\r\n"
    else:
        return b"$-1\r\n"
