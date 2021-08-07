import threading


class Mutex():
    def __init__(self, data) -> None:
        self._data = data
        self.lock = threading.Lock()

    @property
    def data(self):
        """data só será retornado se o lock tiver sido obtido"""
        return self._data if self.lock.locked() else None
