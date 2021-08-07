# usando __identificador  para privado
# usando  _identificador  para protegido
# usando   identificador  para publico
class MaquinaEstados():
    """Implementação ad-hoc de uma máquina de estados customizada"""

    def __init__(self, estadoInicial, estadoFinal):
        self.__maquinaValidada = False
        self.__estadoInicial = estadoInicial
        self.__estadoAtual = estadoInicial
        self.__estadoFinal = estadoFinal
        self.__estados = {}
        self.__transicoes = {}

    def adicionaEstado(self, identificadorEstado, estadoMaquina):
        """
        Define um par, identificador e estado a ser identificado, dentro da maquina.
        """
        self.__estados[identificadorEstado] = estadoMaquina

    def adicionaTransicao(self, estadoOrigem, sinal, estadoDestino):
        """
        Define uma transição entre dois estados juntamente com o sinal/gatilho
        que ativa essa transição, aceita apenas um sinal por transição.
        """
        chave = self.__chaveTransicoes(estadoOrigem, sinal)
        self.__transicoes[chave] = estadoDestino

    def confereMaquina(self):
        """
        Confere certas condições para minimizar problemas durante a execução da
        máquina:
        - Confere se o estado inicial realmente existe
        - Confere se o estado final realmente existe
        - Confere se cada trasicao realmente leva a um estado

        OBS.: Lança KeyError
        """
        estados = self.__estados.keys()
        valores = self.__transicoes.values()
        if self.__estadoInicial not in estados:
            raise KeyError('O estado inicial {} não é um estado dessa maquina'
                           .format(self.__estadoInicial))
        else:
            self.__estadoAtual = self.__estadoInicial
        if self.__estadoFinal not in estados:
            raise KeyError('O estado final {} não é um estado dessa maquina'
                           .format(self.__estadoFinal))
        for v in valores:
            if v not in estados:
                raise KeyError('transicao ao estado {0} não é possível porque {0} não é um estado dessa maquina.'
                               .format(v))
        self.__maquinaValidada = True

    def executa(self, *args, **kwargs):
        """
        Começa a execução da maquina e passa parametros que podem ser usados
        pelas callbacks dos estados.
        A execução parará após a máquina entrar no estado final.
        """
        if not self.__maquinaValidada:
            self.confereMaquina()
        self.__estados[self.__estadoAtual].funcaoAoEntrar(*args, **kwargs)
        while (self.__estadoAtual != self.__estadoFinal):
            self.__estados[self.__estadoAtual].funcaoAoExecutar(
                *args, **kwargs)

    def processaSinal(self, sinal, *args, **kwargs):
        """
        Manda um sinal para a maquina.
        O sinal será processado pela maquina para saber qual transicao ativar,
        caso o sinal não leve a uma transicao a maquina mantem o estado atual.
        """
        chave = self.__chaveTransicoes(self.__estadoAtual, sinal)
        novoEstado = self.__transicoes.get(chave)
        if novoEstado is None:
            return
        self.__estados[self.__estadoAtual].funcaoAoSair(*args, **kwargs)
        self.__estados[novoEstado].funcaoAoEntrar(*args, **kwargs)
        self.__estadoAtual = novoEstado

    def reiniciaMaquina(self):
        """
        Coloca a maquina no o estado inicial (definido na construcao do objeto)
        """
        self.__estadoAtual = self.__estadoInicial

    def __chaveTransicoes(self, estado, sinal) -> str:
        return '{}:|:{}'.format(estado, sinal)


class EstadosMaquina():
    def __init__(self,
        funcaoAoEntrar=lambda *args, **kwargs: None,
        funcaoAoExecutar=lambda *args, **kwargs: None,
        funcaoAoSair=lambda *args, **kwargs: None):
        """
        OBS.: A maneira de passar parametros para as callbacks dos estados é
        por parametros e parametros nomeados,
        ex. de parametro nomeado: funcao(nome=valor)
        e dentro da cada função pegar o par nome=valor usando,
        ex.: nome = kwargs.get('nome', valor_caso_nome_nao_exista)
        onde a variavel nome conterá o valor passado como parametro nomeado ou
        o valor para caso o parametro não tenha sido passado.
        """
        self.__funcaoAoEntrar = funcaoAoEntrar
        self.__funcaoAoExecutar = funcaoAoExecutar
        self.__funcaoAoSair = funcaoAoSair

    """
    Funcao que deve ser executada ao
    """
    @property
    def funcaoAoEntrar(self):
        return self.__funcaoAoEntrar

    @property
    def funcaoAoExecutar(self):
        return self.__funcaoAoExecutar

    @property
    def funcaoAoSair(self):
        return self.__funcaoAoSair


# ==============================================================================
# exemplo de uso
if __name__ == '__main__':
    def processaE1(*args, **kwargs):
        print(kwargs.get('a', 'não existe'), kwargs.get('b', 'não existe'))
        kwargs['b'] = 777
        contador.processaSinal('+')

    def processaE2(*args, **kwargs):
        print(kwargs.get('a', 'não existe'), kwargs.get('b', 'não existe'))
        # funciona, pode ser que a maquina nao tenha sido passada como parametro
        # ao ser executada
        # kwargs.get('MAQUINA_ESTADOS').processaSinal('+')
        contador.processaSinal('+')

    contador = MaquinaEstados(0, 3)
    contador.adicionaEstado(0, EstadosMaquina(
        lambda *args, **kwargs: print('entrou e0'),
        lambda *args, **kwargs: contador.processaSinal('+'),
        lambda *args, **kwargs: print('saiu e0')
    ))
    contador.adicionaEstado(1, EstadosMaquina(
        lambda *args, **kwargs: print('entrou e1'),
        processaE1,
        lambda *args, **kwargs: print('saiu e1')
    ))
    contador.adicionaEstado(2, EstadosMaquina(
        lambda *args, **kwargs: print('entrou e2'),
        processaE2,
        lambda *args, **kwargs: print('saiu e2')
    ))
    contador.adicionaEstado(3, EstadosMaquina())

    contador.adicionaTransicao(0, '+', 1)
    contador.adicionaTransicao(1, '+', 2)
    contador.adicionaTransicao(2, '+', 3)

    contador.confereMaquina()

    contador.executa(1, b=2, MAQUINA_ESTADOS=contador)
    contador.reiniciaMaquina()
