import tkinter as tk
from typing import List, Type
from PIL import Image, ImageTk
from tkinter import messagebox, scrolledtext
from src.cliente_servidor.cliente import Cliente
from src.util.excepts import InvalidIpError
from src.aplicacao.mensagens_aplicacao import MensagensAplicacao
from mainServidor import funcaoPeriodica

class ClienteInterfaceApp(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # um container para o conteudo da interface
        self._container = tk.Frame(self)
        self.client_socket = Cliente()
        self._log_conexao = []
        self._paginaAtual = None

        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        x_co = int((screen_width / 2) - (550 / 2))
        y_co = int((screen_height / 2) - (400 / 2)) - 80
        self.geometry(f"550x400+{x_co}+{y_co}")
        self.title("Sala Virtual")
        self.iconphoto(False, tk.PhotoImage(file='src/images/chat_ca.png'))


        # definindo paginas da aplicacao
        self._container.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.TRUE)
        self._paginas = {}
        for Pagina in (PaginaInicial, PaginaConsulta):
            p: tk.Frame = Pagina(self._container, self)
            self._paginas[Pagina] = p


        self.protocol("WM_DELETE_WINDOW", self.aoFecharAplicacao)
        self.mostraPagina(PaginaInicial)

    def aoFecharAplicacao(self):
        self.client_socket.realizaPedidoEncerramento()
        self.quit()

    def mostraPagina(self, pagina: Type[tk.Frame]):
        for paginaMostrada in self._container.pack_slaves():
            paginaMostrada.pack_forget()
        p: tk.Frame = self._paginas[pagina]
        p.pack(fill=tk.BOTH, expand=tk.TRUE)
        self._paginaAtual = pagina

    @property
    def paginaAutal(self):
        return self._paginaAtual

    @property
    def logConexao(self):
        return self._log_conexao

    def escreveNologConexao(self, texto: str):
        self._log_conexao.append(texto)
        if len(self._log_conexao) > 50:
            self._log_conexao.pop(0)

    def limpaLogConexao(self):
        self._log_conexao = []

