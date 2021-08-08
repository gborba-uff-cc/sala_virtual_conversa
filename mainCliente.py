import socket
from src.cliente_servidor.cliente import Cliente

# TODO - endereco deve ser pego pela interface com o usuario
servidor_endereco = 'localhost'
servidor_porta = 5000

c = Cliente()
c.conectaAoServidor(servidor_endereco, servidor_porta)
strRetornado = c.fazPedidoRegistro('gabrielborba')
print(strRetornado)
strRetornado = c.fazPedidoConsulta('gabrielborba')
print(strRetornado)
c.fazPedidoEncerramento()
