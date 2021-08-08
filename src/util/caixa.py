class Caixa:
        """
        classe para ajudar a passar e mudar argumentos entre uma chamada de
        funçao e outra.

        poder mudar o conteudo da caixa sem mudar de caixa
        """
        def __init__(self, data) -> None:
            self.data = data
