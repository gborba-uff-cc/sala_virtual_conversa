from enum import Enum
from socket import socket, htons, ntohs
from typing import NamedTuple, Tuple, Union

from src.util.transmissao import Transmissao, TransmissaoUdp


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
    CONVITE = MensagemAplicacao('1','PEDIDO CONVITE')
    CONVITE_ACEITO = MensagemAplicacao('2','CONVITE ACEITO')
    CONVITE_REJEITADO = MensagemAplicacao('3','CONVITE REJEITADO')
    ENCERRAR_LIGACAO = MensagemAplicacao('4','ENCERRAR LIGACAO')
    PACOTE_AUDIO = MensagemAplicacao('5','PACOTE AUDIO')

def fazPedidoRegistro(sConexao: socket, nomeDesejado: str, portaUdpDesejada: int):
    """Solicita o registro do nome no servidor"""
    tipoCabecalho = MensagensAplicacao.REGISTO
    cabecalho = tipoCabecalho.value.cod + ' ' + tipoCabecalho.value.description
    corpo = '\n' + nomeDesejado + '\n' + str(portaUdpDesejada)
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


def fazPedidoEncerramento(sConexao: socket, porta: int):
    """Clinte informa que quer encerrar a conexão com o servidor"""
    tipoCabecalho = MensagensAplicacao.ENCERRAMENTO
    cabecalho = tipoCabecalho.value.cod + ' ' + tipoCabecalho.value.description
    corpo = '\n' + str(porta)
    mensagemCompleta = cabecalho + corpo
    Transmissao.enviaBytes(
        socket=sConexao,
        msg=mensagemCompleta.encode('UTF8'))
    return mensagemCompleta


def recebePedidoOuResposta(socket):
    """Função padrão para receber o cabeçalho e o corpo de uma transmissão da aplicação"""
    cabecalho, corpo = ('', '')
    msgBytes = Transmissao.recebeBytes(socket)
    msgStr = msgBytes.decode('UTF8')
    cabecalho, _, corpo = msgStr.partition('\n')
    return (cabecalho, corpo)


# NOTE - mensagens referentes a ligação na aplicação
# def fazPedidoConvite(
#         sUdpOrigem: socket,
#         destIp: str,
#         destPorta: str,
#         meuUserName: str,
#         meuIp: int,
#         minhaPorta: int):
#     """Envia o convite de ligação para o endereco de destino"""
#     raise NotImplementedError()
#     tipoCabecalho = MensagensLigacao.CONVITE
#     cabecalho = f'{tipoCabecalho.value.cod} {tipoCabecalho.value.description}'
#     # TODO - enviar as informações necessárias ao corpa da mensagem
#     corpo = f'\n{meuUserName}\n{meuIp}\n{minhaPorta}'
#     mensagemCompleta = f'{cabecalho}{corpo}'
#     Transmissao.enviaBytes_UdpTimeout(
#         socket=sUdpOrigem,
#         msg=mensagemCompleta.encode('UTF8'))

def fazPedidoConvite(
        sUdp: socket,
        destIp: str,
        destPorta: int,
        meuUsername: str,
        minhaPortaUdp: int):
    """Envia o convite de ligação para o endereco de destino"""
    tipoCabecalho = MensagensLigacao.CONVITE
    cabecalho = f'{tipoCabecalho.value.cod} {tipoCabecalho.value.description}'
    # TODO - enviar as informações necessárias ao corpa da mensagem
    corpo = f'\n{meuUsername}\n{minhaPortaUdp}'
    mensagemCompleta = f'{cabecalho}{corpo}'
    mensagemCompletaBytes = f'{cabecalho}{corpo}'.encode('UTF8')
    TransmissaoUdp.enviaBytes(
        sUdp,
        destIp,
        destPorta,
        mensagemCompletaBytes)
    return mensagemCompleta

def fazRespostaConvite(
        sUdp: socket,
        destIp: str,
        destPorta: int,
        conviteAceito: bool):
    """Responde a solicitação do convite de ligação"""
    tipoCabecalho = MensagensLigacao.CONVITE_ACEITO if conviteAceito else MensagensLigacao.CONVITE_REJEITADO
    cabecalho = f'{tipoCabecalho.value.cod} {tipoCabecalho.value.description}'
    corpo = ''
    mensagemCompleta = f'{cabecalho}{corpo}'
    mensagemCompletaBytes = f'{cabecalho}{corpo}'.encode('UTF8')
    TransmissaoUdp.enviaBytes(
        sUdp,
        destIp,
        destPorta,
        mensagemCompletaBytes)
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
    mensagemCompletaBytes = f'{cabecalho}{corpo}'.encode('UTF8')
    TransmissaoUdp.enviaBytes(
        sUdp,
        destIp,
        destPorta,
        mensagemCompletaBytes)
    return mensagemCompleta


# def enviaPacoteAudio(
#         sUdp: socket,
#         destIp: str,
#         destPorta: int,
#         bytesEnviar: bytes,
#         nPacote: int):
#     tipoCabecalho = MensagensLigacao.PACOTE_AUDIO
#     cabecalho = f'{tipoCabecalho.value.cod} {tipoCabecalho.value.description}'.encode('UTF-8')
#     corpo = f'\n{nPacote}\n'.encode('UTF-8') + bytesEnviar
#     mensagemCompleta = f'{cabecalho.decode("UTF-8")}\n{sum(bytesEnviar)}'
#     mensagemCompletaBytes = cabecalho + corpo
#     TransmissaoUdp.enviaBytes(
#         sUdp,
#         destIp,
#         destPorta,
#         mensagemCompletaBytes)
#     print(bytesEnviar)
#     return mensagemCompleta

def enviaPacoteAudio(
        sUdp: socket,
        destIp: str,
        destPorta: int,
        bytesEnviar: bytes,
        nPacote: int):
    tipoCabecalho = MensagensLigacao.PACOTE_AUDIO
    cabecalho = f'{tipoCabecalho.value.cod} {tipoCabecalho.value.description}'.encode('UTF-8')
    corpo = f'\n{nPacote}\n'.encode('UTF-8') + bytesEnviar
    mensagemCompleta = f'{cabecalho.decode("UTF-8")}\n{sum(bytesEnviar)}'
    mensagemCompletaBytes = cabecalho + corpo
    TransmissaoUdp.enviaBytes(
        sUdp,
        destIp,
        destPorta,
        mensagemCompletaBytes)
    # print('==>', bytesEnviar)
    return mensagemCompleta

def recebeMensagemUdp(sUdp: socket) -> Tuple[str,int,str,Union[str, Tuple[int, bytes]]]:
    """
    Função padrão para receber o cabeçalho, o corpo, o endereco de origem, e a
    porta de uma transmissão UDP da aplicação

    Retorna: (endereco, porta, cabecalho, corpo)
    """
    endOrigem, portaOrigem, cabecalho, corpo = ('', 0, '', '')
    endOrigem, portaOrigem, msgBytes = TransmissaoUdp.recebeBytes(sUdp)
    if msgBytes.startswith(MensagensLigacao.PACOTE_AUDIO.value.cod.encode('ASCII')):
        cabecalho, _, corpo = msgBytes.partition(b'\n')
        nPacote, _, audio = corpo.partition(b'\n')
        corpo = (int(nPacote.decode('UTF-8')), audio)
        cabecalho = cabecalho.decode('UTF-8')
        # print('<==', audio)
    else:
        msgStr = msgBytes.decode('UTF-8')
        cabecalho, _, corpo = msgStr.partition('\n')
    return (endOrigem, portaOrigem, cabecalho, corpo)
