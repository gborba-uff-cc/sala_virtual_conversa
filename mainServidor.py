#! /usr/bin/env python3.8

import tkinter as tki
from io import StringIO
from os import SEEK_SET
from typing import Callable

from src.cliente_servidor.servidor import Servidor
from src.util.tkinter_funcao_periodica import FuncaoPeriodica


def mainInterfaceGrafica(janela, servidor: Servidor):
    frameSuperior = tki.Frame(janela)
    frameInferior = tki.Frame(janela)
    frameSuperior.pack(side=tki.TOP)
    frameInferior.pack(side=tki.BOTTOM)

    btnIniciarServidor = tki.Button(
        frameSuperior, text='Abrir Servidor', command=servidor.comecaServir)
    btnFinalizarServidor = tki.Button(
        frameSuperior, text='Fechar Servidor', command=servidor.deixaServir)
    btnIniciarServidor.pack(side=tki.LEFT, padx=70, pady=5)
    btnFinalizarServidor.pack(side=tki.LEFT, padx=70, pady=5)

    scrlLog = tki.Scrollbar(frameInferior)
    txtLog = tki.Text(frameInferior, cursor='arrow', state=tki.DISABLED,
                      wrap=tki.WORD, spacing3=2, yscrollcommand=scrlLog.set)
    scrlLog.config(command=txtLog.yview)
    txtLog.pack(side=tki.LEFT)
    scrlLog.pack(side=tki.LEFT, fill=tki.Y)

    f1 = FuncaoPeriodica(300, 0, lambda: False, janela)
    f1.funcao = lambda: escreveLogServidorEmTxtLog(txtLog, scrlLog, servidor)
    janela.after(f1.ms, f1.comeca())

    janela.mainloop()


def escreveLogServidorEmTxtLog(txtLog: tki.Text, scrlLog: tki.Scrollbar, servidor: Servidor):
    fimAntes: int = scrlLog.get()[-1]
    with servidor.streamLog.lock:
        if isinstance(servidor.streamLog.data, StringIO):
            servidor.streamLog.data.seek(0, SEEK_SET)
            for linha in servidor.streamLog.data:
                adicionaLinhaLog(txtLog, linha, append=True)
        servidor.clearLog()
    if fimAntes == 1:
        txtLog.yview_moveto(1.0)


def adicionaLinhaLog(txtLog: tki.Text, linha: str, append=True):
    """Adiciona o texto como uma nova linha ao elemento txtLog od tipo Text"""
    estadoAtual = txtLog.configure('state')[-1]
    if estadoAtual == tki.DISABLED:
        txtLog.config(state=tki.NORMAL)
        if not append:
            txtLog.delete('1.0', tki.END)
        txtLog.insert(tki.END, linha)
        txtLog.config(state=tki.DISABLED)
    elif estadoAtual == tki.NORMAL:
        if not append:
            txtLog.delete('1.0', tki.END)
        txtLog.insert(tki.END, linha)


def aoFecharJanela():
    servidor.fechaSocket()
    janela.quit()


if __name__ == '__main__':
    SERVIDOR_ENDERECO = 'localhost'
    SERVIDOR_PORTA = 5000
    servidor = Servidor(SERVIDOR_ENDERECO, SERVIDOR_PORTA)
    ip, porta = servidor.enderecoAtual

    janela = tki.Tk()
    janela.title('Servidor em <' + ip + ':' + porta + '>')
    janela.resizable(tki.FALSE, tki.FALSE)
    janela.protocol("WM_DELETE_WINDOW", aoFecharJanela)

    mainInterfaceGrafica(janela, servidor)
