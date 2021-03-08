"""---クリーンスピーチ音声に対してVADを行いラベルをcsvファイルとして出力するプログラム---"""
import numpy as np
import os
import pandas as pd
import argparse
import glob
import csv
import wave
import collections
import librosa.display
import librosa
import contextlib
import matplotlib.pyplot as plt
import matplotlib as mpl
import sys
sys.path.append('../utils')
import vad_utils
import time

import webrtcvad

def get_args():
    parser = argparse.ArgumentParser(description = 'クリーン音声をvadしてCSVファイルで出力するプログラム')
    parser.add_argument('--i', type = str, default = '', help = '入力wavデータを指定')
    parser.add_argument('--o', type = str, default = '', help = 'clean.csv')
    parser.add_argument('--p', type = str, default = 'picture.png', help = '出力ピクチャーネーム')
    return parser.parse_args()

def read_wave(path):
    """wavファイルを読み込んでPCMオーディオデータと、サンプルレートを返す関数"""

    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate

def write_wave(path, audio, sample_rate):
    """Writes a .wav file.

    Takes path, PCM audio data, and sample rate.
    """
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)

class Frame(object):
    """Represents a "frame" of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration

def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.

    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.

    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


if __name__ == "__main__":
    """--- get_path ---"""
    args = get_args()
    path_i = vad_utils.get_path(args.i)

    path_o = vad_utils.get_path(args.o)

    """--- vad ---"""
    audio, sr =  read_wave(path_i)
    vad = webrtcvad.Vad(2)


    frames = frame_generator(10, audio, sr)
    frames = list(frames)
    print(np.shape(frames))


    labels = []
    for i, frame in enumerate(frames):
        is_speech = vad.is_speech(frame.bytes, sr)
        if is_speech == True:
            labels.append(1)
        else:
            labels.append(0)


    """--- ラベルをcsvファイルとして出力 ---"""
    df = pd.DataFrame(labels)
    df.to_csv(path_o, index = False)
    print(np.shape(labels))
    print(df.shape)

    """---音声波形とラベルの表示(10秒)---"""
    fig = plt.figure()
    plt.title("Audio_data and labels")
    y, sr = librosa.load(path_i, sr = sr)
    y = y[0:160000]
    labels = labels[0:1000]
    t = np.arange(0, 160000) / sr
    x = np.arange(0, 1000) / 100
    plt.plot(t, y)
    plt.plot(x, labels, color = "red")
    plt.grid()
    plt.show()
    fig.savefig(args.p)
    plt.close()
