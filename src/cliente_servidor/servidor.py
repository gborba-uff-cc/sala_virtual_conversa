import socket
import threading
from enum import Enum
from io import SEEK_END, StringIO
from typing import Dict, NamedTuple, Tuple

import src.aplicacao.mensagens_aplicacao as ma
from src.util.caixa import Caixa
from src.util.maquina_estados import *
from src.util.mutex import Mutex


class LinhaTabelaRegistro(NamedTuple):
    nome: str
    ip: str
    porta: str


class Servidor():
    def __init__(self, endereco, porta) -> None:
        self._endereco = endereco
        self._porta = porta
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._aceitandoConexoes = True
        self._clientesRegistrados = Mutex({})

    def _processaConexao(self, sConexao: socket.socket, endCliente) -> None:
        """
        Função que trata de cada conexão estabeecida com o servidor;

        Essa função é executada para cada conexão em uma thread separada
        """
        try:
            processador = geraMaquinaServidor()
            processador.executa(
                maquinaEstados=processador,
                servidor=self,
                socketConexao=sConexao,
                enderecoCliente=endCliente,
                strMsg=Caixa(''))
        except Exception as e:
            raise e
        finally:
            sConexao.close()

    def comecaServir(self) -> None:
        # evitando reexecucao ao metodo se o servidor ja estiver rodando
        if not self._aceitandoConexoes:
            self._aceitandoConexoes = True
            threading.Thread(target=self._comecaServir).start()

    def _comecaServir(self):
        # self.escreveLog('',escreverEmStdOut=True)
        self.escreveLog('Servidor começou a aceitar novas conexões',
                        escreverEmStdOut=True, escreverEmLog=True)
        self.escreveLog('Esperando uma nova conexao...', escreverEmStdOut=True)
        while self._aceitandoConexoes:
            try:
                socketConexao, enderecoCliente = self._socket.accept()
                self.escreveLog('\nNova conexão de: {}'.format(
                    enderecoCliente), escreverEmStdOut=True)
                socketConexao.setblocking(True)
                novaThread = threading.Thread(
                    target=self._processaConexao,
                    args=(socketConexao, enderecoCliente))
                novaThread.start()
                # threading.enumerate()
                self.escreveLog('Esperando nova conexao...',
                                escreverEmStdOut=True)
            except BlockingIOError as be:
                # "Resource temporarily unavailable" => ninguem tentou se conectar
                if be.errno == 11:
                    pass
                else:
                    raise be
            except RuntimeError as re:
                self.escreveLog(re, escreverEmStdOut=True)
                raise re
        self.escreveLog('Servidor parou de aceitar novas conexões',
                        escreverEmStdOut=True, escreverEmLog=True)

    def deixaServir(self):
        self._aceitandoConexoes = False

    def fechaSocket(self):
        self._aceitandoConexoes = False
        self._socket.close()

# ==============================================================================
    def consultaRegistro(self, nome: str):
        """
        Consulta e retorna uma linha da tabela de registro se tiver
        encontrado o nome desejado, retorna None no caso contrário
        """
        encontrou = False
        valRetornado = None
        # faz o lock e release na tabela de registro
        with self._clientesRegistrados.lock:
            # valor retornado sera o nome endereço e
            if isinstance(self._clientesRegistrados.data, dict):
                if nome in self._clientesRegistrados.data:
                    valRetornado = self._clientesRegistrados.data[nome]
        return valRetornado

    def cadastraCliente(self, nome, ip, porta):
        """Tenta incluir uma linha na tabela de clientes registrados"""
        cadastrou = False
        with self._clientesRegistrados.lock:
            if isinstance(self._clientesRegistrados.data, dict):
                # acrescenta linha na tabela de registro se o nome ainda não existe
                if nome not in self._clientesRegistrados.data:
                    # redundante, mas flexivel
                    self._clientesRegistrados.data[nome] = LinhaTabelaRegistro(
                        nome=nome, ip=ip, porta=str(porta))
                    tabela = '----------------------------- Clientes Registrados -----------------------------\n'
                    tabela += '|{0: ^52.52}|{1: ^17.17}|{2: ^7.7}|\n'.format(
                        'Nome', 'Endereco IP', 'Porta')
                    tabela += '|------------------------------------------------------------------------------|\n'
                    for k, v in self._clientesRegistrados.data.items():
                        tabela += '|{0: <52.52}|{1:^17.17}|{2:^7.7}|\n'.format(
                            v.nome, v.ip, v.porta)
                    tabela += '--------------------------------------------------------------------------------'
                    self.escreveLog(tabela, escreverEmLog=True)
                    cadastrou = True
        return cadastrou

    def descadastraCliente(self, ip, porta):
        """Remove uma entrada da tabela de clientes registrados"""
        with self._clientesRegistrados.lock:
            if isinstance(self._clientesRegistrados.data, dict):
                nome = None
                for _, v in self._clientesRegistrados.data.items():
                    if v.ip == ip and v.porta == str(porta):
                        nome = v.nome
                        break
                self._clientesRegistrados.data.pop(nome, None)

    def escreveLog(self, *valores, escreverEmStdOut: bool = False, escreverEmLog: bool = False, separador=' ', terminador='\n', flush=False):
        """usando print"""
        if escreverEmLog:
            with self._streamLog.lock:
                # teste para remover warning
                if isinstance(self._streamLog.data, StringIO):
                    # forcando append
                    self._streamLog.data.seek(0, SEEK_END)
                    print(*valores, file=self._streamLog.data,
                          sep=separador, end=terminador, flush=flush)
        if escreverEmStdOut:
            print(*valores)

    @property
    def streamLog(self):
        return self._streamLog

    def clearLog(self):
        """Deve adquirir o lock antes de descartar a stream de texto"""
        self._streamLog = Mutex(StringIO())

