from enum import Enum
import socket
import threading
from typing import Dict, NamedTuple, Tuple

from src.util.transmissao import Transmissao
from src.util.mutex import Mutex
from src.util.gerador_maquinas import geraMaquinaServidor
from src.util.caixa import Caixa

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
        # self._clientesRegistrados: Dict[str, LinhaTabelaRegistro] = {}
        # dados no mutex será a tabela (dicionario)
        self._clientesRegistrados = Mutex({})

    def comecaServir(self) -> None:
        try:
            self._socket.bind((self._endereco, self._porta))
            self._socket.listen(3)
        except Exception as e:
            print(e)
            self._socket.close()
            return

        while self._aceitandoConexoes:
            print('Esperando nova conexao...')
            socketConexao, enderecoCliente = self._socket.accept()
            print('Nova conexão de: {}'.format(enderecoCliente))

            novaThread = threading.Thread(
                target=self._processaConexao,
                args=(socketConexao, enderecoCliente))
            novaThread.start()
            # threading.enumerate()

        self._socket.close()

    def _processaConexao(self, sConexao: socket.socket, endCliente) -> None:
        try:
            # print(socketConexao, enderecoCliente)
            # msg = Transmissao.recebeBytes(socketConexao)
            # print(msg)
            # msg = msg.decode('UTF8').upper().encode('UTF8')
            # Transmissao.enviaBytes(socketConexao, msg)
            processador = geraMaquinaServidor()
            processador.executa(
                maquinaEstados=processador,
                servidor=self,
                socketConexao=sConexao,
                enderecoCliente=endCliente,
                strMsg=Caixa(''))
        except Exception as e:
            print(e)
        finally:
            sConexao.close()

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
            if nome in self._clientesRegistrados.data:
                valRetornado = (LinhaTabelaRegistro) self._clientesRegistrados.data[nome]
        return valRetornado

    def cadastraCliente(self, nome, ip, porta):
        cadastrou = False
        with self._clientesRegistrados.lock:
            # acresenta linha na tabela de registro se o nome ainda não existe
            if nome not in self._clientesRegistrados.data:
                # redundante, mas flexivel
                self._clientesRegistrados.data[nome] = LinhaTabelaRegistro(nome=nome, ip=ip, porta=porta)
                cadastrou = True
        return cadastrou


    def descadastraCliente(self, ip, porta):
        with self._clientesRegistrados.lock:
            nome = ''
            for k,v in self._clientesRegistrados.data.items():
                if v.ip == ip and v.porta == porta:
                    nome = v.nome
                    break
            self._clientesRegistrados.data.pop(nome, None)

