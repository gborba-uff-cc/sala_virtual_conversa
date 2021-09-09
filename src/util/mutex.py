import threading


class Mutex():
    """
    Classe para organizar o acesso feito por threads a certas 'variaveis'.
    """
    def __init__(self, data) -> None:
        self._data = data
        self._lock = threading.RLock()

    @property
    def lock(self):
        return self._lock

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
