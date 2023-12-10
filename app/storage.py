from datetime import datetime, timedelta
import app.persistence as persistence


class Storage:
    def __init__(self):
        self.storage = {}

    def load_from_db_file(self):
        persisted_data = persistence.read_file()
        if persisted_data:
            self.storage = persisted_data[0]

    def set(self, key, value):
        self.storage[key] = (value, -1)

    def set_with_ttl(self, key, value, ttl):
        self.storage[key] = (
            value,
            (datetime.now().utcnow() + timedelta(milliseconds=ttl)).isoformat(
                sep=" ", timespec="milliseconds"
            ),
        )

    def get(self, key):
        if key in self.storage:
            entry = self.storage[key]
            if type(entry) is not tuple:
                entry = (entry, -1)

            if entry[1] != -1:
                current = datetime.now().utcnow()
                saved = datetime.fromisoformat(entry[1])
                if saved < current:
                    del self.storage[key]
                else:
                    return entry[0]
            else:
                return entry[0]

        return None
