import socket
from typing import Tuple

class CaractereStuffing():
    """
    Classe responsavel por fazer o caractere stuffing no que será enviado na
    transmissão.
    """
    # 0b01111110 = 126 = '~'
    _FLAG = b'~'
    # 0b01111101 = 125 = '}'
    _ESCAPE = b'}'

    @classmethod
    def fazCaractereStuffing(cls, msg: bytes):
        """
        Adiciona os caracteres de escape e de flag à mesagem e retorna a
        mensagem "recheada".
        """
        return cls._FLAG + (msg\
            .replace(cls._ESCAPE, cls._ESCAPE+cls._ESCAPE)\
            .replace(cls._FLAG, cls._ESCAPE+cls._FLAG))\
            + cls._FLAG

    @classmethod
    def desfazCaractereStuffing(cls, msg: bytes):
        """
        Remove os caracteres de escape e de flag da mesagem e retorna mensagem
        depois de limpa.
        """
        return msg\
            .replace(cls._ESCAPE+cls._FLAG, cls._FLAG)\
            .replace(cls._ESCAPE+cls._ESCAPE, cls._ESCAPE)\
            [1:-1]

    @classmethod
    def transmissaoTerminou(cls, ultimosDoisBytes: bytes):
        """
        Identifica o fim de uma mensagem tranmitida
        """
        # TODO - notificar a funcao que invocou esse metodo caso os bytes
        # recebidos contenham o fim de uma transmissao e o inicio de uma proxima
        return not ultimosDoisBytes.endswith(cls._ESCAPE+cls._FLAG)\
            and ultimosDoisBytes.endswith(cls._FLAG)


class Transmissao():
    """
    Classe para tratar das transmissões, enviando e recebendo toda a mensagem
    """
    # REVIEW - há muito espaço para melhoria na classe de tranmissão
    _TAMANHO_BUFFER = 4096

    @classmethod
    def enviaBytes(cls, socket: socket.socket, msg: bytes) -> None:
        """
        Envia toda a mensagem através do socket para o socket remoto

        Pode laçar RuntimeError
        """
        totalEnviado = 0
        msgEstufada = CaractereStuffing.fazCaractereStuffing(msg)
        while totalEnviado < len(msgEstufada):
            enviado = socket.send(msgEstufada[totalEnviado:])
            if enviado == 0:
                raise RuntimeError("a conexão do socket foi quebrada")
            totalEnviado = totalEnviado + enviado

    @classmethod
    def recebeBytes(cls, socket: socket.socket) -> bytes:
        """
        Recebe toda a mensagem que foi enviada pelo socket remoto através do
        socket da conexao

        Pode lançar RuntimeError
        """
        mensagemRecebida = b''
        # NOTE - enquanto não encontrar a flag de termino continua recebendo
        # REVIEW - o que ocorre quando recebe apenas a flag termino? é um
        # término ou um inicio?
        while not CaractereStuffing.transmissaoTerminou(mensagemRecebida[-2:]):
            pedaco = socket.recv(cls._TAMANHO_BUFFER)
            if pedaco == b'':
                raise RuntimeError("a conexão do socket foi quebrada")
            mensagemRecebida = b''.join((mensagemRecebida, pedaco))
        return CaractereStuffing.desfazCaractereStuffing(mensagemRecebida)


class TransmissaoUdp():

    _TAMANHO_BUFFER = 1024


    @classmethod
    def enviaBytes(cls, sUdp: socket.socket, destIp: str, destPorta: int, dados: bytes) -> None:
        sUdp.sendto(dados, (destIp, destPorta))


    @classmethod
    def recebeBytes(cls, sUdp: socket.socket) -> Tuple[str, int, bytes]:
        endereco, porta, dados = ('', 0, b'')
        dados, (endereco, porta) = sUdp.recvfrom(TransmissaoUdp._TAMANHO_BUFFER)
        return (endereco, porta, dados)
