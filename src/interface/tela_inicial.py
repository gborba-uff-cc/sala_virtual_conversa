import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
from src.cliente_servidor.cliente import Cliente
from src.util.excepts import InvalidIpError

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
      if len((self.username_entry.get()).strip()) > 6:
          self.user = self.username_entry.get()[:6]+"."
      else:
          self.user = self.username_entry.get()
      
      try:
        self.client_socket.conectaAoServidor(self.ip.encode('utf-8'), 5000)
        status = self.client_socket.getStatus()
        if status == 'not_allowed':
          self.client_socket.realizaPedidoEncerramento()
          messagebox.showinfo(title="Não é possivel conectar!", message='Desculpa, servidor ocupado. Tente novamente, mais tarde.')
          return

      except ConnectionRefusedError:
        messagebox.showinfo(title="Não é possivel conectar!", message="Servidor desligado, Tente novamente, mais tarde.")
        return
      
      except InvalidIpError:
        messagebox.showinfo(title="Não é possivel conectar!", message='Ip inválido, Tente novamente.')
        return
      
      response_register = self.client_socket.realizaPedidoRegistro(self.user)
          