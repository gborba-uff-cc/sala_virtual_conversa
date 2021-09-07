# SECTION - Objetivos da segunda parte do trabalho
# NOTE - inicializar socket UDP que será usado para a comunicao com o servidor de ligação
# NOTE - enviar uma mensagem de 'convite', a um servidor de ligação que encontra-se em um certo endereco IP e receber a 'resposta_ao_convite'
# NOTE - o 'convite' deve conter o nome de usuário, o ip e a porta utilizadas pelo socket do cliente
# NOTE - a 'resposta_ao_convite' pode ser 'rejeitado' ou 'aceito'
# NOTE - todas as mensagens trocadas devem ser logadas
# NOTE - caso 'convite'seja 'aceito', inicia a coleta e transmissão do sinal de áudio
# NOTE - caso o cliente deseje encerrar a ligação uma mensagem 'encerrar_ligação' deverá ser enviada e a transmissão do áudio deverá ser encerrado
# NOTE - caso o cliente receba 'encerrar_ligacao' ele deverá parar transmitir
# NOTE - se resposta_ao_convite for rejeitado mostrar na tela a mensagem 'usuário destino ocupado'
# !SECTION


import errno
import socket
import src.aplicacao.mensagens_aplicacao as ma
from src.util.mutex import Mutex
import threading
from typing import Deque, Tuple, Union


class ClienteServidorLigacao():

    _PORTA_PREFERENCIAL_SERVIDOR = 6000

    def __init__(self):
        # self._sCliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self._sServidor.bind(('localhost', ClienteServidorLigacao._PORTA_SERVIDOR_LIGACAO))

    # NOTE - propriedades compartilhadas entre threads =========================
        # NOTE - socket.AF_INET -> familia de enderecos IPv4
        # NOTE - socket.AF_INET6 -> familia de enderecos IPv6
        # NOTE - socket.SOCK_STREAM -> socket do tipo TCP
        # NOTE - socket.SOCK_DGRAM -> socket do tipo UDP
        # NOTE - fazer lock antes de usar
        self._sCliente = Mutex(socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM))
        # NOTE - fazer lock antes de usar
        self._sServidor = Mutex(socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM))
        with self._sServidor.lock:
            if isinstance(self._sServidor.data, socket.socket):
                for tentativa in range(51):
                    if tentativa >= 50:
                        raise RuntimeError('Não foi possivel (criar o/fazer bind do) socket UDP para o servidor')
                    try:
                        self._sServidor.data.bind((
                                'localhost',
                                ClienteServidorLigacao._PORTA_PREFERENCIAL_SERVIDOR + tentativa))
                        # NOTE - armazena o endereco e porta do servidor
                        self._endServidor: Tuple[str,int] = self._sServidor.data.getsockname()
                        break
                    except OSError as oe:
                        # NOTE - Address already in use
                        if oe.errno == errno.EADDRINUSE:
                            pass
        # NOTE - fazer lock antes de escrever
        self._emChamada : Mutex = Mutex(False)
        # NOTE - fazer lock antes de escrever
        self._recebendoChamada : Mutex = Mutex(False)
        # NOTE - fazer lock antes de ler/escrever
        self._log : Mutex = Mutex([])

    # NOTE - propriedades não compartilhadas entre threads =====================
        # NOTE - armazenando o endereço do par da ligacao
        self._endParLigacao: Tuple[str, int] = ('',0)
        self._endIpChamadaRecebida: Tuple[str, int] = ('',0)
        # NOTE - thread do servidor que irá ser encerrada junto com a principal
        self._executaServidor: bool = True
        self._threadServidor: threading.Thread = threading.Thread(
                target=self._manipulaMensagens,
                daemon=True)
        self._threadServidor.start()
        # NOTE - deque é thread safe para append e pop nas duas pontas
        self._audioBuffer_saida: Deque = Deque([], maxlen=50)
        # NOTE - considerando que pacotes de audio não serão perdidos por não
        # irem para a rede
        self._audioBuffer_entrada: Deque = Deque([], maxlen=50)


    # @property
    # def log(self) -> Mutex:
    #     """
    #     Retorna o log das mensagens sobre as ligacoes que foram trocadas

    #     A função/método que utilizar esse método deverá realizar o acquire e
    #     release do lock
    #     """
    #     return self._log

    # def clearLog(self):
    #     """
    #     A função/método que utilizar esse método deverá realizar o acquire e
    #     release do lock
    #     """
    #     self._log

