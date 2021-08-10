import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
from src.cliente_servidor.cliente import Cliente
from src.util.excepts import InvalidIpError
# from src.aplicacao.mensagens_aplicacao import MensagensAplicacao


class TelaInicial(tk.Tk):
  def __init__(self):
    super().__init__()
    self.client_socket = Cliente()
    screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()

    self.x_co = int((screen_width / 2) - (550 / 2))
    self.y_co = int((screen_height / 2) - (400 / 2)) - 80
    self.geometry(f"550x400+{self.x_co}+{self.y_co}")
    self.title("Sala Virtual")

    self.user = None
    self.image_extension = None
    self.image_path = None

    self.first_frame = tk.Frame(self, bg="sky blue")
    self.first_frame.pack(fill="both", expand=True)

    app_icon = Image.open('src/images/chat_ca.png')
    app_icon = ImageTk.PhotoImage(app_icon)

    self.iconphoto(False, app_icon)

    background = Image.open("src/images/login_background.jpg")
    background = background.resize((550, 400), Image.ANTIALIAS)
    background = ImageTk.PhotoImage(background)

    tk.Label(self.first_frame, image=background).place(x=0, y=0)

    head = tk.Label(self.first_frame, text="Entrar", font="lucida 17 bold", bg="grey")
    head.place(relwidth=1, y=24)

    self.username = tk.Label(self.first_frame, text="Usuário", font="lucida 12 bold", bg="grey")
    self.username.place(x=80, y=100)

    self.username_entry = tk.Entry(self.first_frame,  font="lucida 12 bold", width=15,
                                       highlightcolor="blue", highlightthickness=1)
    self.username_entry.place(x=195, y=100)

    self.username_entry.focus_set()

    #IP
    self.ip = tk.Label(self.first_frame, text="IP", font="lucida 12 bold", bg="grey")
    self.ip.place(x=80, y=150)

    self.ip_entry = tk.Entry(self.first_frame,  font="lucida 12 bold", width=15,
                                       highlightcolor="blue", highlightthickness=1)
    self.ip_entry.place(x=195, y=150)

    self.ip_entry.focus_set()

    submit_button = tk.Button(self.first_frame, text="Conectar", font="lucida 12 bold", padx=30, cursor="hand2",
                                  command=self.process_data, bg="#16cade", relief="solid", bd=2)

    submit_button.place(x=200, y=275)


    self.mainloop()

  def process_data(self):
    if self.username_entry.get():
      self.ip = self.ip_entry.get()
      # SECTION - Aquisição do nome do usuário
      if len((self.username_entry.get()).strip()) > 6:
          # REVIEW - o nome do usuário será truncado e ecrescido de um ponto se
          # ele for maior que 6 caracteres? (6 caracteres após remover os
          # espaços vazios)
          # ex.: 'gabrielborba' -> 'gabrie.'
          self.user = self.username_entry.get()[:6]+"."
      else:
        # REVIEW - o nome do usuário pode ser qualquer coisa desde que não passe
        # de 6 caracteres? (6 caracteres incluindo os espaços em branco)
        # '  oi  ' -> '  oi  '
          self.user = self.username_entry.get()
      # !SECTION

      try:
        # SECTION - Conexão e Comunicação
        # FIXME - encode é para transformar de string em bytes,
        # conectaAoServidor recebe str em lugar de bytes
        self.client_socket.conectaAoServidor(self.ip.encode('utf-8'), 5000)
        # NOTE - self.client_socket.conectaAoServidor(self.ip, 5000)
        # FIXME - servidor não começa a comunicação com o cliente, pedir uma
        # leitura sem ter algo a receber do servidor fará o programa parar de
        # responder
        status = self.client_socket.getStatus()
        # FIXME - servidor nao responde com 'not_allowed'
        if status == 'not_allowed':
          # FIXME - realizaPedidoEncerramento é para remover da tabela de
          # clientes do servidor a entrada referente ao cliente
          self.client_socket.realizaPedidoEncerramento()
          messagebox.showinfo(title="Não é possivel conectar!", message='Desculpa, servidor ocupado. Tente novamente, mais tarde.')
          return
        # NOTE - o cabecalho das mensagens trocadas pela aplicação estão todos
        # na enumeração MensagensAplicacao em src/aplicacao/mensagens_aplicacao.py
        # NOTE - MensagensAplicacao.REGISTO_EXITO.value.cod é o campo codigo
        # NOTE - MensagensAplicacao.REGISTO_EXITO.value.description é o campo descricao
        # !SECTION

      except ConnectionRefusedError:
        messagebox.showinfo(title="Não é possivel conectar!", message="Servidor desligado, Tente novamente, mais tarde.")
        return

      except InvalidIpError:
        messagebox.showinfo(title="Não é possivel conectar!", message='Ip inválido, Tente novamente.')
        return

      # TODO - apresentar ao usuário se ele conseguiu ou não se registrar o nome
      # REVIEW - atenção ao valor de retorno das funções do cliente
      response_register = self.client_socket.realizaPedidoRegistro(self.user)
      # SECTION - exemplo de como testar o cabecalho de resposta
      # enviado, (cabecalhoRecebido, corpoRecebido) = self.client_socket.realizaPedidoRegistro(self.user)
      # # NOTE - MensagensAplicacao tem que ser descomentado lá nos imports
      # if cabecalhoRecebido.startswith(MensagensAplicacao.REGISTO_EXITO.value.cod):
      #   # registro foi bem sucedido
      #   pass
      # elif cabecalhoRecebido.startswith(MensagensAplicacao.REGISTO_FALHA.value.cod):
      #   # registro não foi bem sucedido
      #   pass
      # else:
      #   # a resposta não foi nenhuma dessas (teoricamente nunca vai chegar aqui)
      #   pass
      # !SECTION

      # TODO - permitir ao usuário realizar uma consulta a outro usuário do servidor

      # TODO - apresentar ao usuário o resultado da consulta
