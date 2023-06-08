import pyaudio
from scipy.fft import fft, fftfreq
import numpy as np


CHUNK = 2**15
RATE = 44100

GUITAR_FREQS_DICT = {'E2': 82.41, 'A2': 110.00, 'D3': 146.83, 'G3': 196.00, 'B3': 246.94, 'E4': 329.63}
GUITAR_LABELS = list(GUITAR_FREQS_DICT.keys())
GUITAR_FREQS = np.array(list(GUITAR_FREQS_DICT.values()))
GUITAR_FREQS_TILED = np.tile(GUITAR_FREQS, (3,1))


def get_dominant_freqency(data):
    N = len(data)
    spectrum = 2.0/N * np.abs(fft(data)[:N//2])
    freqs = fftfreq(N, 1./RATE)[:N//2]
    spectrum[0] = 0.0
    return freqs[np.argmax(spectrum)]

def potential_freqs(freq: float):
    return np.array([freq*0.5, freq, freq*2])

def get_closest_guitar_freq(freq: float) -> tuple[str, float, float]:
    pf = potential_freqs(freq).reshape((3,1))
    diffs = np.abs(GUITAR_FREQS_TILED - pf)
    idx = np.unravel_index(np.argmin(diffs), diffs.shape)
    print(idx)
    mult = 2 ** (int(idx[0]) - 1)
    return GUITAR_LABELS[idx[1]], GUITAR_FREQS[idx[1]], mult

if __name__ == '__main__':
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
    # player = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True, frames_per_buffer=CHUNK)

    # to_write = np.array([])
    # LEN = 10
    # for i in range(int(LEN*RATE/CHUNK)): #go for a LEN seconds
    while True:
        data = np.frombuffer(stream.read(CHUNK),dtype=np.int16)
        dom_freq = get_dominant_freqency(data)
        guitar_string, guitar_freq, mult = get_closest_guitar_freq(dom_freq)
        freq_played = dom_freq * mult
        error = guitar_freq - freq_played
        ok = '(OK)' if abs(error) < 0.7 else ('(-)' if error > 0 else '(+)')
        print(f'{freq_played:.2f} {guitar_freq:.2f}    {guitar_string}{ok}')


    # stream.stop_stream()
    # stream.close()
    # p.terminate()

    # print(to_write)
    # plt.plot(to_write)
    # plt.grid()
    # plt.show()

    # scipy.io.wavfile.write(filename='out.wav', rate=RATE, data=to_write)
