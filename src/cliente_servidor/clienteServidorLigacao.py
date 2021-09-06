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


import socket
import src.aplicacao.mensagens_aplicacao as ma
from typing import Tuple, Union



class ClienteServidorLigacao():

    PORTA_SERVIDOR_LIGACAO = 6000

    def __init__(self):
        # usa .sendto(bytes, endereco) para enviar algo
        # usa .recvfrom(tambuffer) para receber algo; bytes, endereco
        # NOTE - socket.AF_INET -> familia de enderecos IPv4
        # NOTE - socket.AF_INET6 -> familia de enderecos IPv6
        # NOTE - socket.SOCK_STREAM -> socket do tipo TCP
        # NOTE - socket.SOCK_DGRAM -> socket do tipo UDP
        self._sCliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sServidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sServidor.bind(('localhost', ClienteServidorLigacao.PORTA_SERVIDOR_LIGACAO));
        # NOTE - armazenando o endereço do par da ligacao
        self._endIpParLigacao = ''
        self._emChamada = False
        self._recebendoChamada = False

    def realizaConvite(self, destIp: str, destPorta: int, meuUsername: str) -> Tuple[str, Tuple[str,str]]:
        enviado, recebido = ('', ('', ''))
        cabecalho, corpo = ('', '')

        # NOTE - rejeita a invocacao se ja esta em chamada
        if self._emChamada:
            # print('já existe uma chamada em andamento')
            recebido = (f'{ma.MensagensLigacao.CONVITE_REJEITADO.value.cod} {ma.MensagensLigacao.CONVITE_REJEITADO.value.description}', recebido[1])
            return (enviado, recebido)

        # NOTE - Envia um convite para uma chamada
        enviado = ma.fazPedidoConvite(
                self._sCliente,
                destIp,
                ClienteServidorLigacao.PORTA_SERVIDOR_LIGACAO,
                meuUsername)
        try:
            # NOTE - atribuindo um timeout de 400ms para o socket receber a resposta
            self._sServidor.settimeout(0.400)
            # NOTE - recebe a resposta do convite
            _, _, cabecalho, corpo = ma.recebeMensagemUdp(self._sServidor)
        except TimeoutError as te:
            print(te)
        finally:
            # NOTE - removendo o timeout atribuido ao socket
            self._sServidor.settimeout(0.400)

        # NOTE - se a chamada foi aceita atualiza o endereco do par da chamada
        if cabecalho.startswith(ma.MensagensLigacao.CONVITE_ACEITO.value.cod):
            self._endIpParLigacao = destIp
        else:
            if not cabecalho.startswith(ma.MensagensLigacao.CONVITE_REJEITADO.value.cod):
                # TODO - O que fazer se receber uma mensagem que não é uma resposta ao convite?
                pass
            self._endIpParLigacao = ''

        if isinstance(corpo, str):
            return (enviado, (cabecalho, corpo))
        else:
            return (enviado, (cabecalho, '<bytes>'))

    def realizaEncerramento(self, destIp: str) -> Tuple[str, Tuple[str,str]]:
        enviado, recebido = ('', ('', ''))

        # NOTE - envia um aviso de encerramento da chamada
        enviado = ma.fazPedidoEncerrarLigacao(
                self._sCliente,
                self._endIpParLigacao,
                ClienteServidorLigacao.PORTA_SERVIDOR_LIGACAO)

        # NOTE - encerra a ligacao
        self._emChamada = False
        return (enviado, recebido)

    def enviaPacoteAudio(self, destPorta: int, nSeqAudio: int ,bytesAudio: bytes) -> Tuple[str, Tuple[str,str]]:
        enviado, recebido = ('', ('', ''))

        ma.enviaPacoteAudio(
                self._sCliente,
                self._endIpParLigacao,
                ClienteServidorLigacao.PORTA_SERVIDOR_LIGACAO,
                bytesAudio,
                nSeqAudio)

        return (enviado, recebido)

    def manipulaMensagens(self) -> Tuple[str, Tuple[str,str]]:
        """
        Retorna strings para que sejam apresentadas no console da aplicação.

        Deve fazer um teste booleano nas strings para saber se elas existem
        """
        socketBloqueante = self._sServidor.getblocking()
        endOrigem, portaOrigem, cabecalho, corpo = ('', 0, '', '')

        # NOTE - faz com que o socket deixe de ser bloqueante
        # (cliente e servidor compartilham a mesma thread)
        self._sServidor.setblocking(False)
        try:
            endOrigem, portaOrigem, cabecalho, corpo = ma.recebeMensagensUdp(self._sServidor)

            # NOTE - recebeu pedido de ligacao
            if cabecalho.startswith(ma.MensagensLigacao.CONVITE.value.cod):
                # NOTE - recusa a nova chamada se já estou em chamada
                if self._emChamada:
                    ma.fazRespostaConvite(self._sCliente, endOrigem, portaOrigem, False)
                    if isinstance(corpo, str):
                        return ('',(cabecalho,corpo))

            # NOTE - recebeu aviso de encerrar ligação
            elif cabecalho.startswith(ma.MensagensLigacao.ENCERRAR_LIGACAO.value.cod):
                # NOTE - sai da chamada
                self._emChamada = False
                return ('',(cabecalho,''))

            # NOTE - recebeu um pacote de audio
            elif cabecalho.startswith(ma.MensagensLigacao.PACOTE_AUDIO.value.cod):
                # NOTE - adiciona o pacote de audio no buffer
                # TODO - adicionar o pacote de audio no buffer
                return ('',(cabecalho,'<bytes>'))

            else:
                # TODO - tratar mensagem invalida
                return ('',('',''))

        except BlockingIOError as be:
            # NOTE - "[ERRNO 11] Resource temporarily unavailable"
            # => não há mensagem
            #    (sem problemas)
            if be.errno == 11:
                return ('',('',''))

        self._sServidor.setblocking(socketBloqueante)
        return ('',('',''))
