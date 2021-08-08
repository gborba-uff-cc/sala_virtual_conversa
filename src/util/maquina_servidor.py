import socket
from enum import Enum
from typing import Tuple

import src.aplicacao.mensagens_aplicacao as ma
from src.util.maquina_estados import EstadosMaquina, MaquinaEstados
from src.util.transmissao import Transmissao


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

    msg = cabecalho, _ = ma.recebePedidoOuResposta(socketConexao)
    kwargs['strMsg'].data = msg

    # decide para qual estado ir e transiciona para o estado
    if cabecalho.startswith(ma.MensagensAplicacao.REGISTO.value.cod):
        maquinaEstados.processaSinal(PossiveisEstadosMaquina.REGISTO)
    elif cabecalho.startswith(ma.MensagensAplicacao.CONSULTA.value.cod):
        maquinaEstados.processaSinal(PossiveisEstadosMaquina.CONSULTA)
    elif cabecalho.startswith(ma.MensagensAplicacao.ENCERRAMENTO.value.cod):
        maquinaEstados.processaSinal(PossiveisEstadosMaquina.ENCERRAMENTO)
    else:
        # TODO - criar estado para codigo não reconhecido
        pass


def servidorProcessaRegistro(*args, **kwargs):
    maquinaEstados: MaquinaEstados = kwargs['maquinaEstados']
    msg: Tuple[str, str] = kwargs['strMsg'].data
    servidor = kwargs['servidor']
    socketConexao: socket.socket = kwargs['socketConexao']
    enderecoCliente: Tuple[str, int] = kwargs['enderecoCliente']

    registrou = False
    _, corpo = msg
    if corpo:
        nome = corpo
        encontrado = servidor.consultaRegistro(nome)
        if encontrado:
            registrou = False
        else:
            servidor.cadastraCliente(nome, *enderecoCliente)
            registrou = True
    else:
        registrou = False

    ma.fazRespostaPedidoRegistro(sConexao=socketConexao, registrou=registrou)

    maquinaEstados.processaSinal(PossiveisEstadosMaquina.MENSAGEM_QUALQUER)


def servidorProcessaConsulta(*args, **kwargs):
    maquinaEstados: MaquinaEstados = kwargs['maquinaEstados']
    msg: Tuple[str, str] = kwargs['strMsg'].data
    servidor = kwargs['servidor']
    socketConexao: socket.socket = kwargs['socketConexao']

    cabecalho, corpo = msg
    if corpo:
        nome = corpo
        encontrado = servidor.consultaRegistro(nome)
        ma.fazRespostaPedidoConsulta(sConexao=socketConexao, encontrou=bool(
            encontrado), ip=encontrado.ip, porta=encontrado.porta)

    maquinaEstados.processaSinal(PossiveisEstadosMaquina.MENSAGEM_QUALQUER)


def servidorProcessaEncerramento(*args, **kwargs):
    maquinaEstados: MaquinaEstados = kwargs['maquinaEstados']
    servidor = kwargs['servidor']
    enderecoCliente: Tuple = kwargs['enderecoCliente']

    servidor.descadastraCliente(*enderecoCliente)

    maquinaEstados.processaSinal(PossiveisEstadosMaquina.FINALIZADO)
