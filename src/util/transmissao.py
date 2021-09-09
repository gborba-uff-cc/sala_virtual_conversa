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
    def transmissaoTerminou(cls, pedaco: bytes) -> Tuple[bool, bytes, bytes]:
        """
        Identifica o fim de uma mensagem tranmitida
        """

        parte1, _, parte2 = pedaco.partition(cls._FLAG+cls._FLAG)
        # NOTE - se tenho uma segunda mensagem no pedaco recebido
        if parte2:
            return (True, b''.join((parte1,cls._FLAG)), b''.join((cls._FLAG,parte2)))
        else:
            terminou = pedaco.endswith(cls._FLAG) and \
                not pedaco.endswith(cls._ESCAPE+cls._FLAG)
            return (terminou, pedaco, b'')


class Transmissao():
    """
    Classe para tratar das transmissões, enviando e recebendo toda a mensagem
    """

    # REVIEW - há muito espaço para melhoria na classe de tranmissão
    _TAMANHO_BUFFER = 4096
    _sobraUltimaTransmissao: bytes = b''

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
        mensagemRecebida = cls._sobraUltimaTransmissao
        terminou, msg1, msg2 = CaractereStuffing.transmissaoTerminou(mensagemRecebida)
        # NOTE - enquanto não encontrar a flag de termino continua recebendo
        while not terminou:
            pedaco = socket.recv(cls._TAMANHO_BUFFER)
            if pedaco == b'':
                raise RuntimeError("a conexão do socket foi quebrada")
            terminou, msg1, msg2 = CaractereStuffing.transmissaoTerminou(pedaco)
            mensagemRecebida = b''.join((mensagemRecebida, msg1))
        if msg2:
            cls._sobraUltimaTransmissao = msg2
        return CaractereStuffing.desfazCaractereStuffing(mensagemRecebida)


class TransmissaoUdp():

    # NOTE - deve ser maior que o maior pacote de dados recebido
    _TAMANHO_BUFFER = 2048

    @classmethod
    def enviaBytes(cls, sUdp: socket.socket, destIp: str, destPorta: int, dados: bytes) -> None:
        """
        Envia todos os bytes de dados para o destino.

        Pode lançar RuntimeError
        """

        totalEnviado = 0
        while totalEnviado < len(dados):
            enviado = sUdp.sendto(dados[totalEnviado:], (destIp, destPorta))
            if enviado == 0:
                raise RuntimeError("a conexão do socket foi quebrada")
            totalEnviado = totalEnviado + enviado

    @classmethod
    def recebeBytes(cls, sUdp: socket.socket) -> Tuple[str, int, bytes]:
        """Recebe os bytes através do socket UDP"""

        endereco, porta, dados = ('', 0, b'')
        pedaco, (endereco, porta) = sUdp.recvfrom(cls._TAMANHO_BUFFER)
        dados = pedaco

        try:
            while pedaco != b'':
                pedaco, _ = sUdp.recvfrom(TransmissaoUdp._TAMANHO_BUFFER)
                dados = b''.join((dados, pedaco))
        except BlockingIOError as be:
            pass
        return (endereco, porta, dados)
