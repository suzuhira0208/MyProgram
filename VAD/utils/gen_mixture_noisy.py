"""----クリーン音声とノイズ音声を任意のSNR比で重畳する---"""
import argparse
import numpy as np
import librosa
import wave
import sys
sys.path.append('../utils')
import vad_utils
import array
import random


def get_args():
    parser = argparse.ArgumentParser(description = '---任意のSNR比で雑音と音声を重畳するプログラム---')
    parser.add_argument('--i', type = str, default = 'clean.wav', help = "クリーン音声ファイル")
    parser.add_argument('--n', type = str, default = 'noise.wav', help = "ノイズ音声ファイル")
    parser.add_argument('--o', type = str, default = 'noisy.wav', help = "出力音声ファイル")
    parser.add_argument('--snr', type = float, default = 5, help = "任意のSNR比を指定")
    args = parser.parse_args()
    return args

def cal_amp(wf):
    buffer = wf.readframes(wf.getnframes())
    amplitude = (np.frombuffer(buffer, dtype="int16")).astype(np.float64)
    return amplitude

def cal_rms(amp):
    return np.sqrt(np.mean(np.square(amp), axis = -1))

def cal_adjusted_rms(clean_rms, snr):
    a = float(snr) / 20
    noise_rms = clean_rms / (10 ** a)
    return noise_rms

if __name__ == '__main__':

    """--- get path ---"""
    args = get_args()
    snr = args.snr

    path_i = vad_utils.get_path(args.i)
    path_n = vad_utils.get_path(args.n)
    path_o = vad_utils.get_path(args.o)



    """--- gen mixture noisy data ---"""
    """--- read wav data and calculate ---"""

    print("test")
    clean_data = wave.open(path_i, "r")
    noise_data = wave.open(path_n, "r")

    clean_amp = cal_amp(clean_data)
    noise_amp = cal_amp(noise_data)

    start = random.randint(0, len(noise_amp) - len(clean_amp))
    clean_rms = cal_rms(clean_amp)
    split_noise_amp = noise_amp[start: start + len(clean_amp)]
    noise_rms = cal_rms(split_noise_amp)

    adjusted_noise_rms = cal_adjusted_rms(clean_rms, snr)
    adjusted_noise_amp = split_noise_amp * (adjusted_noise_rms / noise_rms)

    mixed_amp = (clean_amp + adjusted_noise_amp)

    """ normalization """
    if (mixed_amp.max(axis = 0) > 32767):
        mixed_amp = mixed_amp * (32767 / mixed_amp.max(axis = 0))
        clean_amp = clean_amp * (32767 / mixed_amp.max(axis = 0))
        adjusted_noise_amp = adjusted_noise_amp * (32767 / mixed_amp.max(axis = 0))

        """ export wavfile """
        #mixed_amp = np.array(mixed_amp)
        output_data = wave.Wave_write(path_o)
        output_data.setparams(noise_data.getparams())
        output_data.writeframes(array.array('h', mixed_amp.astype(np.int16)).tostring())
        output_data.close()
