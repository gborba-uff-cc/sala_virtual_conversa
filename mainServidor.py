from src.cliente_servidor.servidor import Servidor


def main():
    SERVIDOR_ENDERECO = 'localhost'
    SERVIDOR_PORTA = 5000
    # SERVIDOR_PORTA    = 49152
    servidor = Servidor(SERVIDOR_ENDERECO, SERVIDOR_PORTA)
    servidor.comecaServir()

if __name__ == '__main__':
    main()
