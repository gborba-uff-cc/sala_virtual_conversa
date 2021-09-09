# NOTE - Inspirado em:
# LINK - https://people.csail.mit.edu/hubert/pyaudio/#sources
# LINK - https://people.csail.mit.edu/hubert/pyaudio/docs/
# LINK - https://realpython.com/python-deque/#sharing-data-between-threads


# FIXME - para "ALSA lib pcm.c:8306:(snd_pcm_recover) underrun occurred" digite no terminal
# NOTE  - echo 4096 | /usr/bin/tee /proc/asound/card0/pcm0p/sub0/prealloc
# LINK  - https://www.reddit.com/r/ChipCommunity/comments/53aly4/alsa_lib_pcmc7843snd_pcm_recover_underrun_occurred/

from typing import Deque
import pyaudio
import time
import threading

class MecanismoAudio():

    def __init__(
            self,
            tamanhoAmostra: int = 1,
            nCanais: int = 1,
            txAmostragem: int = 44100,
            bufferGravacao: Deque = Deque(maxlen=50),
            bufferReproducao: Deque = Deque(maxlen=50)) -> None:

        self._WIDTH = tamanhoAmostra
        self._CHANNELS = nCanais
        self._RATE = txAmostragem

        self._PY_A = pyaudio.PyAudio()
        self._BUFFER_FlUXO_ENTRADA = bufferGravacao
        self._BUFFER_FlUXO_SAIDA = bufferReproducao
        self._fluxoEntrada = self._PY_A.open(
            format=self._PY_A.get_format_from_width(self._WIDTH),
            channels=self._CHANNELS,
            rate=self._RATE,
            input=True,
            start=False,
            stream_callback=self._geraPacoteAudio)
        self._fluxoSaida = self._PY_A.open(
            format=self._PY_A.get_format_from_width(self._WIDTH),
            channels=self._CHANNELS,
            rate=self._RATE,
            output=True,
            start=False,
            stream_callback=self._consomePacoteAudio)

        self._executando = False
        self._tExecuta: threading.Thread = threading.Thread(target=self._executa)
        # NOTE - manter por causa do .close()
        self._tExecuta.start()

    @property
    def executando(self):
        return self._executando

    def executa(self):
        """
        Inicia uma thread que começará:
        - Capturar e armazena no buffer de entrada o áudio da entrada padrão do computador
        - Buscar e reproduzir na saída padrão o áudio armazenado no buffer de saída
        """

        self._executando = True
        # NOTE - permite apenas uma thread desse metodo
        if not self._tExecuta.is_alive():
            self._tExecuta = threading.Thread(target=self._executa)
            self._tExecuta.start()

    def paraExecucao(self):
        self._executando = False

    def close(self):
        """
        Librera os recursos utilizados e para a execucao thread de execução caso
        ela esteja ativa
        """

        self._fluxoEntrada.close()
        self._fluxoSaida.close()
        self._executando = False
        self._tExecuta.join()
        self._PY_A.terminate()

    def _executa(self):
        self._fluxoEntrada.start_stream()
        # NOTE - delay para inicio da reproducao
        time.sleep(0.1)
        self._fluxoSaida.start_stream()

        while self._executando:
            time.sleep(.5)

        self._fluxoEntrada.stop_stream()
        self._fluxoSaida.stop_stream()

    def _geraPacoteAudio(self, in_data, frame_count, time_info, status):
        self._BUFFER_FlUXO_ENTRADA.append(in_data)
        return (in_data, pyaudio.paContinue)

    def _consomePacoteAudio(self, in_data, frame_count, time_info, status):
        try:
            out_data = self._BUFFER_FlUXO_SAIDA.popleft()
        except IndexError:
            out_data = b'\x00'*frame_count
        return (out_data, pyaudio.paContinue)

# NOTE - para testar o uso
if __name__ == '__main__':
# ==============================================================================
    d = Deque()
    audioEngine = MecanismoAudio(bufferGravacao=d,bufferReproducao=d)

# ==============================================================================
    audioEngine.executa()
    print('>>> executou')
    try:
        print('>>> ctrl+c para interromper')
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    audioEngine.paraExecucao()
    print('\n>>> interrompeu')
    time.sleep(2)

# ==============================================================================
    audioEngine.executa()
    print('>>> executou')
    try:
        print('ctrl+c para parar')
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    audioEngine.close()
    print('\nTerminou')
