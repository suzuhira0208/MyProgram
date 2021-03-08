import numpy as np
import scipy as sp
from scipy import signal
import sys
import wave
import tempfile
from six.moves import xrange, zip
import scipy.special as spc
import math
import argparse
import pandas as pd

#sys.path.append('../../utils')
import utils.vad_utils as utls


_window = None
_G = None
_prevGamma = None
_alpha = None
_prevAmp = None
_ratio = None
_constant = None
_gamma15 = None
#np.seterr('ignore')


def get_args():
    parser = argparse.ArgumentParser(description = '---MMSE-STSA法---')
    parser.add_argument('--i', type = str, default = "Wav/noisy_signal_test_snr0.wav", help = "ノイジーファイルを入力")
    parser.add_argument('--o', type = str, default = "Wav/mmse_test_snr0.wav")
    parser.add_argument('--lo', type = str, default = "Output_MMSE/mmse_labels_test_snr0.csv")
    parser.add_argument('--winsize', type = int, default = 320)
    parser.add_argument('--ratio', type = float, default = 1.0)
    parser.add_argument('--constant', type = float, default = 0.001)
    parser.add_argument('--alpha', type = float, default = 0.99)
    args = parser.parse_args()
    return args

def noise_reduction(signal,params,winsize,window,ss,ntime):
    out=np.zeros(len(signal),np.float64)
    #print(np.shape(out))
    n_pow = compute_avgpowerspectrum(signal[0:winsize*int(params[2] /float(winsize)/(1000.0/ntime))],winsize,window)#maybe 300ms
    nf = (int(len(signal)/(winsize/2)) - 1)
    for no in xrange(nf):
        s = get_frame(signal, winsize, no)
        add_signal(out, compute_by_noise_pow(s,n_pow), winsize, no)

    return out


def write(param,signal):
    st = tempfile.TemporaryFile()
    wf=wave.open(st,'wb')
    wf.setparams(params)
    s=sp.int16(signal*32767.0).tobytes()
    wf.writeframes(s)
    st.seek(0)
    #print(st.read())
    return wf

def read(fname,winsize):
    if fname =="-":
        wf=wave.open(sys.stdin,'rb')
        n=wf.getnframes()
        str=wf.readframes(n)
        params = ((wf.getnchannels(), wf.getsampwidth(),
                   wf.getframerate(), wf.getnframes(),
                   wf.getcomptype(), wf.getcompname()))
        siglen=((int )(len(str)/2/winsize) + 1) * winsize
        signal=np.zeros(siglen, np.float64)
        signal[0:len(str)/2] = np.float64(sp.fromstring(str,np.int16))/32767.0
        return signal,params
    else:
        return read_signal(fname,winsize)


def __init__(winsize, window, constant=0.001, ratio=1.0, alpha=0.99):
    global _window
    global _G
    global _prevGamma
    global _alpha
    global _prevAmp
    global _ratio
    global _constant
    global _gamma15
    global _eta
    global _labels
    _window = window
    _G = np.zeros(winsize, np.float64)
    _prevGamma = np.zeros(winsize, np.float64)
    _alpha = alpha
    _prevAmp = np.zeros(winsize, np.float64)
    _ratio = ratio
    _constant = constant
    _gamma15 = math.gamma(1.5)
    _eta = -5.0
    _labels = []

def compute_by_noise_pow(signal, n_pow):
    # global _window
    # global _G
    # global _prevGamma
    # global _alpha
    # global _prevAmp
    # global _ratio
    # global _constant
    # global _gamma15

    s_spec = np.fft.fft(signal * _window)
    s_amp = np.absolute(s_spec)
    #print(np.shape(s_amp))
    s_phase = np.angle(s_spec)
    #for idx in xrange(len(s_phase)):
    #    print(s_phase[idx])
    gamma = _calc_aposteriori_snr(s_amp, n_pow)
    xi = _calc_apriori_snr(gamma)
    _prevGamma = gamma
    nu = gamma * xi / (1.0 + xi)
    _G = (_gamma15 * np.sqrt(nu) / gamma) * np.exp(-nu / 2.0) * ((1.0 + nu) * spc.i0(nu / 2.0) + nu * spc.i1(1, nu / 2.0))

    idx = np.less(s_amp ** 2.0, n_pow)
    #print(idx)
    _G[idx] = _constant
    idx = np.isnan(_G) + np.isinf(_G)
    _G[idx] = xi[idx] / (xi[idx] + 1.0)
    idx = np.isnan(_G) + np.isinf(_G)
    _G[idx] = _constant
    #print(_G)
    _G = np.maximum(_G, 0.0)

    LAMBDA_means = np.mean(np.log(_G * np.exp(nu)))
    #print(LAMBDA_means)

    if LAMBDA_means > _eta:
        _labels.append(1)
    else:
        _labels.append(0)



    amp = _G * s_amp
    amp = np.maximum(amp, 0.0)
    amp2 = _ratio * amp + (1.0 - _ratio) * s_amp
    _prevAmp = amp
    spec = amp2 * np.exp(s_phase * 1j)
    return np.real(np.fft.ifft(spec))