class PaginaInicial(tk.Frame):
    def __init__(self, widgetPai, aplicacao: ClienteInterfaceApp):
        super().__init__(widgetPai)
        self._aplicacao: ClienteInterfaceApp = aplicacao

        img = ImageTk.PhotoImage(Image.open('src/images/login_background.jpg').resize((550, 400), Image.ANTIALIAS))
        self._imagemFundo = tk.Label(self, image=img)
        self._imagemFundo.bgimg = img # LINK - https://stackoverflow.com/questions/54250448/

        self._usuarioEntry = tk.Entry(self, font="lucida 12 bold", width=30, highlightcolor="blue", highlightthickness=1)
        self._ipEntry = tk.Entry(self, font="lucida 12 bold", width=30, highlightcolor="blue", highlightthickness=1)

        self._desenhaTela()

    def _desenhaTela(self):
        cabecalho = tk.Frame(self)
        textoCabecalho = tk.Label(cabecalho, text="Entrar", font="lucida 17 bold", bg="#d0d0d0")
        labelUsuario = tk.Label(self, text="Usuário", font="lucida 12 bold", bg="#d0d0d0")
        labelIp = tk.Label(self, text="IP servidor", font="lucida 12 bold", bg="#d0d0d0")
        botaoAcao = tk.Button(self, text="Conectar", font="lucida 12 bold", cursor="hand2", command=self.conectaRegistra, bg="#16cade", relief="solid", bd=2)

        self._imagemFundo.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # definindo um grid de 5 linhas e 12 colunas
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=3)
        self.rowconfigure(4, weight=4)
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=1)
        self.columnconfigure(3,weight=1)
        self.columnconfigure(4,weight=1)
        self.columnconfigure(5,weight=1)
        self.columnconfigure(6,weight=1)
        self.columnconfigure(7,weight=1)
        self.columnconfigure(8,weight=1)
        self.columnconfigure(9,weight=1)
        self.columnconfigure(10,weight=1)
        self.columnconfigure(11,weight=1)

        # coloando os elementos no grid
        cabecalho.grid(row=0,column=0,columnspan=12,sticky=tk.EW)
        textoCabecalho.pack(side=tk.TOP,fill=tk.X,expand=tk.TRUE)

        labelUsuario.grid(row=1,column=0,columnspan=4,sticky=tk.E)
        self._usuarioEntry.grid(row=1,column=5,columnspan=7,sticky=tk.W)

        labelIp.grid(row=2,column=0,columnspan=4,sticky=tk.E)
        self._ipEntry.grid(row=2,column=5,columnspan=7,sticky=tk.W)

        botaoAcao.grid(row=3,column=0,columnspan=12)

        # colocando o foco do teclado no campo usuario
        self._usuarioEntry.focus_set()

    def conectaRegistra(self):
        validado = False
        nomeUsuario = self._usuarioEntry.get().strip()
        ipServidor = self._ipEntry.get().strip()
        clienteInternet = self._aplicacao.client_socket

        # valida entrada
        if len(nomeUsuario) == 0:
            validado = False
            messagebox.showerror(title='',message='Por favor, digite um nome de usuário com no máximo 30 caracteres')
        elif len(nomeUsuario) > 30:
            validado = False
            messagebox.showerror(title='',message='Por favor, digite um nome de usuário com no máximo 30 caracteres')
        else:
            validado = True

        if validado:
            try:
                clienteInternet.conectaAoServidor(ipServidor, 5000)
                enviado, (cabecalhoRecebido, corpoRecebido) = clienteInternet.realizaPedidoRegistro(nomeUsuario)
                self._aplicacao.escreveNologConexao(enviado)
                self._aplicacao.escreveNologConexao(cabecalhoRecebido+'\n'+corpoRecebido)
                if cabecalhoRecebido.startswith(MensagensAplicacao.REGISTO_EXITO.value.cod):
                    self._aplicacao.mostraPagina(PaginaConsulta)
                elif cabecalhoRecebido.startswith(MensagensAplicacao.REGISTO_FALHA.value.cod):
                    messagebox.showinfo(title='', message='Não foi possível realizar o registro no servidor usando o nome de usuário fornecido.')
            except ConnectionRefusedError as cr:
                messagebox.showinfo(title="Não é possivel conectar!", message="Servidor desligado, Tente novamente, mais tarde.")
                return
            except InvalidIpError:
                messagebox.showinfo(title="Não é possivel conectar!", message='Ip inválido, Tente novamente.')
                return