# NOTE - métodos do cliente
    def realizaConvite(self, destIp: str, destPorta: int, meuUsername: str) -> Tuple[str, Tuple[str,str]]:
        enviado, recebido = ('', ('', ''))
        cabecalho, corpo = ('', '')

    # NOTE - rejeita a invocacao se ja esta em chamada
        if self._emChamada.data:
            # print('já existe uma chamada em andamento')
            recebido = (f'{ma.MensagensLigacao.CONVITE_REJEITADO.value.cod} {ma.MensagensLigacao.CONVITE_REJEITADO.value.description}', '')
            self._escreveNoLog(enviado, '')
            return (enviado, recebido)

    # NOTE - Envia um convite para uma chamada
        with self._sCliente.lock:
            if isinstance(self._sCliente.data, socket.socket):
                enviado = ma.fazPedidoConvite(
                        self._sCliente.data,
                        destIp,
                        destPorta,
                        meuUsername)
        with self._sServidor.lock:
            if isinstance(self._sServidor.data, socket.socket):
                try:
                    # NOTE - atribuindo um timeout de 400ms para o socket receber a resposta
                    self._sServidor.data.settimeout(0.400)
                    # NOTE - recebe a resposta do convite
                    _, _, cabecalho, corpo = ma.recebeMensagemUdp(self._sServidor.data)
                except TimeoutError as te:
                    print(te)
                finally:
                    # NOTE - removendo o timeout atribuido ao socket
                    self._sServidor.data.settimeout(0.400)

    # NOTE - se a chamada foi aceita atualiza propriedades
        if cabecalho.startswith(ma.MensagensLigacao.CONVITE_ACEITO.value.cod):
            self._endIpParLigacao = (destIp, destPorta)
            with self._emChamada.lock:
                if isinstance(self._emChamada.data, bool):
                    self._emChamada.data = True
        else:
            if not cabecalho.startswith(ma.MensagensLigacao.CONVITE_REJEITADO.value.cod):
                # TODO - O que fazer se receber uma mensagem que não é uma resposta ao convite?
                pass
            self._endIpParLigacao = ('',0)

        # if isinstance(corpo, str):
        #     return (enviado, (cabecalho, corpo))
        # else:
        #     return (enviado, (cabecalho, '<bytes>'))

        if not isinstance(corpo, str):
            corpo = '<bytes>'

        # NOTE - ASCII chr(10) = '\n'
        self._escreveNoLog(enviado, f'{cabecalho}{chr(10) if corpo else ""}{corpo}')
        return (enviado, (cabecalho, corpo))


    def respondeConvite(self, atende: bool):
        # TODO -
        if atende:
            self._endIpParLigacao = self._endIpChamadaRecebida
        with self._sCliente.lock:
            self._endIpChamadaRecebida = ('',0)
            if isinstance(self._sCliente.data, socket.socket):
                ma.fazRespostaConvite(self._sCliente.data, *self._endIpChamadaRecebida, atende)
        with self._recebendoChamada.lock:
            self._recebendoChamada.data = False


    def realizaEncerramento(self, destIp: str) -> Tuple[str, Tuple[str,str]]:
        enviado, recebido = ('', ('', ''))

        with self._sCliente.lock:
            if isinstance(self._sCliente.data, socket.socket):
                # NOTE - envia um aviso de encerramento da chamada
                # enviado = ma.fazPedidoEncerrarLigacao(
                #         self._sCliente.data,
                #         self._endParLigacao,
                #         ClienteServidorLigacao._PORTA_SERVIDOR_LIGACAO)
                enviado = ma.fazPedidoEncerrarLigacao(
                        self._sCliente.data,
                        self._endParLigacao[0],
                        self._endParLigacao[1])

        # NOTE - encerra a ligacao
        with self._emChamada.lock:
            if isinstance(self._emChamada, bool):
                self._emChamada.data = False
        return (enviado, recebido)


    def enviaPacoteAudio(self, destPorta: int, nSeqAudio: int ,bytesAudio: bytes) -> Tuple[str, Tuple[str,str]]:
        enviado, recebido = ('', ('', ''))

        with self._sCliente.lock:
            if isinstance(self._sCliente.data, socket.socket):
                # enviado = ma.enviaPacoteAudio(
                #         self._sCliente.data,
                #         self._endIpParLigacao,
                #         ClienteServidorLigacao._PORTA_SERVIDOR_LIGACAO,
                #         bytesAudio,
                #         nSeqAudio)
                enviado = ma.enviaPacoteAudio(
                        self._sCliente.data,
                        self._endIpParLigacao[0],
                        self._endIpParLigacao[1],
                        bytesAudio,
                        nSeqAudio)

        return (enviado, recebido)


    @property
    def enderecoAtualServidorUdp(self):
        return self._endServidor


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
        return self._audioBuffer_entrada


    @property
    def bufferAudio_Envio(self) -> Deque:
        return self._audioBuffer_saida


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

        # NOTE - recebe uma mensagem
            with self._sServidor.lock:
                if isinstance(self._sServidor.data, socket.socket):
                    socketBloqueante = self._sServidor.data.getblocking()

                    # NOTE - faz com que o socket deixe de ser bloqueante
                    # (cliente e servidor compartilham a mesma thread)
                    self._sServidor.data.setblocking(False)
                    try:
                        # NOTE - le o socket
                        endOrigem, portaOrigem, cabecalho, corpo = ma.recebeMensagemUdp(self._sServidor.data)
                    except BlockingIOError as be:
                        pass
                    finally:
                        self._sServidor.data.setblocking(socketBloqueante)
                        # return ('',('',''))

        # NOTE - recebeu pedido de ligacao
            if cabecalho.startswith(ma.MensagensLigacao.CONVITE.value.cod):
                # NOTE - recusa a nova chamada se já estou em chamada
                if self._emChamada.data or self._endIpChamadaRecebida[0]:
                    with self._sCliente.lock:
                        if isinstance(self._sCliente.data, socket.socket):
                            ma.fazRespostaConvite(self._sCliente.data, endOrigem, portaOrigem, False)
                else:
                    with self._recebendoChamada.lock:
                        if not self._recebendoChamada.data:
                            self._recebendoChamada.data = True
                            self._endIpChamadaRecebida = (endOrigem, portaOrigem)

                # if isinstance(corpo, str):
                #     return ('',(cabecalho,corpo))

        # NOTE - recebeu aviso de encerrar ligação
            elif cabecalho.startswith(ma.MensagensLigacao.ENCERRAR_LIGACAO.value.cod):
                # NOTE - encerra somente se receber o pedido de encerrar vindo do par da ligacao
                if endOrigem == self._endIpParLigacao:
                    # NOTE - sai da chamada
                    with self._emChamada.lock:
                        self._emChamada.data = False
                # return ('',(cabecalho,''))
                corpo = ''

        # NOTE - recebeu um pacote de audio
            elif cabecalho.startswith(ma.MensagensLigacao.PACOTE_AUDIO.value.cod):
                if self._emChamada.data and endOrigem == self._endIpParLigacao:
                    # NOTE - adiciona o pacote de audio no buffer
                    if self._emChamada.data:
                        self._audioBuffer_entrada.append(corpo)
                # return ('',(cabecalho,'<bytes>'))
                corpo = '<bytes>'

            else:
                # TODO - tratar mensagem invalida
                pass
                # return ('',('',''))

            # return ('',('',''))
            self._escreveNoLog('', f'{cabecalho}{chr(10) if corpo else ""}{corpo}')
            # return ('',(cabecalho,corpo))

    def _escreveNoLog(self, enviado: str, recebido: str) -> None:
        with self._log.lock:
            if isinstance(self._log.data, list):
                if enviado:
                    self._log.data.append(f'mod.lig.R: {enviado}')
                if recebido:
                    self._log.data.append(f'mod.lig.E: {recebido}')