def _sigmoid(gain):
    for i in xrange(len(gain)):
        gain[i] = sigmoid(gain[1], 1, 2, _gain)

def compute(signal, noise):
    n_spec = np.fft.fft(noise * _window)
    n_pow = np.absolute(n_spec) ** 2.0
    return compute_by_noise_pow(signal, n_pow)

def _calc_aposteriori_snr(s_amp, n_pow):
    return s_amp ** 2.0 / n_pow

def _calc_apriori_snr(gamma):
    return _alpha * _G ** 2.0 * _prevGamma +\
        (1.0 - _alpha) * np.maximum(gamma - 1.0, 0.0)  # a priori s/n ratio

def _calc_apriori_snr2(gamma, n_pow):
    return _alpha * (_prevAmp ** 2.0 / n_pow) +\
        (1.0 - _alpha) * np.maximum(gamma - 1.0, 0.0)  # a priori s/n ratio


def read_signal(filename, winsize):
    wf = wave.open(filename, 'rb')
    n = wf.getnframes()
    st = wf.readframes(n)
    params = ((wf.getnchannels(), wf.getsampwidth(),
               wf.getframerate(), wf.getnframes(),
               wf.getcomptype(), wf.getcompname()))
    siglen = ((int)(len(st) / 2 / winsize) + 1) * winsize
    signal = np.zeros(siglen, np.float64)
    signal[0:int(len(st) / 2)] = np.float64(np.frombuffer(st, np.int16)) / 32767.0
    return [signal, params]


def get_frame(signal, winsize, no):
    shift = int(winsize / 2)
    start = int(no * shift)
    end = start + winsize
    return signal[start:end]


def add_signal(signal, frame, winsize, no):
    shift = int(winsize / 2)
    start = int(no * shift)
    end = start + winsize
    signal[start:end] = signal[start:end] + frame


def write_signal(filename, params, signal):
    wf = wave.open(filename, 'wb')
    wf.setparams(params)
    s = np.int16(signal * 32767.0).tobytes()
    wf.writeframes(s)
    wf.close()


def get_window(winsize, no):
    shift = int(winsize / 2)
    s = int(no * shift)
    return (s, s + winsize)


def separate_channels(signal):
    return signal[0::2], signal[1::2]


def uniting_channles(leftsignal, rightsignal):
    ret = []
    for i, j in zip(leftsignal, rightsignal):
        ret.append(i)
        ret.append(j)
    return np.array(ret, np.float64)


def compute_avgamplitude(signal, winsize, window):
    windownum = int(len(signal) / (winsize / 2)) - 1
    avgamp = np.zeros(winsize)
    for l in xrange(windownum):
        avgamp += np.absolute(sp.fft.fft(get_frame(signal, winsize, l) * window))
    return avgamp / float(windownum)


def compute_avgpowerspectrum(signal, winsize, window):
    windownum = int(len(signal) / (winsize / 2)) - 1
    avgpow = np.zeros(winsize)
    for l in xrange(windownum):
        avgpow += np.absolute(sp.fft.fft(get_frame(signal, winsize, l) * window))**2.0
    return avgpow / float(windownum)


def sigmoid(x, x0, k, a):
    y = k * 1 / (1 + np.exp(-a * (x - x0)))
    return y


def calc_kurtosis(samples):
    n = len(samples)
    avg = np.average(samples)
    moment2 = np.sum((samples - avg) ** 2) / n
    s_sd = np.sqrt(((n / (n - 1)) * moment2))
    k = ((n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))) * np.sum(((samples - avg) / s_sd) ** 4)
    return k - 3 * ((n - 1) ** 2) / ((n - 2) * (n - 3))


if __name__ == '__main__':
    args = get_args()
    path_i = utls.get_path(args.i)
    path_o = utls.get_path(args.o)
    path_lo = utls.get_path(args.lo)
    winsize = args.winsize
    ratio = args.ratio
    constant = args.constant
    alpha = args.alpha


    window = np.hanning(args.winsize)

    __init__(winsize, window, ratio = ratio, constant = constant, alpha = alpha)

    signal, params = read(path_i, winsize)
    #import os.path


    write_signal(path_o, params, noise_reduction(signal, params, winsize, window, None, 300))


    """---データフレーム化---"""
    _labels = np.asarray(_labels)
    labels = pd.DataFrame(_labels)

    """---csv形式で出力---"""
    labels.to_csv(path_lo, index = False)