# ==============================================================================
    def recebeMensagemQualquer(self, socketConexao: socket.socket):
        retorno = ma.recebePedidoOuResposta(socketConexao)
        self.escreveLog(
            ('{}\n{}' if retorno[-1] else '{}').format(retorno[0], retorno[1]), escreverEmLog=True)
        return retorno

    def processaRegistro(self, socketConexao: socket.socket, cabecalhoCorpo: Tuple[str, str], enderecoCliente: Tuple[str, int]):
        registrou = False
        _, corpo = cabecalhoCorpo
        if corpo:
            nome = corpo
            registrou = self.cadastraCliente(nome, *enderecoCliente)
        else:
            registrou = False

        retorno = ma.fazRespostaPedidoRegistro(
            sConexao=socketConexao, registrou=registrou)
        self.escreveLog(retorno, escreverEmLog=True)

    def processaConsulta(self, socketConexao: socket.socket, cabecalhoCorpo: Tuple[str, str]):
        cabecalho, corpo = cabecalhoCorpo
        if corpo:
            nome = corpo
            encontrado = self.consultaRegistro(nome)
            retorno = None
            if isinstance(encontrado, LinhaTabelaRegistro):
                retorno = ma.fazRespostaPedidoConsulta(sConexao=socketConexao, encontrou=bool(
                    encontrado), ip=encontrado.ip, porta=encontrado.porta)
            elif encontrado is None:
                retorno = ma.fazRespostaPedidoConsulta(
                    sConexao=socketConexao, encontrou=False, ip='', porta='')
            self.escreveLog(retorno, escreverEmLog=True)

    def processaEncerramento(self, enderecoCliente: Tuple[str, int]):
        self.descadastraCliente(*enderecoCliente)

# ==============================================================================


class PossiveisEstadosMaquina(Enum):
    MENSAGEM_QUALQUER = 'mensagem_qualquer',
    REGISTO = 'registo'
    REGISTO_EXITO = 'registo_exito'
    REGISTO_FALHA = 'registo_falha'
    CONSULTA = 'consulta'
    CONSULTA_EXITO = 'consulta_exito'
    CONSULTA_FALHA = 'consulta_falha'
    ENCERRAMENTO = 'encerramento'
    FINALIZADO = 'finalizado'


