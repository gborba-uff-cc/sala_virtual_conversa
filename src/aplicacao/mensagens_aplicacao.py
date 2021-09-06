from enum import Enum
from socket import SOCK_DGRAM, SOCK_STREAM, socket
from typing import NamedTuple

from src.util.transmissao import Transmissao


class MensagemAplicacao(NamedTuple):
    cod: str
    description: str


class MensagensAplicacao(Enum):
    REGISTO = MensagemAplicacao('1', 'PEDIDO REGISTRO')
    REGISTO_EXITO = MensagemAplicacao('2', 'REGISTRO BEM-SUCEDIDO')
    REGISTO_FALHA = MensagemAplicacao('3', 'REGISTRO MAL-SUCEDIDO')
    CONSULTA = MensagemAplicacao('4', 'PEDIDO CONSULTA')
    CONSULTA_EXITO = MensagemAplicacao('5', 'CONSULTA BEM-SUCEDIDA')
    CONSULTA_FALHA = MensagemAplicacao('6', 'CONSULTA MAL-SUCEDIDA')
    ENCERRAMENTO = MensagemAplicacao('7', 'PEDIDO ENCERRAMENTO')

class MensagensLigacao(Enum):
    CONVITE = MensagemAplicacao('','PEDIDO CONVITE')
    CONVITE_ACEITO = MensagemAplicacao('','CONVITE ACEITO')
    CONVITE_REJEITADO = MensagemAplicacao('','CONVITE REJEITADO')
    ENCERRAR_LIGACAO = MensagemAplicacao('','ENCERRAR LIGACAO')
    PACOTE_AUDIO = MensagemAplicacao('','PACOTE AUDIO')

def fazPedidoRegistro(sConexao: socket, nomeDesejado: str):
    """Solicita o registro do nome no servidor"""
    tipoCabecalho = MensagensAplicacao.REGISTO
    cabecalho = tipoCabecalho.value.cod + ' ' + tipoCabecalho.value.description
    corpo = '\n' + nomeDesejado
    mensagemCompleta = cabecalho + corpo
    Transmissao.enviaBytes(
        socket=sConexao,
        msg=mensagemCompleta.encode('UTF8'))
    # para mostrar na interface o que esta sendo enviado e recebido
    return mensagemCompleta


def fazRespostaPedidoRegistro(sConexao, registrou: bool):
    """Responde a solicitação de registro do nome feita pelo cliente"""
    tipoCabecalho = MensagensAplicacao.REGISTO_EXITO if registrou else MensagensAplicacao.REGISTO_FALHA
    cabecalho = tipoCabecalho.value.cod + ' ' + tipoCabecalho.value.description
    corpo = ''
    mensagemCompleta = cabecalho + corpo
    Transmissao.enviaBytes(
        socket=sConexao,
        msg=mensagemCompleta.encode('UTF8'))
    return mensagemCompleta


def fazPedidoConsulta(sConexao: socket, nomeDesejado: str):
    """Solicita a consulta de um nome"""
    tipoCabecalho = MensagensAplicacao.CONSULTA
    cabecalho = tipoCabecalho.value.cod + ' ' + tipoCabecalho.value.description
    corpo = '\n' + nomeDesejado
    mensagemCompleta = cabecalho + corpo
    Transmissao.enviaBytes(
        socket=sConexao,
        msg=mensagemCompleta.encode('UTF8'))
    return mensagemCompleta


def fazRespostaPedidoConsulta(sConexao, encontrou: bool, ip: str = '', porta: str = ''):
    """Responde a solicitação de consulta ao nome feita pelo cliente"""
    tipoCabecalho = MensagensAplicacao.CONSULTA_EXITO if encontrou else MensagensAplicacao.CONSULTA_FALHA
    cabecalho = tipoCabecalho.value.cod + ' ' + tipoCabecalho.value.description
    corpo = ('\n' + ip + ' ' + porta) if encontrou else ''
    mensagemCompleta = cabecalho + corpo
    Transmissao.enviaBytes(
        socket=sConexao,
        msg=mensagemCompleta.encode('UTF8'))
    return mensagemCompleta


