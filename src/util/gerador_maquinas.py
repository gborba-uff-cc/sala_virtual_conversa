from enum import Enum
from src.aplicacao.mensagens_aplicacao import MensagensAplicacao
from src.util.transmissao import Transmissao
from .maquina_estados import MaquinaEstados, EstadosMaquina
from ..servidor.servidor import Servidor


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
        EstadosMaquina())
    maquina.adicionaTransicao(
        PossiveisEstadosMaquina.ENCERRAMENTO,
        PossiveisEstadosMaquina.FINALIZADO,
        PossiveisEstadosMaquina.FINALIZADO)

    maquina.confereMaquina()
    return maquina

def servidorProcessaMensagemQualquer(*args, **kwargs):
    maquinaEstados: MaquinaEstados = kwargs['maquinaEstados']
    msg: str = kwargs['strMsg']
    servidor: Servidor = kwargs['servidor']
    socketConexao = kwargs['socketConexao']
    bytes = Transmissao.recebeBytes(socketConexao)
    msg = bytes.decode('UTF8')
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
    msg: str = kwargs['strMsg']
    servidor: Servidor = kwargs['servidor']
    socketConexao = kwargs['socketConexao']
    # TODO - ler nome, ip e porta
    # TODO - faz lock da tabela
    # TODO - registra nome, ip e porta na tabela se nome não existe
    # TODO - faz unlock na tabela
    # TODO - se nome foi registrado, envia mensagem registro_exito e imprime a nova tabela
    # TODO - se nome já existia, envia mensagem de registro_falho

def servidorProcessaConsulta(*args, **kwargs):
    maquinaEstados: MaquinaEstados = kwargs['maquinaEstados']
    msg: str = kwargs['strMsg']
    servidor: Servidor = kwargs['servidor']
    socketConexao = kwargs['socketConexao']

def servidorProcessaEncerramento(*args, **kwargs):
    maquinaEstados: MaquinaEstados = kwargs['maquinaEstados']
    msg: str = kwargs['strMsg']
    servidor: Servidor = kwargs['servidor']
    socketConexao = kwargs['socketConexao']

# def clienteProcessa(*args, **kwargs):
#     pass

# def clienteProcessa(*args, **kwargs):
#     pass

# def clienteProcessa(*args, **kwargs):
#     pass

# def clienteProcessa(*args, **kwargs):
#     pass
