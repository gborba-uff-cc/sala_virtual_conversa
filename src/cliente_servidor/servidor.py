import socket
import threading
from enum import Enum
from typing import Dict, NamedTuple, Tuple

from src.util.caixa import Caixa
from src.util.maquina_servidor import geraMaquinaServidor
from src.util.mutex import Mutex
from src.util.transmissao import Transmissao


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
                    print('\n--------------------')
                    for k, v in self._clientesRegistrados.data.items():
                        print(v.nome, '(', v.ip, ':', v.porta, ')')
                    print('--------------------\n')
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

