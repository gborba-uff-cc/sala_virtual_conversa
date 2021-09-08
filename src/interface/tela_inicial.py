import tkinter as tk
from tkinter import messagebox, scrolledtext
from typing import List, Type

from PIL import Image, ImageTk
from src.aplicacao.mensagens_aplicacao import MensagensAplicacao, MensagensLigacao
from src.cliente_servidor.cliente import Cliente
from src.cliente_servidor.clienteServidorLigacao import ClienteServidorLigacao
from src.util.excepts import InvalidIpError
from src.util.tkinter_funcao_periodica import FuncaoPeriodica


class ClienteInterfaceApp(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.resizable(tk.FALSE, tk.FALSE)

        # um container para o conteudo da interface
        self._container = tk.Frame(self)
        self.client_socket = Cliente()
        self.agenteLigacao = ClienteServidorLigacao()
        self._log_conexao = []
        self._paginaAtual = None

        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        x_co = int((screen_width / 2) - (550 / 2))
        y_co = int((screen_height / 2) - (400 / 2)) - 80
        self.geometry(f"550x400+{x_co}+{y_co}")
        self.title("Sala Virtual")
        self.iconphoto(False, tk.PhotoImage(file='src/images/chat_ca.png'))

        # NOTE - definido meu nome de usuario registrado
        self._nomeRegistrado = ''
        self._ultimoNomeBuscado = ''
        self.apresentandoChamadaRecebida = False

        # definindo paginas da aplicacao
        self._container.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.TRUE)
        self._paginas = {}
        for Pagina in (PaginaInicial, PaginaConsulta):
            p: tk.Frame = Pagina(self._container, self)
            self._paginas[Pagina] = p


        self.protocol("WM_DELETE_WINDOW", self.aoFecharAplicacao)
        self.mostraPagina(PaginaInicial)

    def aoFecharAplicacao(self):
        """
        Método que encerrará a conexão do cliente como servidor quando o usuário
        fechar a aplição.
        """
        self.client_socket.realizaPedidoEncerramento(self.agenteLigacao.enderecoAtualServidorUdp[1])
        self.quit()

    def mostraPagina(self, pagina: Type[tk.Frame]):
        """
        Faz com que a aplicação mostre uma certa tela ao usuário.
        """
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
        """
        Atualiza o conteúdo do log da conexão
        """
        self._log_conexao.append(texto)
        if len(self._log_conexao) > 50:
            self._log_conexao.pop(0)

    def limpaLogConexao(self):
        """
        Esvazia o conteúdo do log da aplicação
        """
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
        """
        Define a ação de tentar conectar ao servidor e registrar o cliente,
        tratando da entrada do usuário
        """
        validado = False
        nomeUsuario = self._usuarioEntry.get().strip()
        ipServidor = self._ipEntry.get().strip()
        clienteInternet = self._aplicacao.client_socket
        agenteLigacao = self._aplicacao.agenteLigacao

        # NOTE - faz a validação da entrada (testando as possibilidades do que
        # poderiamos fazer)
        if len(nomeUsuario) == 0:
            validado = False
            messagebox.showerror(title='',message='Por favor, digite um nome de usuário com no máximo 30 caracteres')
        elif len(nomeUsuario) > 30:
            validado = False
            messagebox.showerror(title='',message='Por favor, digite um nome de usuário com no máximo 30 caracteres')
        else:
            validado = True

        if validado:
            # NOTE - tenta conectar e registrar o nome no servidor
            try:
                clienteInternet.conectaAoServidor(ipServidor, 5000)
                # NOTE - recupera o que foi enviado e recebido
                enviado, (cabecalhoRecebido, corpoRecebido) = clienteInternet.realizaPedidoRegistro(nomeUsuario, agenteLigacao.enderecoAtualServidorUdp[1])
                self._aplicacao.escreveNologConexao(enviado)
                self._aplicacao.escreveNologConexao(cabecalhoRecebido+'\n'+corpoRecebido)
                # NOTE - verifica e trata a resposta recebida
                if cabecalhoRecebido.startswith(MensagensAplicacao.REGISTO_EXITO.value.cod):
                    self._aplicacao._nomeRegistrado = nomeUsuario
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
        self._ipEntry = tk.Entry(self, font="lucida 12 bold", width=20, highlightcolor="green", highlightthickness=1)
        self._portaEntry = tk.Entry(self, font="lucida 12 bold", width=10, highlightcolor="green", highlightthickness=1)
        self._textoPercorrivel = scrolledtext.ScrolledText(self, height=4, width=60, state=tk.DISABLED)
        self._botaoLigar = tk.Button(self, text="Ligar", font="lucida 12 bold", cursor="hand2", command=self.iniciaLigacao, bg="#d0d0d0", relief="solid", bd=2)
        self._botaoEncerrar = tk.Button(self, text="Encerrar", font="lucida 12 bold", cursor="hand2", command=self.finalizaLigacao, bg="#d0d0d0", relief="solid", bd=2)

        self._desenhaTela()

    def _desenhaTela(self):
        cabecalho = tk.Frame(self)
        textoCabecalho = tk.Label(cabecalho, text="Procure alguém", font="lucida 17 bold", bg="#d0d0d0")
        labelUsuario = tk.Label(self, text="Usuário", font="lucida 12 bold", bg="#d0d0d0")
        botaoProcurar = tk.Button(self, text="Procurar", font="lucida 12 bold", cursor="hand2", command=self.procuraUsuario, bg="#229944", relief="solid", bd=2)
        labelLigar = tk.Label(self, text="Ligue", font="lucida 12 bold", bg="#d0d0d0")

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
        self._ipEntry.grid(row=5,column=1,columnspan=5)
        self._portaEntry.grid(row=5,column=5,columnspan=3)
        self._botaoLigar.grid(row=5,column=8,columnspan=2,sticky=tk.E)
        self._botaoEncerrar.grid(row=5,column=8,columnspan=2,sticky=tk.E)
        self._botaoLigar.grid_remove()  # esconde o widget memorizando onde ele estava
        self._botaoEncerrar.grid_remove()  # esconde o widget memorizando onde ele estava

        # colocando o foco do teclado no campo usuario
        self._usuarioEntry.focus_set()

        # NOTE - definindo uma funcao que vai ser executada a cada 300ms
        f1 = FuncaoPeriodica(
            300, 0,
            self.atualizaElementosPagina,
            self)
        f1.comeca()

    def procuraUsuario(self):
        validado = False
        nomeUsuario = self._usuarioEntry.get().strip()
        clienteInternet = self._aplicacao.client_socket

        # NOTE - faz a validacao da entrada
        if len(nomeUsuario) == 0:
            validado = False
            messagebox.showerror(title='',message='Por favor, digite um nome de usuário para ser buscado')
        else:
            validado = True

        if validado:
            enviado, (cabecalhoRecebido, corpoRecebido) = clienteInternet.realizaPedidoConsulta(nomeUsuario)
            self._aplicacao.escreveNologConexao(enviado)
            self._aplicacao.escreveNologConexao(cabecalhoRecebido+'\n'+corpoRecebido)
            # NOTE - verifica e trata a resposta recebida
            if cabecalhoRecebido.startswith(MensagensAplicacao.CONSULTA_EXITO.value.cod):
                pass
            elif cabecalhoRecebido.startswith(MensagensAplicacao.CONSULTA_FALHA.value.cod):
                messagebox.showinfo(title='', message='Atualmente não há um usuário com o nome fornecido registrado no servidor.')


    def iniciaLigacao(self):
        # NOTE - recupera alguns valores
        (enviado, (cabecalho, corpo)) = ('', ('', ''))
        meuNome = self._aplicacao._nomeRegistrado
        destNome = self._aplicacao._ultimoNomeBuscado
        ip = self._ipEntry.get().strip()
        porta = int(self._portaEntry.get().strip())
        # NOTE - faz a chamada para o outro usuario
        with self._aplicacao.agenteLigacao._emChamada.lock:
            if isinstance(self._aplicacao.agenteLigacao._emChamada.data, bool):
                try:
                    # TODO - tenta enviar mensagem de convite
                    (enviado, (cabecalho, corpo)) = self._aplicacao.agenteLigacao.realizaConvite(ip, porta, self._aplicacao._ultimoNomeBuscado, meuNome)
                except InvalidIpError:
                    messagebox.showerror(
                            title="Não é possivel conectar!",
                            message='Ip inválido, Verifique o endereço digitado.')
            if self._aplicacao.agenteLigacao._emChamada.data:
                messagebox.showinfo(
                        title="Não é possivel conectar!",
                        message='Voce já está em uma chamada.')
            elif cabecalho.startswith(MensagensLigacao.CONVITE_ACEITO.value.cod):
                # TODO - trocar botao ligar por botao encerrar
                pass
            elif cabecalho.startswith(MensagensLigacao.CONVITE_REJEITADO.value.cod):
                 messagebox.showinfo(
                        title="Não é possivel conectar!",
                        message='Usuário de destino está ocupado.')

    def finalizaLigacao(self):
        self._aplicacao.agenteLigacao.realizaEncerramento()

    def atualizaElementosPagina(self):
        with self._aplicacao.agenteLigacao.emChamada.lock:
            if isinstance(self._aplicacao.agenteLigacao.emChamada.data, bool):
                if self._aplicacao.agenteLigacao.emChamada.data:
                    self._botaoLigar.grid_remove()
                    self._botaoEncerrar.grid()  # vai relembrar onde ele foi posto da ultima vez
                else:
                    self._botaoEncerrar.grid_remove()
                    self._botaoLigar.grid()  # vai relembrar onde ele foi posto da ultima vez
        with self._aplicacao.agenteLigacao.log.lock:
            if isinstance(self._aplicacao.agenteLigacao.log.data, list):
                for texto in self._aplicacao.agenteLigacao.log.data:
                    self._aplicacao.escreveNologConexao(texto)
                self._aplicacao.agenteLigacao.clearLog()
        self.escreveLogConexaoTextoPercorrivel(self._aplicacao.logConexao)
        self.apresentaChamadaRecebida()

    def escreveLogConexaoTextoPercorrivel(self, log: List[str]):
        """
        Mótodo que consome o log da aplicação e o apresenta ao usuário
        """
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

    def apresentaChamadaRecebida(self):
        def aceitaChamada():
            self._aplicacao.agenteLigacao.respondeConvite(True)
            self._aplicacao.apresentandoChamadaRecebida = False
            win.destroy()

        def rejeitaChamada():
            self._aplicacao.agenteLigacao.respondeConvite(False)
            self._aplicacao.apresentandoChamadaRecebida = False
            win.destroy()

        recebendoChamada = False
        with self._aplicacao.agenteLigacao._recebendoChamada.lock:
            if isinstance(self._aplicacao.agenteLigacao._recebendoChamada.data, bool):
                recebendoChamada = self._aplicacao.agenteLigacao._recebendoChamada.data

        # NOTE - não mostra a caixa de diálogo se já estiver mostrando ou se não estiver recebendo uma chamada
        if self._aplicacao.apresentandoChamadaRecebida or not recebendoChamada:
            return
        else:
            self._aplicacao.apresentandoChamadaRecebida = True

        win = tk.Toplevel()
        # NOTE - instrui ao tkinter que essa janela é filha de outra janela e
        # nao uma janela stand-alone
        win.transient(self._aplicacao)
        win.title('Chamada')
        tk.Label(win, text=f'Você deseja atender a chamada de {self._aplicacao.agenteLigacao._infoChamadaRecebida.nomeUsuario}.').pack()
        # TODO - agrupar os botões em uma única linha
        tk.Button(win, text="Aceitar", cursor="hand2", command=aceitaChamada).pack()
        tk.Button(win, text="Recusar", cursor="hand2", command=rejeitaChamada).pack()
