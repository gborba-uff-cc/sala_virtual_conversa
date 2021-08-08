import socket

import src.aplicacao.mensagens_aplicacao as ma
from src.util.transmissao import Transmissao


class Cliente():
    def __init__(self) -> None:
        self._socketConectado = False
        self._socketConexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def conectaAoServidor(self, enderecoServidor: str, portaServidor: int):
        if self._socketConectado:
            return
        self._socketConexao.connect((enderecoServidor, portaServidor))
        self._socketConectado = True

    def fazPedidoRegistro(self, nomeDesejado: str):
        return ma.fazPedidoRegistro(self._socketConexao, nomeDesejado)

    def fazPedidoConsulta(self, nomeDesejado: str):
        return ma.fazPedidoConsulta(self._socketConexao, nomeDesejado)

    def fazPedidoEncerramento(self):
        ma.fazPedidoEncerramento(self._socketConexao)
        self._socketConexao.close()
        self._socketConectado = False
