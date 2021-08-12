import socket
import threading
from enum import Enum
from io import SEEK_END, StringIO
from typing import Dict, NamedTuple, Tuple, Union

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
        # socket.AF_INET -> familia de enderecos IPv4
        # socket.AF_INET6 -> familia de enderecos IPv6
        # socket.SOCK_STREAM -> socket do tipo TCP
        # socket.SOCK_DGRAM -> socket do tipo UDP
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._aceitandoConexoes = False
        self._clientesRegistrados = Mutex({})
        self._streamLog = Mutex(StringIO())
        self._socket.setblocking(False)
        self._socket.bind((self._endereco, self._porta))
        self._socket.listen(3)

    @property
    def enderecoAtual(self):
        ip, porta = self._socket.getsockname()
        return (str(ip), str(porta))

    @property
    def aceitandoConexoes(self):
        return self._aceitandoConexoes

    def _processaConexao(self, sConexao: socket.socket, endCliente) -> None:
        """
        Função que trata de cada conexão estabelecida com o servidor;

        Essa função é executada para cada conexão em uma thread separada
        """
        try:
            processador = ProcessadorRequisicoes.geraProcessador()
            processador.executa(
                maquinaEstados=processador,
                servidor=self,
                socketConexao=sConexao,
                enderecoCliente=endCliente,
                strMsg=Caixa(''))
        except RuntimeError as re:
            raise re
        finally:
            sConexao.close()

    def comecaServir(self) -> None:
        # evitando reexecucao do metodo se o servidor ja estiver rodando
        if not self._aceitandoConexoes:
            self._aceitandoConexoes = True
            threading.Thread(target=self._comecaServir).start()

    def _comecaServir(self):
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
                # NOTE - "[ERRNO 11] Resource temporarily unavailable" => ninguem
                # tentou se conectar
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
    def consultaRegistro(self, nome: str) -> Union[LinhaTabelaRegistro, None]:
        """
        Consulta e retorna uma linha da tabela de registro se tiver
        encontrado o nome desejado, retorna None caso contrário
        """
        valRetornado = None
        # NOTE - usando with para fazer o lock e release na tabela de registro
        with self._clientesRegistrados.lock:
            # NOTE - isinstance está servindo para remover warnings
            if isinstance(self._clientesRegistrados.data, dict):
                if nome in self._clientesRegistrados.data:
                    valRetornado = self._clientesRegistrados.data[nome]
            else:
                self.escreveLog(
                    '>>> servidor.consultaRegistro: a implementação da tabela de registro não é a esperada',
                    escreverEmStdOut=True, escreverEmLog=True)
        # NOTE - valor retornado sera a linha da tabela de usuarios registrados ou None
        return valRetornado

    def cadastraCliente(self, nome, ip, porta):
        """Tenta incluir uma linha na tabela de clientes registrados"""
        nomeString = str(nome)
        ipString = str(ip)
        portaString = str(porta)
        jaCadastrado = False
        # NOTE - usando with para fazer o lock e release na tabela de registro
        with self._clientesRegistrados.lock:
            # NOTE - isinstance está servindo para remover warnings
            if isinstance(self._clientesRegistrados.data, dict):
                # NOTE - verifica se o nome já está em uso e se a conexao ainda não
                # registrou um nome
                nomeExiste = nomeString in self._clientesRegistrados.data
                socketCadastrado = False
                for linhaTabela in self._clientesRegistrados.data.values():
                    if linhaTabela.ip == ipString and linhaTabela.porta == portaString:
                        socketCadastrado = True
                        break
                jaCadastrado = nomeExiste or socketCadastrado
                # NOTE - adiciona linha na tabela de registro se nome ainda nao existe
                # e a conexao ainda não se registrou
                if not jaCadastrado:
                    # NOTE - a chave tambem constar no valor eh redundante mas flexivel
                    self._clientesRegistrados.data[nome] = LinhaTabelaRegistro(
                        nome=nome, ip=ip, porta=str(porta))
                    self._escreveTabelaUsuariosNoLog()
            else:
                self.escreveLog(
                    '>>> servidor.cadastraCliente: a implementação da tabela de registro não é a esperada',
                    escreverEmStdOut=True, escreverEmLog=True)
            # NOTE - se ja cadastrado entao o cadastro nao foi feito;
            # retona True se foi feito o cadastro, False no caso contrario
            return not jaCadastrado
        return False

    def descadastraCliente(self, ip, porta):
        """Remove uma entrada da tabela de clientes registrados"""
        ipString = str(ip)
        portaString = str(porta)
        # NOTE - usando with para fazer o lock e release na tabela de registro
        with self._clientesRegistrados.lock:
            # NOTE - isinstance está servindo para remover warnings
            if isinstance(self._clientesRegistrados.data, dict):
                nome = None
                # NOTE - encontra o endereco e porta da conexao que pediu a remocao
                for _, v in self._clientesRegistrados.data.items():
                    if v.ip == ipString and v.porta == portaString:
                        nome = v.nome
                        break
                # NOTE - ao encontrar remove a linha correspondente na tabela
                self._clientesRegistrados.data.pop(nome, None)
                self._escreveTabelaUsuariosNoLog()
            else:
                self.escreveLog(
                    '>>> servidor.descadastraCliente: a implementação da tabela de registro não é a esperada',
                    escreverEmStdOut=True, escreverEmLog=True)

    def escreveLog(self, *valores, escreverEmStdOut: bool = False, escreverEmLog: bool = False, separador=' ', terminador='\n', flush=False):
        """
        Usa a função print do Python para escrever na stream de log do servidor
        e/ou na saida padrão.

        A decisão de onde os valores serão impressos fica por conta dos
        argumentos passados na chamada do método
        """
        if escreverEmLog:
            # NOTE - usando with para fazer o lock e release na stream de logs do servidor
            with self._streamLog.lock:
                # NOTE - isinstance está servindo para remover warnings
                if isinstance(self._streamLog.data, StringIO):
                    # NOTE - forcando a escrita no fim stream
                    self._streamLog.data.seek(0, SEEK_END)
                    print(*valores, file=self._streamLog.data,
                          sep=separador, end=terminador, flush=flush)
        if escreverEmStdOut:
            print(*valores, sep=separador, end=terminador, flush=flush)

    def _escreveTabelaUsuariosNoLog(self):
        """
        Método privado que

        O lock da tabela deve ser adquirido antes de utilizar esse método
        """
        # NOTE - isinstance está servindo para remover warnings
        if isinstance(self._clientesRegistrados.data, dict):
            tabela = '----------------------------- Clientes Registrados -----------------------------\n'
            tabela += '|{0: ^52.52}|{1: ^17.17}|{2: ^7.7}|\n'.format(
                'Nome', 'Endereco IP', 'Porta')
            tabela += '|------------------------------------------------------------------------------|\n'
            for k, v in self._clientesRegistrados.data.items():
                tabela += '|{0: <52.52}|{1:^17.17}|{2:^7.7}|\n'.format(
                    v.nome, v.ip, v.porta)
            tabela += '--------------------------------------------------------------------------------'
            self.escreveLog(tabela, escreverEmLog=True)

    @property
    def streamLog(self):
        """A stream que contem o log do servidor"""
        return self._streamLog

    def clearLog(self):
        """
        Descarta a stream de log

        A função/método que utilizar esse método deverá realizar o acquire e
        release do lock
        """
        self._streamLog = Mutex(StringIO())