class ProcessadorRequisicoes():
    @classmethod
    def geraProcessador(cls) -> MaquinaEstados:
        maquina = MaquinaEstados(
            PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
            PossiveisEstadosMaquina.FINALIZADO)

        maquina.adicionaEstado(
            # identificador do estado
            PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
            # definicao do estado
            EstadosMaquina(
                funcaoAoExecutar=cls.servidorProcessaMensagemQualquer))
        maquina.adicionaTransicao(
            # estado de origem
            PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
            # sinal de transicao (vou sinalizar com o nome do estado que quero ir)
            PossiveisEstadosMaquina.REGISTO,
            # estado de destino
            PossiveisEstadosMaquina.REGISTO)
        maquina.adicionaTransicao(
            PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
            PossiveisEstadosMaquina.CONSULTA,
            PossiveisEstadosMaquina.CONSULTA)
        maquina.adicionaTransicao(
            PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
            PossiveisEstadosMaquina.ENCERRAMENTO,
            PossiveisEstadosMaquina.ENCERRAMENTO)

        maquina.adicionaEstado(
            PossiveisEstadosMaquina.REGISTO,
            EstadosMaquina(
                funcaoAoExecutar=cls.servidorProcessaRegistro))
        maquina.adicionaTransicao(
            PossiveisEstadosMaquina.REGISTO,
            PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
            PossiveisEstadosMaquina.MENSAGEM_QUALQUER)

        maquina.adicionaEstado(
            PossiveisEstadosMaquina.CONSULTA,
            EstadosMaquina(
                funcaoAoExecutar=cls.servidorProcessaConsulta))
        maquina.adicionaTransicao(
            PossiveisEstadosMaquina.CONSULTA,
            PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
            PossiveisEstadosMaquina.MENSAGEM_QUALQUER)

        maquina.adicionaEstado(
            PossiveisEstadosMaquina.ENCERRAMENTO,
            EstadosMaquina(
                funcaoAoExecutar=cls.servidorProcessaEncerramento))
        maquina.adicionaTransicao(
            PossiveisEstadosMaquina.ENCERRAMENTO,
            PossiveisEstadosMaquina.FINALIZADO,
            PossiveisEstadosMaquina.FINALIZADO)

        maquina.adicionaEstado(
            PossiveisEstadosMaquina.FINALIZADO,
            EstadosMaquina())

        maquina.confereMaquina()
        return maquina

    @classmethod
    def servidorProcessaMensagemQualquer(cls, *args, **kwargs):
        maquinaEstados: MaquinaEstados = kwargs['maquinaEstados']
        servidor: Servidor = kwargs['servidor']
        socketConexao: socket.socket = kwargs['socketConexao']

        cabecalho, _ = msg = servidor.recebeMensagemQualquer(socketConexao)
        kwargs['strMsg'].data = msg

        # decide para qual estado ir e transiciona
        if cabecalho.startswith(ma.MensagensAplicacao.REGISTO.value.cod):
            maquinaEstados.processaSinal(PossiveisEstadosMaquina.REGISTO)
        elif cabecalho.startswith(ma.MensagensAplicacao.CONSULTA.value.cod):
            maquinaEstados.processaSinal(PossiveisEstadosMaquina.CONSULTA)
        elif cabecalho.startswith(ma.MensagensAplicacao.ENCERRAMENTO.value.cod):
            maquinaEstados.processaSinal(PossiveisEstadosMaquina.ENCERRAMENTO)
        else:
            # TODO - criar estado para codigo não reconhecido
            pass

    @classmethod
    def servidorProcessaRegistro(cls, *args, **kwargs):
        maquinaEstados: MaquinaEstados = kwargs['maquinaEstados']
        msg: Tuple[str, str] = kwargs['strMsg'].data
        servidor: Servidor = kwargs['servidor']
        socketConexao: socket.socket = kwargs['socketConexao']
        enderecoCliente: Tuple[str, int] = kwargs['enderecoCliente']

        servidor.processaRegistro(
            socketConexao=socketConexao, cabecalhoCorpo=msg, enderecoCliente=enderecoCliente)

        maquinaEstados.processaSinal(PossiveisEstadosMaquina.MENSAGEM_QUALQUER)

    @classmethod
    def servidorProcessaConsulta(cls, *args, **kwargs):
        maquinaEstados: MaquinaEstados = kwargs['maquinaEstados']
        msg: Tuple[str, str] = kwargs['strMsg'].data
        servidor: Servidor = kwargs['servidor']
        socketConexao: socket.socket = kwargs['socketConexao']

        servidor.processaConsulta(
            socketConexao=socketConexao, cabecalhoCorpo=msg)

        maquinaEstados.processaSinal(PossiveisEstadosMaquina.MENSAGEM_QUALQUER)

    @classmethod
    def servidorProcessaEncerramento(cls, *args, **kwargs):
        maquinaEstados: MaquinaEstados = kwargs['maquinaEstados']
        servidor: Servidor = kwargs['servidor']
        enderecoCliente: Tuple[str, int] = kwargs['enderecoCliente']

        servidor.processaEncerramento(enderecoCliente=enderecoCliente)

        maquinaEstados.processaSinal(PossiveisEstadosMaquina.FINALIZADO)