def fazPedidoEncerramento(sConexao: socket):
    """Clinte informa que quer encerrar a conexão com o servidor"""
    tipoCabecalho = MensagensAplicacao.ENCERRAMENTO
    cabecalho = tipoCabecalho.value.cod + ' ' + tipoCabecalho.value.description
    corpo = ''
    mensagemCompleta = cabecalho + corpo
    Transmissao.enviaBytes(
        socket=sConexao,
        msg=mensagemCompleta.encode('UTF8'))
    return mensagemCompleta


def recebePedidoOuResposta(socket):
    """Função padrão para receber o cabeçalho e o corpo de uma transmissão da aplicação"""
    cabecalho, corpo = ('', '')
    if socket.type == SOCK_STREAM:
        msgBytes = Transmissao.recebeBytes(socket)
        msgStr = msgBytes.decode('UTF8')
        cabecalho, _, corpo = msgStr.partition('\n')
    elif socket.type == SOCK_DGRAM:
        pass
    return (cabecalho, corpo)


# NOTE - mensagens referentes a ligação na aplicação
def fazPedidoConvite(
        sUdp: socket,
        destIp: str,
        destPorta: int,
        meuUsername: str):
    """Envia o convite de ligação para o endereco de destino"""
    raise NotImplementedError()
    tipoCabecalho = MensagensLigacao.CONVITE
    cabecalho = f'{tipoCabecalho.value.cod} {tipoCabecalho.value.description}'
    # TODO - enviar as informações necessárias ao corpa da mensagem
    corpo = f'\n{meuUsername}'
    mensagemCompleta = f'{cabecalho}{corpo}'
    Transmissao.enviaBytes_UdpTimeout(
        socket=sUdpOrigem,
        msg=mensagemCompleta.encode('UTF8'))


def fazRespostaConvite(
        sUdp: socket,
        destIp: str,
        destPorta: int,
        conviteAceito: bool):
    """Responde a solicitação do convite de ligação"""
    raise NotImplementedError()
    tipoCabecalho = MensagensLigacao.CONVITE_ACEITO if conviteAceito else MensagensLigacao.CONVITE_REJEITADO
    cabecalho = f'{tipoCabecalho.value.cod} {tipoCabecalho.value.description}'
    corpo = ''
    mensagemCompleta = f'{cabecalho}{corpo}'
    Transmissao.enviaBytes_UdpTimeout(
        socket=sUdpOrigem,
        msg=mensagemCompleta.encode('UTF8'))
    return mensagemCompleta


def fazPedidoEncerrarLigacao(
        sUdp: socket,
        destIp: str,
        destPorta: int):
    """Envia um aviso de encerramento da ligação"""
    tipoCabecalho = MensagensLigacao.ENCERRAR_LIGACAO
    cabecalho = f'{tipoCabecalho.value.cod} {tipoCabecalho.value.description}'
    corpo = ''
    mensagemCompleta = f'{cabecalho}{corpo}'
    Transmissao.enviaBytes_UdpTimeout(
        socket=sUdpOrigem,
        msg=mensagemCompleta.encode('UTF8'))
    return mensagemCompleta


def enviaPacoteAudio(
        sUdp: socket,
        destIp: str,
        destPorta: int,
        bytesEnviar: bytes,
        nPacote: int):
    raise NotImplementedError()
    tipoCabecalho = MensagensLigacao.PACOTE_AUDIO
    cabecalho = f'{tipoCabecalho.value.cod} {tipoCabecalho.value.description}'.encode('UTF-8')
    corpo = f'\n{nPacote}\n'.encode('UTF-8') + bytesEnviar
    mensagemCompleta = f'{cabecalho}{corpo}'
    Transmissao.enviaBytes_Udp(
        socket=sUdpOrigem,
        msg=mensagemCompleta)
    return mensagemCompleta
