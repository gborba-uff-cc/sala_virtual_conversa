from socket import socket

from enum import Enum
from typing import NamedTuple

from src.util.transmissao import Transmissao

class MensagemAplicacao(NamedTuple):
    cod: str
    description: str

class MensagensAplicacao(Enum):
    REGISTO = MensagemAplicacao('1', '')
    REGISTO_EXITO = MensagemAplicacao('2', '')
    REGISTO_FALHA = MensagemAplicacao('3', '')
    CONSULTA = MensagemAplicacao('4', '')
    CONSULTA_EXITO = MensagemAplicacao('5', '')
    CONSULTA_FALHA = MensagemAplicacao('6', '')
    ENCERRAMENTO = MensagemAplicacao('7', '')

def fazPedidoRegistro(sConexao: socket, nomeDesejado: str):
    Transmissao.enviaBytes(
        socket=sConexao,
        msg=(
            MensagensAplicacao.REGISTO.value.cod +
            ' ' +
            MensagensAplicacao.REGISTO.value.description +
            '\n' +
            nomeDesejado).encode('UTF8'))
    msgBytes = Transmissao.recebeBytes(sConexao)
    return msgBytes.decode('UTF8')

# def recebePedidoRegistro(sConexao):
#     msgBytes = Transmissao.recebeBytes(sConexao)
#     msgStr = msgBytes.decode('UTF8')
#     return {'cabecalho': msgStr.partition('\n')[0], 'corpo': msgStr.partition('\n')[-1:]}

def fazPedidoConsulta(sConexao: socket, nomeDesejado: str):
    Transmissao.enviaBytes(
        socket=sConexao,
        msg=(
            MensagensAplicacao.CONSULTA.value.cod +
            ' ' +
            MensagensAplicacao.CONSULTA.value.description +
            '\n' +
            nomeDesejado).encode('UTF8'))
    msgBytes = Transmissao.recebeBytes(sConexao)
    return msgBytes.decode('UTF8')

# def recebePedidoConsulta(sConexao):
#    pass

def fazPedidoEncerramento(sConexao: socket):
    Transmissao.enviaBytes(
        socket=sConexao,
        msg=(
            MensagensAplicacao.ENCERRAMENTO.value.cod +
            ' ' +
            MensagensAplicacao.ENCERRAMENTO.value.description).encode('UTF8'))

# def recebePedidoEncerramento(sConexao):
#    pass

# TODO - mover parte da lógica da maquinaServidor, que enviam e recebem
# mensagens, para cá
