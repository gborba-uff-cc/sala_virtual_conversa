# SECTION - Objetivos da segunda parte do trabalho
# NOTE - inicializar socket UDP que será usado para a comunicao com o servidor de ligação
# NOTE - enviar uma mensagem de 'convite', a um servidor de ligação que encontra-se em um certo endereco IP e receber a 'resposta_ao_convite'
# NOTE - o 'convite' deve conter o nome de usuário, o ip e a porta utilizadas pelo socket do cliente
# NOTE - a 'resposta_ao_convite' pode ser 'rejeitado' ou 'aceito'
# NOTE - todas as mensagens trocadas devem ser logadas
# NOTE - caso 'convite'seja 'aceito', inicia a coleta e transmissão do sinal de áudio
# NOTE - caso o cliente deseje encerrar a ligação uma mensagem 'encerrar_ligação' deverá ser enviada e a transmissão do áudio deverá ser encerrado
# NOTE - caso o cliente receba 'encerrar_ligacao' ele deverá parar transmitir
# NOTE - se resposta_ao_convite for rejeitado mostrar na tela a mensagem 'usuário destino ocupado'
# !SECTION


import socket


class ClienteLigacao():

    def __init__(self):
        # usa .sendto(bytes, endereco) para enviar algo
        # usa .recvfrom(tambuffer) para receber algo; bytes, endereco
        # NOTE - criando um socket udp
        # NOTE - AF_INET indica um endereco do tipo internet;
        # NOTE - SOCK_DGRAMindica que o socket é do tipo UDP;
        sCliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

