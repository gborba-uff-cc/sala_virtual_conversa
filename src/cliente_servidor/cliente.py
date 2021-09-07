import socket

import src.aplicacao.mensagens_aplicacao as ma
from src.util.excepts import InvalidIpError


class Cliente():
    def __init__(self) -> None:
        self._socketConectado = False
        self._socketConexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def conectaAoServidor(self, enderecoServidor: str, portaServidor: int):
        """
        Realiza uma tentativa de conexao com o servidor da aplicação que se
        encontra no endereçoServidor e na portaServidor
        """
        if self._socketConectado:
            return
        try:
            self._socketConexao.connect((enderecoServidor, portaServidor))
            self._socketConectado = True
        except socket.gaierror:
            raise InvalidIpError


    def realizaPedidoRegistro(self, nomeDesejado: str, portaUdp: int):
        """
        Envia ao servidor uma mensagem de REGISTRO para o nome desejado;
        Recebe a resposta do servidor;

        Valor de retorno é uma dupla (tupla com tamanho dois):
            O primeiro elemento é a mensagem que foi enviada ao servidor
            O segundo elemento é uma dupla:
                O primeiro elemento é o cabecalho da mensagem recebida do servidor
                O segundo elemento é o corpo da mensagem recebida do servidor
        """
        if not self._socketConectado:
            return ('', ('', ''))
        enviado = ma.fazPedidoRegistro(self._socketConexao, nomeDesejado, portaUdp)
        recebido = ma.recebePedidoOuResposta(self._socketConexao)
        return (enviado, recebido)

    def realizaPedidoConsulta(self, nomeDesejado: str):
        """
        Envia ao servidor uma mensagem de CONSULTA para o nome desejado;
        Recebe a resposta do servidor;

        Valor de retorno é uma dupla (tupla com tamanho dois):
            O primeiro elemento é a mensagem que foi enviada ao servidor
            O segundo elemento é uma dupla:
                O primeiro elemento é o cabecalho da mensagem recebida do servidor
                O segundo elemento é o corpo da mensagem recebida do servidor
        """
        if not self._socketConectado:
            return ('', ('', ''))
        enviado = ma.fazPedidoConsulta(self._socketConexao, nomeDesejado)
        recebido = ma.recebePedidoOuResposta(self._socketConexao)
        return (enviado, recebido)

    def realizaPedidoEncerramento(self, portaUdp: int):
        """
        Envia ao servidor uma mensagem de ENCERRAMENTO para o nome desejado;
        Não recebe resposta do servidor (servidor não precisa responder mensagem
        de encerramento);
        """
        if not self._socketConectado:
            return ('', ('', ''))
        enviado = ma.fazPedidoEncerramento(self._socketConexao, portaUdp)
        self._socketConexao.close()
        self._socketConectado = False
        return enviado
