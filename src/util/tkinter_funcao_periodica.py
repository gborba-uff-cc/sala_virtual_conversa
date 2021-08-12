class FuncaoPeriodica():
    def __init__(self, ms, limiteVezes: int, funcao, widgetPai) -> None:
        self.ms = ms
        self.limite = limiteVezes
        self.funcao = funcao
        self.execucaoAtual = 0
        self.widgetPai = widgetPai

    def comeca(self):
        if not self.limite or (self.execucaoAtual < self.limite):
            if self.limite:
                self.execucaoAtual += 1
            self.funcao()
            self.widgetPai.after(self.ms, self.comeca)
