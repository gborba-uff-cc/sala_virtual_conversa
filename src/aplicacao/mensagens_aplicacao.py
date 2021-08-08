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


def fazPedidoRegistro(sConexao: socket, nomeDesejado: str):
    """Solicita o registro do nome no servidor"""
    tipoCabecalho = MensagensAplicacao.REGISTO
    cabecalho = tipoCabecalho.value.cod + ' ' + tipoCabecalho.value.description
    corpo = nomeDesejado
    Transmissao.enviaBytes(
        socket=sConexao,
        msg=(cabecalho + '\n' + corpo).encode('UTF8'))


def fazRespostaPedidoRegistro(sConexao, registrou: bool):
    """Responde a solicitação de registro do nome feita pelo cliente"""
    tipoCabecalho = MensagensAplicacao.REGISTO_EXITO if registrou else MensagensAplicacao.REGISTO_FALHA
    cabecalho = tipoCabecalho.value.cod + ' ' + tipoCabecalho.value.description
    Transmissao.enviaBytes(
        socket=sConexao,
        msg=cabecalho.encode('UTF8'))


def fazPedidoConsulta(sConexao: socket, nomeDesejado: str):
    """Solicita a consulta de um nome"""
    tipoCabecalho = MensagensAplicacao.CONSULTA
    cabecalho = tipoCabecalho.value.cod + ' ' + tipoCabecalho.value.description
    corpo = nomeDesejado
    Transmissao.enviaBytes(
        socket=sConexao,
        msg=(cabecalho + '\n' + corpo).encode('UTF8'))


def fazRespostaPedidoConsulta(sConexao, encontrou: bool, ip: str = '', porta: str = ''):
    """Responde a solicitação de consulta ao nome feita pelo cliente"""
    tipoCabecalho = MensagensAplicacao.CONSULTA_EXITO if encontrou else MensagensAplicacao.CONSULTA_FALHA
    cabecalho = tipoCabecalho.value.cod + ' ' + tipoCabecalho.value.description
    corpo = (ip + ' ' + porta) if encontrou else ''
    Transmissao.enviaBytes(
        socket=sConexao,
        msg=(cabecalho + '\n' + corpo).encode('UTF8'))


def fazPedidoEncerramento(sConexao: socket):
    """Clinte informa que quer encerrar a conexão com o servidor"""
    tipoCabecalho = MensagensAplicacao.ENCERRAMENTO
    cabecalho = tipoCabecalho.value.cod + ' ' + tipoCabecalho.value.description
    Transmissao.enviaBytes(
        socket=sConexao,
        msg=cabecalho.encode('UTF8'))


def recebePedidoOuResposta(sConexao):
    """Função padrão para receber o cabeçalho e o corpo de uma transmissão da aplicação"""
    msgBytes = Transmissao.recebeBytes(sConexao)
    msgStr = msgBytes.decode('UTF8')
    cabecalho, _, corpo = msgStr.partition('\n')
    return (cabecalho, corpo)
