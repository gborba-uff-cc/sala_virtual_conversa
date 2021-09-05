from enum import Enum
from socket import socket
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


def recebePedidoOuResposta(sConexao):
    """Função padrão para receber o cabeçalho e o corpo de uma transmissão da aplicação"""
    msgBytes = Transmissao.recebeBytes(sConexao)
    msgStr = msgBytes.decode('UTF8')
    cabecalho, _, corpo = msgStr.partition('\n')
    return (cabecalho, corpo)
