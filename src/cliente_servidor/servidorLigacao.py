import socket

class ServidorLigacao():

    def __init__(self):
        # NOTE - criando um socket udp
        # NOTE - AF_INET indica um endereco do tipo internet;
        # NOTE - SOCK_DGRAMindica que o socket é do tipo UDP;
        sServidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
