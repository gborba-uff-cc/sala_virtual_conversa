class FuncaoPeriodica():
    """
    Classe que possibilita a execução de uma função dentro de intervalos fixos
    nas interfaces do servidor e do cliente que foram escritas com o tkinter
    """
    def __init__(self, ms, limiteVezes: int, funcao, widgetPai) -> None:
        self.ms = ms
        self.limite = limiteVezes
        self.funcao = funcao
        self.execucaoAtual = 0
        self.widgetPai = widgetPai

    def comeca(self):
        # NOTE - executa se não tem um maximo de vezes definido; ou
        # se o numero da execucao atual for menor que o maximo de vezes definido;
        if not self.limite or (self.execucaoAtual < self.limite):
            if self.limite:
                self.execucaoAtual += 1
            self.funcao()
            self.widgetPai.after(self.ms, self.comeca)
