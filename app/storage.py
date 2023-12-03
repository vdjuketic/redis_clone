import time


class Storage:
    def __init__(self):
        self.storage = {}

    def set(self, key, value):
        self.storage[key] = (value, -1)

    def set_with_ttl(self, key, value, ttl):
        # ttl in seconds
        self.storage[key] = (value, int(time.time() + ttl))

    def get(self, key):
        if key in self.storage:
            entry = self.storage[key]
            if entry[1] != -1:
                timestamp = int(time.time())
                if entry[1] < timestamp:
                    del self.storage[key]
                else:
                    return entry[0]
            else:
                return entry[0]

        return None
