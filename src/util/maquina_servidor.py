from enum import Enum
import socket
from typing import Tuple
from src.aplicacao.mensagens_aplicacao import MensagensAplicacao
from src.util.transmissao import Transmissao
from src.util.maquina_estados import MaquinaEstados, EstadosMaquina
# from src.cliente_servidor.servidor import Servidor


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


def geraMaquinaServidor() -> MaquinaEstados:
    maquina = MaquinaEstados(
        PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
        PossiveisEstadosMaquina.FINALIZADO)


    maquina.adicionaEstado(
        # identificador do estado
        PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
        # definicao do estado
        EstadosMaquina(
            funcaoAoExecutar=servidorProcessaMensagemQualquer))
    maquina.adicionaTransicao(
        # estado de origem
        PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
        # sinal de transicao (vou sinalizar com o nome do estado que quero ir)
        PossiveisEstadosMaquina.REGISTO,
        # estado de destino
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
            funcaoAoExecutar=servidorProcessaRegistro))
    maquina.adicionaTransicao(
        PossiveisEstadosMaquina.REGISTO,
        PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
        PossiveisEstadosMaquina.MENSAGEM_QUALQUER)


    maquina.adicionaEstado(
        PossiveisEstadosMaquina.CONSULTA,
        EstadosMaquina(
            funcaoAoExecutar=servidorProcessaConsulta))
    maquina.adicionaTransicao(
        PossiveisEstadosMaquina.CONSULTA,
        PossiveisEstadosMaquina.MENSAGEM_QUALQUER,
        PossiveisEstadosMaquina.MENSAGEM_QUALQUER)


    maquina.adicionaEstado(
        PossiveisEstadosMaquina.ENCERRAMENTO,
        EstadosMaquina(
            funcaoAoExecutar=servidorProcessaEncerramento))
    maquina.adicionaTransicao(
        PossiveisEstadosMaquina.ENCERRAMENTO,
        PossiveisEstadosMaquina.FINALIZADO,
        PossiveisEstadosMaquina.FINALIZADO)

    maquina.adicionaEstado(
        PossiveisEstadosMaquina.FINALIZADO,
        EstadosMaquina())

    maquina.confereMaquina()
    return maquina

def servidorProcessaMensagemQualquer(*args, **kwargs):
    maquinaEstados: MaquinaEstados = kwargs['maquinaEstados']
    socketConexao: socket.socket = kwargs['socketConexao']

    msgBytes = Transmissao.recebeBytes(socketConexao)
    msg = msgBytes.decode('UTF8')
    kwargs['strMsg'].data = msg

    # decide para qual estado ir e transiciona para o estado
    if msg.startswith(MensagensAplicacao.REGISTO.value.cod):
        maquinaEstados.processaSinal(PossiveisEstadosMaquina.REGISTO)
    elif msg.startswith(MensagensAplicacao.CONSULTA.value.cod):
        maquinaEstados.processaSinal(PossiveisEstadosMaquina.CONSULTA)
    elif msg.startswith(MensagensAplicacao.ENCERRAMENTO.value.cod):
        maquinaEstados.processaSinal(PossiveisEstadosMaquina.ENCERRAMENTO)
    else:
        # TODO - criar estado para codigo não reconhecido
        pass

def servidorProcessaRegistro(*args, **kwargs):
    maquinaEstados: MaquinaEstados = kwargs['maquinaEstados']
    msg: str = kwargs['strMsg'].data
    servidor = kwargs['servidor']
    socketConexao: socket.socket = kwargs['socketConexao']
    enderecoCliente: Tuple[str, int] = kwargs['enderecoCliente']

    registrou = False
    # ler nome
    cabecalho, _, corpo = msg.partition('\n')
    if corpo:
        nome = corpo
        ip, porta = enderecoCliente
        encontrado = servidor.consultaRegistro(nome)
        if encontrado:
            registrou = False
        else:
            servidor.cadastraCliente(nome, *enderecoCliente)
            registrou = True
    else:
        registrou = False

    if registrou:
        # envia mensagem registro_exito e imprime a nova tabelas e nome foi registrado
        Transmissao.enviaBytes(
            socket=socketConexao,
            msg=(
                MensagensAplicacao.REGISTO_EXITO.value.cod +
                ' ' +
                MensagensAplicacao.REGISTO_EXITO.value.description).encode('UTF8'))
    else:
        # envia mensagem de registro_falho se nome já existia
        Transmissao.enviaBytes(
            socket=socketConexao,
            msg=(
                MensagensAplicacao.REGISTO_FALHA.value.cod +
                ' ' +
                MensagensAplicacao.REGISTO_FALHA.value.description).encode('UTF8'))

    maquinaEstados.processaSinal(PossiveisEstadosMaquina.MENSAGEM_QUALQUER)

def servidorProcessaConsulta(*args, **kwargs):
    maquinaEstados: MaquinaEstados = kwargs['maquinaEstados']
    msg: str = kwargs['strMsg'].data
    servidor = kwargs['servidor']
    socketConexao: socket.socket = kwargs['socketConexao']

    cabecalho, _, corpo = msg.partition('\n')
    if corpo:
        nome = corpo
        encontrado = servidor.consultaRegistro(nome)
        if encontrado:
            Transmissao.enviaBytes(
                socket=socketConexao,
                msg=(
                    MensagensAplicacao.CONSULTA_EXITO.value.cod +
                    ' ' +
                    MensagensAplicacao.CONSULTA_EXITO.value.description +
                    '\n' +
                    encontrado.ip +
                    '\n' +
                    encontrado.porta).encode('UTF8'))
        else:
            Transmissao.enviaBytes(
                socket=socketConexao,
                msg=(
                    MensagensAplicacao.CONSULTA_FALHA.value.cod +
                    ' ' +
                    MensagensAplicacao.CONSULTA_FALHA.value.description).encode('UTF8'))

    maquinaEstados.processaSinal(PossiveisEstadosMaquina.MENSAGEM_QUALQUER)

def servidorProcessaEncerramento(*args, **kwargs):
    maquinaEstados: MaquinaEstados = kwargs['maquinaEstados']
    servidor = kwargs['servidor']
    enderecoCliente: Tuple = kwargs['enderecoCliente']

    servidor.descadastraCliente(*enderecoCliente)

    maquinaEstados.processaSinal(PossiveisEstadosMaquina.FINALIZADO)