# ==============================================================================
    # NOTE - Metodos para atender a aplicacao
    def recebeMensagemQualquer(self, socketConexao: socket.socket):
        """
        Recebe uma mensagem qualquer da aplicação qeu foi recebida do cliente
        """
        retorno = ma.recebePedidoOuResposta(socketConexao)
        self.escreveLog(
            ('{}\n{}' if retorno[-1] else '{}').format(retorno[0], retorno[1]), escreverEmLog=True)
        return retorno

    def processaRegistro(self, socketConexao: socket.socket, cabecalhoCorpo: Tuple[str, str], enderecoCliente: Tuple[str, int]):
        """
        Manipula o pedido de registro recebido do cliente
        """
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
        """
        Manipula o pedido de consulta recebido do cliente
        """
        cabecalho, corpo = cabecalhoCorpo
        if corpo:
            nome = corpo
            encontrado = self.consultaRegistro(nome)
            retorno = ''
            if encontrado is None:
                retorno = ma.fazRespostaPedidoConsulta(
                    sConexao=socketConexao, encontrou=False, ip='', porta='')
            else:
                retorno = ma.fazRespostaPedidoConsulta(sConexao=socketConexao, encontrou=bool(
                    encontrado), ip=encontrado.ip, porta=encontrado.porta)
            self.escreveLog(retorno, escreverEmLog=True)

    def processaEncerramento(self, enderecoCliente: Tuple[str, int]):
        """
        Manipula a mensagem de encerramento do cliente
        """
        self.descadastraCliente(*enderecoCliente)

# ==============================================================================
# NOTE - montando o processador de conexões do servidor


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
    """
    'Classe estática' que gera o processador de conexões do servidor.
    """
    @classmethod
    def geraProcessador(cls) -> MaquinaEstados:
        maquina = MaquinaEstados(
            PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
            PossiveisEstadosMaquina.FINALIZADO)

        maquina.adicionaEstado(
            # NOTE - definindo o identificador do estado
            PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
            # NOTE - definindo o estado e o que ele fará
            EstadosMaquina(
                funcaoAoExecutar=cls.servidorProcessaMensagemQualquer))
        maquina.adicionaTransicao(
            # NOTE - estado de origem
            PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
            # NOTE - sinal de transicao (estarei sinalizando com o nome do estado que quero ir)
            PossiveisEstadosMaquina.REGISTO,
            # NOTE - estado de destino
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
# ==============================================================================
# NOTE - Metodos que definem o que cada estado fará

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
