import socket

class CaractereStuffing():
    # 0b01111110 = 126 = '~'
    _FLAG = b'~'
    # 0b01111101 = 125 = '}'
    _ESCAPE = b'}'

    @classmethod
    def fazCaractereStuffing(cls, msg: bytes):
        return cls._FLAG + (msg\
            .replace(cls._ESCAPE, cls._ESCAPE+cls._ESCAPE)\
            .replace(cls._FLAG, cls._ESCAPE+cls._FLAG))\
            + cls._FLAG

    @classmethod
    def desfazCaractereStuffing(cls, msg: bytes):
        return msg\
            .replace(cls._ESCAPE+cls._FLAG, cls._FLAG)\
            .replace(cls._ESCAPE+cls._ESCAPE, cls._ESCAPE)\
            [1:-1]

    @classmethod
    def transmissaoTerminou(cls, ultimosDoisBytes: bytes):
        return not ultimosDoisBytes.endswith(cls._ESCAPE+cls._FLAG)\
            and ultimosDoisBytes.endswith(cls._FLAG)


class Transmissao():
    """classe para tratar da transmissao, enviando e recebendo toda a mensagem"""
    _TAMANHO_BUFFER = 4096

    @classmethod
    def enviaBytes(cls, socket: socket.socket, msg: bytes) -> None:
        """pode lancar RuntimeError"""
        totalEnviado = 0
        msgEstufada = CaractereStuffing.fazCaractereStuffing(msg)
        while totalEnviado < len(msgEstufada):
            enviado = socket.send(msgEstufada[totalEnviado:])
            if enviado == 0:
                raise RuntimeError("socket connection broken")
            totalEnviado = totalEnviado + enviado

    @classmethod
    def recebeBytes(cls, socket: socket.socket) -> bytes:
        """pode lancar RuntimeError"""
        pedacos = b''
        bytesRecebidos = 0
        while not CaractereStuffing.transmissaoTerminou(pedacos[-2:]):
            pedaco = socket.recv(cls._TAMANHO_BUFFER)
            if pedaco == b'':
                raise RuntimeError("socket connection broken")
            pedacos = b''.join((pedacos, pedaco))
            bytesRecebidos = bytesRecebidos + len(pedaco)
        return CaractereStuffing.desfazCaractereStuffing(pedacos)
