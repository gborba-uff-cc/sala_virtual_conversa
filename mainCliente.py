import socket
from src.cliente_servidor.cliente import Cliente
import time

# TODO - interface do usuario
# TODO - endereco deve ser pego pela interface com o usuario
servidor_endereco = 'localhost'
servidor_porta = 5000

c = Cliente()
c.conectaAoServidor(servidor_endereco, servidor_porta)
retorno = c.realizaPedidoRegistro('gabrielborba')
print(retorno)
time.sleep(1)
retorno = c.realizaPedidoConsulta('gabrielborba')
print(retorno)
time.sleep(1)
c.realizaPedidoEncerramento()
