from enum import Enum
import socket
import threading
from typing import Dict, NamedTuple, Tuple

from src.util.transmissao import Transmissao
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

    def _processaConexao(self, socketConexao: socket.socket, enderecoCliente) -> None:
        try:
            print(socketConexao, enderecoCliente)
            msg = Transmissao.recebeBytes(socketConexao)
            print(msg)
            msg = msg.decode('UTF8').upper().encode('UTF8')
            Transmissao.enviaBytes(socketConexao, msg)
        except Exception as e:
            print(e)
        finally:
            print('processaConexao:finally')
            socketConexao.close()

    def _consultaRegistro(self, nome: str) -> Tuple[bool, LinhaTabelaRegistro]:
        nome, ip, porta = ('', '', '')
        encontrou = False

        # faz o lock na tabela de registro
        # TODO
        # with self._clientesRegistrados.lock:
        #     if nome in self._clientesRegistrados.data:
        #         pass

        # faz o unlock na tabela de registro
        # TODO
        return (encontrou, LinhaTabelaRegistro(nome, ip, porta))
