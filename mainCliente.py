import socket
from src.util.transmissao import Transmissao

SERVIDOR_ENDERECO = 'localhost'
# SERVIDOR_PORTA    = 49152
SERVIDOR_PORTA = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVIDOR_ENDERECO, SERVIDOR_PORTA))
f = 'estou testando envio ]]} com} e ~sem flags e escapes }~'
print(f)
Transmissao.enviaBytes(s, f.encode('UTF8'))
f = Transmissao.recebeBytes(s)
print(f.decode('UTF8'))
s.close()