class PaginaConsulta(tk.Frame):
    def __init__(self, widgetPai, aplicacao):
        super().__init__(widgetPai)
        self._aplicacao: ClienteInterfaceApp = aplicacao

        img = ImageTk.PhotoImage(Image.open('src/images/chat_bg_ca.jpg').resize((550, 400), Image.ANTIALIAS))
        self._imagemFundo = tk.Label(self, image=img)
        self._imagemFundo.bgimg = img # LINK - https://stackoverflow.com/questions/54250448/

        self._usuarioEntry = tk.Entry(self, font="lucida 12 bold", width=30, highlightcolor="green", highlightthickness=1)
        self._ligarEntry = tk.Entry(self, font="lucida 12 bold", width=30, highlightcolor="green", highlightthickness=1)
        self._textoPercorrivel = scrolledtext.ScrolledText(self, height=4, width=60, state=tk.DISABLED)

        self._desenhaTela()

    def _desenhaTela(self):
        cabecalho = tk.Frame(self)
        textoCabecalho = tk.Label(cabecalho, text="Procure alguém", font="lucida 17 bold", bg="#d0d0d0")
        labelUsuario = tk.Label(self, text="Usuário", font="lucida 12 bold", bg="#d0d0d0")
        botaoProcurar = tk.Button(self, text="Procurar", font="lucida 12 bold", cursor="hand2", command=self.procuraUsuario, bg="#229944", relief="solid", bd=2)
        labelLigar = tk.Label(self, text="Ligue", font="lucida 12 bold", bg="#d0d0d0")
        botaoLigar = tk.Button(self, text="Ligar", font="lucida 12 bold", cursor="hand2", command=self.procuraUsuario, bg="#d0d0d0", relief="solid", bd=2, state=tk.DISABLED)

        self._imagemFundo.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # definindo um grid de 5 linhas e 12 colunas
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=1)
        self.columnconfigure(3,weight=1)
        self.columnconfigure(4,weight=1)
        self.columnconfigure(5,weight=1)
        self.columnconfigure(6,weight=1)
        self.columnconfigure(7,weight=1)
        self.columnconfigure(8,weight=1)
        self.columnconfigure(9,weight=1)
        self.columnconfigure(10,weight=1)
        self.columnconfigure(11,weight=1)

        # colocando os elementos no grid
        cabecalho.grid(row=0,column=0,columnspan=12,sticky=tk.EW)
        textoCabecalho.pack(side=tk.TOP,fill=tk.X,expand=tk.TRUE)

        # usuario
        labelUsuario.grid(row=1,column=0,columnspan=12,sticky=tk.S)
        self._usuarioEntry.grid(row=2,column=1,columnspan=6,sticky=tk.E)
        botaoProcurar.grid(row=2,column=8,columnspan=3,sticky=tk.W)

        # texto percorrivel
        self._textoPercorrivel.grid(row=3,column=1,columnspan=10,sticky=tk.NS)

        # ligar
        labelLigar.grid(row=4,column=0,columnspan=12,sticky=tk.S)
        self._ligarEntry.grid(row=5,column=1,columnspan=6,sticky=tk.E)
        botaoLigar.grid(row=5,column=8,columnspan=3,sticky=tk.W)

        # colocando o foco do teclado no campo usuario
        self._usuarioEntry.focus_set()

        # recupera log da conexao e apresenta na tela a cada 300ms
        f1 = funcaoPeriodica(300, 0, lambda: False, self)
        f1.funcao = lambda: self.escreveLogConexaoTextoPercorrivel(self._aplicacao.logConexao)
        self.after(f1.ms, f1.comeca())

    def procuraUsuario(self):
        validado = False
        nomeUsuario = self._usuarioEntry.get().strip()
        clienteInternet = self._aplicacao.client_socket

        # faz validacao da entrada
        if len(nomeUsuario) == 0:
            validado = False
            messagebox.showerror(title='',message='Por favor, digite um nome de usuário para a ser buscado')
        else:
            validado = True

        if validado:
            enviado, (cabecalhoRecebido, corpoRecebido) = clienteInternet.realizaPedidoConsulta(nomeUsuario)
            self._aplicacao.escreveNologConexao(enviado)
            self._aplicacao.escreveNologConexao(cabecalhoRecebido+'\n'+corpoRecebido)
            if cabecalhoRecebido.startswith(MensagensAplicacao.CONSULTA_EXITO.value.cod):
                pass
            elif cabecalhoRecebido.startswith(MensagensAplicacao.CONSULTA_FALHA.value.cod):
                messagebox.showinfo(title='', message='Atualmente não há um usuário com o nome fornecido registrado no servidor.')

    def escreveLogConexaoTextoPercorrivel(self, log: List[str]):
        if self._aplicacao.paginaAutal != PaginaConsulta:
            return

        fimAntes: int = self._textoPercorrivel.vbar.get()[-1]
        self._textoPercorrivel.config(state=tk.NORMAL)
        for texto in log:
            self._textoPercorrivel.insert(tk.END, texto+'\n')
        self._aplicacao.limpaLogConexao()

        # apaga as linhas mais antigas se total passou de 50 linhas
        linhasAtuais = int(self._textoPercorrivel.index(tk.INSERT).partition('.')[0])
        linhasRemover = linhasAtuais - 50
        if linhasRemover > 0:
            self._textoPercorrivel.delete('1.0',f'{linhasRemover+1}.0')

        self._textoPercorrivel.config(state=tk.DISABLED)
        if fimAntes == 1:
            self._textoPercorrivel.yview_moveto(1.0)
