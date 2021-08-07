from enum import Enum
from typing import NamedTuple


class MensagemAplicacao(NamedTuple):
    cod: str
    description: str

class MensagensAplicacao(Enum):
    REGISTO = MensagemAplicacao('1', '')
    REGISTO_EXITO = MensagemAplicacao('2', '')
    REGISTO_FALHA = MensagemAplicacao('3', '')
    CONSULTA = MensagemAplicacao('4', '')
    CONSULTA_EXITO = MensagemAplicacao('5', '')
    CONSULTA_FALHA = MensagemAplicacao('6', '')
    ENCERRAMENTO = MensagemAplicacao('7', '')
