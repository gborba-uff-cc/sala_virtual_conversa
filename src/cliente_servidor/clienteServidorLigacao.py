import errno
import socket
import sys
import threading
from typing import Deque, NamedTuple, Tuple

import src.aplicacao.mensagens_aplicacao as ma
from src.util.mutex import Mutex


class InformacaoPar(NamedTuple):
    ip: str
    porta: int
    nomeUsuario: str


class ClienteServidorLigacao():

    _PORTA_PREFERENCIAL_SERVIDOR = 6000

    def __init__(self):

    # NOTE - propriedades compartilhadas entre threads =========================
        # NOTE - socket.AF_INET -> familia de enderecos IPv4
        # NOTE - socket.AF_INET6 -> familia de enderecos IPv6
        # NOTE - socket.SOCK_STREAM -> socket do tipo TCP
        # NOTE - socket.SOCK_DGRAM -> socket do tipo UDP
        self._sCliente = Mutex(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        sE = None
        sS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for tentativa in range(51):
            if tentativa >= 50:
                raise RuntimeError('Não foi possivel fazer o socket UDP para o servidor')
            try:
                nPorta = ClienteServidorLigacao._PORTA_PREFERENCIAL_SERVIDOR + tentativa
                sS.bind(('localhost',nPorta))
                # NOTE - armazena o endereco e porta do servidor
                sE = sS.getsockname()
                break
            except OSError as oe:
                # NOTE - Address already in use
                if oe.errno == errno.EADDRINUSE:
                    pass
        if isinstance(sS, socket.socket) and isinstance(sE, tuple):
            self._sServidor = Mutex(sS)
            self._endServidor: Tuple[str,int] = sE
        else:
            sys.exit(1)
        self._emChamada: Mutex = Mutex(False)
        self._recebendoChamada: Mutex = Mutex(False)
        self._realizandoChamada: Mutex = Mutex(False)
        self._log: Mutex = Mutex([])

        # NOTE - armazenando o endereço do par da ligacao
        self._infoChamadaEstabelecida: InformacaoPar = InformacaoPar('',0,'')
        self._infoChamadaRecebida: InformacaoPar = InformacaoPar('',0,'')
        self._infoChamadaRealizada: InformacaoPar = InformacaoPar('',0,'')
        self._executaServidor: bool = True
        # NOTE - thread do servidor que irá ser encerrada junto com a principal
        self._threadServidor: threading.Thread = threading.Thread(
                target=self._manipulaMensagens,
                daemon=True)
        self._threadServidor.start()
        # NOTE - deque é thread safe para append e pop nas duas pontas
        self._audioBuffer_envio: Deque = Deque([], maxlen=50)
        # NOTE - considerando que pacotes de audio não serão perdidos por não
        # irem para a rede
        self._audioBuffer_recebido: Deque = Deque([], maxlen=50)

    @property
    def infoChamadaEstabelecida(self):
        return self._infoChamadaEstabelecida

    @property
    def infoChamadaRecebida(self):
        return self._infoChamadaRecebida

    @property
    def infoChamadaRealizada(self):
        return self._infoChamadaRealizada

    @property
    def enderecoAtualServidorUdp(self):
        return self._endServidor

    @property
    def emChamada(self):
        """
        A função/método que utilizar esse método deverá realizar o acquire e
        release do lock
        """
        return self._emChamada

    @property
    def log(self) -> Mutex:
        """
        Retorna uma lista com todas as strings do log

        A função/método que utilizar esse método deverá realizar o acquire e
        release do lock
        """
        return self._log

    def clearLog(self) -> None:
        """
        Limpa o log de mensagens da aplicacao enviadas e recebidas

        A função/método que utilizar esse método deverá realizar o acquire e
        release do lock
        """
        self._log.data = []

    @property
    def bufferAudio_Recebido(self) -> Deque:
        return self._audioBuffer_recebido

    @property
    def bufferAudio_Envio(self) -> Deque:
        return self._audioBuffer_envio

    def realizaConvite(self, destIp: str, destPorta: int, destUsername: str, meuUsername: str) -> Tuple[str, Tuple[str, str]]:
        destIp = destIp if destIp else 'localhost'
        enviado, recebido = ('', ('', ''))
        cabecalho, corpo = ('', '')

    # NOTE - rejeita a invocacao se ja esta em chamada
        with self._emChamada.lock:
            if isinstance(self._emChamada.data, bool):
                destIp = socket.gethostbyname(destIp)

                # NOTE - ou se esta tentando ligar para si mesmo
                if self._emChamada.data or (destIp, destPorta) == (self._endServidor):
                    cabecalho = f'{ma.MensagensLigacao.CONVITE_REJEITADO.value.cod} {ma.MensagensLigacao.CONVITE_REJEITADO.value.description}'
                    recebido = (cabecalho, '')
                    self._escreveNoLog(enviado=enviado, recebido=cabecalho)
                    return (enviado, recebido)

    # NOTE - Envia um convite para uma chamada
        with self._sCliente.lock, self._realizandoChamada.lock:
            if isinstance(self._sCliente.data, socket.socket):
                enviado = ma.fazPedidoConvite(
                        self._sCliente.data,
                        destIp,
                        destPorta,
                        meuUsername,
                        self.enderecoAtualServidorUdp[1])
                self._realizandoChamada.data = True
                self._infoChamadaRealizada = InformacaoPar(destIp, destPorta, '')

        self._escreveNoLog(enviado=enviado, recebido='')
        return (enviado, (cabecalho, corpo))


    def respondeConvite(self, atende: bool):
        enviado, recebido = ('', ('', ''))

        if atende:
            self._infoChamadaEstabelecida = self._infoChamadaRecebida
            # NOTE - inicia a ligacao
            with self._emChamada.lock:
                if isinstance(self._emChamada.data, bool):
                    self._emChamada.data = True

        with self._sCliente.lock:
            if isinstance(self._sCliente.data, socket.socket):
                enviado = ma.fazRespostaConvite(self._sCliente.data, self._infoChamadaRecebida.ip, self._infoChamadaRecebida.porta, atende)
            self._infoChamadaRecebida = InformacaoPar('',0,'')

        with self._recebendoChamada.lock:
            if isinstance(self._recebendoChamada.data, bool):
                self._recebendoChamada.data = False

        self._escreveNoLog(enviado=enviado, recebido='')
        return (enviado, recebido)

    def realizaEncerramento(self) -> Tuple[str, Tuple[str,str]]:
        enviado, recebido = ('', ('', ''))

        with self._sCliente.lock:
            if isinstance(self._sCliente.data, socket.socket):
                enviado = ma.fazPedidoEncerrarLigacao(
                        self._sCliente.data,
                        self._infoChamadaEstabelecida.ip,
                        self._infoChamadaEstabelecida.porta)

        # NOTE - encerra a ligacao
        with self._emChamada.lock:
            if isinstance(self._emChamada.data, bool):
                self._emChamada.data = False

        self._escreveNoLog(enviado=enviado, recebido='')
        return (enviado, recebido)


    def _enviaPacoteAudio(self) -> Tuple[str, Tuple[str,str]]:
        enviado, recebido = ('', ('', ''))
        pacoteAudio = b''
        try:
            pacoteAudio = self._audioBuffer_envio.popleft()
        except IndexError:
            # NOTE - não envia caso não tenha o que enviar
            return (enviado, recebido)
        with self._sCliente.lock:
            if isinstance(self._sCliente.data, socket.socket):
                enviado = ma.enviaPacoteAudio(
                        self._sCliente.data,
                        self._infoChamadaEstabelecida.ip,
                        self._infoChamadaEstabelecida.porta,
                        pacoteAudio,
                        # b'abcdefghi '*200,
                        0)

        # self._escreveNoLog(enviado=enviado, recebido='')
        return (enviado, recebido)

    def fechaSockets(self):
        """
        Deve chamar essa função antes de encerrar para liberar os sockets.
        """
        self._executaServidor = False
        self._threadServidor.join()
        with self._sCliente.lock:
            if isinstance(self._sCliente.data, socket.socket):
                self._sCliente.data.close()
        with self._sServidor.lock:
            if isinstance(self._sServidor.data, socket.socket):
                self._sServidor.data.close()


# NOTE - metodos do servidor
    # def _manipulaMensagens(self) -> Tuple[str, Tuple[str,str]]:
    def _manipulaMensagens(self) -> None:
        """
        Retorna strings que podem ser exibidas no console da aplicação.

        Se for necessário usar as strings do retorno, um teste booleano deve ser
        feito para saber se as strings existem
        """

        while self._executaServidor:
            endOrigem, portaOrigem, cabecalho, corpo = ('', 0, '', '')

        # ======================================================================
        # NOTE - recebe uma mensagem
            with self._sServidor.lock:
                if isinstance(self._sServidor.data, socket.socket):
                    socketBloqueante = self._sServidor.data.getblocking()

                    # NOTE - faz com que o socket deixe de ser bloqueante
                    # (cliente e servidor compartilham a mesma thread)
                    self._sServidor.data.setblocking(False)
                    try:
                        # NOTE - le do socket
                        endOrigem, portaOrigem, cabecalho, corpo = ma.recebeMensagemUdp(self._sServidor.data)

                    except BlockingIOError as be:
                        pass
                    finally:
                        self._sServidor.data.setblocking(socketBloqueante)
                    # endOrigem, portaOrigem, cabecalho, corpo = ma.recebeMensagemUdp(self._sServidor.data)
        # NOTE - envia pacote de audio se estiver em chamada
            with self._emChamada.lock:
                if isinstance(self._emChamada.data, bool):
                    if self._emChamada.data:
                        self._enviaPacoteAudio()

        # ======================================================================
        # NOTE - recebeu convite de chamada
            if cabecalho.startswith(ma.MensagensLigacao.CONVITE.value.cod):
                with self._sCliente.lock, self._emChamada.lock, self._recebendoChamada.lock:
                        if isinstance(self._sCliente.data, socket.socket) and \
                                isinstance(self._emChamada.data, bool) and \
                                isinstance(self._recebendoChamada.data, bool):
                            # NOTE - recusa a nova chamada se já estou em chamada, ou
                            # se estou no processo de aceitar a chamada de outro usuario
                            if self._emChamada.data or (
                                    self._infoChamadaRecebida != InformacaoPar('',0,'') and
                                    self._infoChamadaRecebida != (endOrigem, portaOrigem)):
                                ma.fazRespostaConvite(self._sCliente.data, endOrigem, portaOrigem, False)
                            else:
                                if not self._recebendoChamada.data and isinstance(corpo, str):
                                    self._recebendoChamada.data = True
                                    nome, _, porta = corpo.partition('\n')
                                    self._infoChamadaRecebida = InformacaoPar(endOrigem, int(porta), nome)

        # ======================================================================
        # NOTE - recebeu resposta da chamada e foi aceita
            elif cabecalho.startswith(ma.MensagensLigacao.CONVITE_ACEITO.value.cod):
                with self._emChamada.lock, self._realizandoChamada.lock:
                    if isinstance(self._realizandoChamada.data, bool) and isinstance(self._emChamada.data, bool):
                        if self._realizandoChamada.data and endOrigem == self._infoChamadaRealizada[0]:
                            self._infoChamadaEstabelecida = self._infoChamadaRealizada
                            self._infoChamadaRealizada = InformacaoPar('',0,'')
                            self._emChamada.data = True
                            self._realizandoChamada.data = False

        # ======================================================================
        # NOTE - recebeu resposta da chamada e foi rejeitada
            elif cabecalho.startswith(ma.MensagensLigacao.CONVITE_REJEITADO.value.cod):
                with self._emChamada.lock, self._realizandoChamada.lock:
                    if isinstance(self._realizandoChamada.data, bool):
                        if self._realizandoChamada.data and endOrigem == self._infoChamadaRealizada[0]:
                            self._realizandoChamada.data = False
                            self._infoChamadaEstabelecida = InformacaoPar('',0,'')

        # ======================================================================
        # NOTE - recebeu aviso de encerrar ligação
            elif cabecalho.startswith(ma.MensagensLigacao.ENCERRAR_LIGACAO.value.cod):
                # NOTE - encerra somente se receber o pedido de encerrar vindo do par da ligacao
                if endOrigem == self._infoChamadaEstabelecida[0]:
                    # NOTE - sai da chamada
                    with self._emChamada.lock:
                        if isinstance(self._emChamada.data, bool):
                            self._emChamada.data = False
                corpo = ''

        # ======================================================================
        # NOTE - recebeu um pacote de audio
            elif cabecalho.startswith(ma.MensagensLigacao.PACOTE_AUDIO.value.cod):
                with self._emChamada.lock:
                    if self._emChamada.data and endOrigem == self._infoChamadaEstabelecida.ip:
                        # NOTE - adiciona o pacote de audio no buffer
                        if self._emChamada.data:
                            self._audioBuffer_recebido.append(corpo[1])
                            # pass
                cabecalho, corpo = ('', '')

        # ======================================================================
        # NOTE - recebeu uma mensagem que nao existe
            else:
                # TODO - tratar mensagem invalida
                pass

            self._escreveNoLog('', f'{cabecalho}{chr(10) if corpo else ""}{corpo}')

    def _escreveNoLog(self, enviado: str, recebido: str) -> None:
        with self._log.lock:
            if isinstance(self._log.data, list):
                if enviado:
                    # self._log.data.append(f'[mod.lig.E] >>>\n{enviado}')
                    self._log.data.append(f'{enviado}')
                if recebido:
                    # self._log.data.append(f'[mod.lig.R] >>>\n{recebido}')
                    self._log.data.append(f'{recebido}')
