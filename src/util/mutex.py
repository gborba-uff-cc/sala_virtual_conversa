import threading


class Mutex():
    """
    Classe para organizar o acesso feito por threads a certas 'variaveis'.
    """
    def __init__(self, data) -> None:
        self._data = data
        self._lock = threading.Lock()

    @property
    def lock(self):
        return self._lock

    @property
    def data(self):
        """
        data só será retornado se o lock tiver sido obtido
        """
        # return self._data if self.lock.locked() else None
        if self.lock.locked():
            return self._data
        else:
            print('Tentativa de acesso ao mutex sem o devido acquire')

    @data.setter
    def data(self, data):
        """
        data só será modificado se o lock tiver sido obtido.
        """
        if self._lock.locked():
            self._data = data
        else:
            print('Tentativa de acesso ao mutex sem o devido acquire')
