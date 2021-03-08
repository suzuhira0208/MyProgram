#ホワイトノイズを生成するプログラム#
import numpy as np
import argparse
import librosa
import wave
import sys
import librosa.display
sys.path.append('../utils')
import vad_utils as utl
import time
import random
import matplotlib.pyplot as plt
import struct


def get_args():
    parser = argparse.ArgumentParser(description = 'ホワイトノイズ生成プログラム')
    parser.add_argument('--s', type = int, default = 3600, help = '時間(秒)')
    parser.add_argument('--n', type = str, default = 'whitenoise_1H.wav', help = '出力ファイルネーム')
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()

    Amp = 0.5
    sr = 16000 #サンプリングレート
    s = args.s #時間（引数から取得)
    N = s * sr #サンプルの個数
    mean = 0.0 #ノイズの平均
    var = 1.0 #ノイズの分散

    y = np.array([random.gauss(mean, var) for i in range(N)]) #ランダムガウス分布
    y = np.rint(32767 * y/ max (abs(y)))#[-32767, 32767]のは範囲に収める
    y = Amp * y
    y = y.astype(np.int16) #16bit整数に変換
    print(y)
    print(y.shape)
    data = struct.pack("h" * len(y), *y)

    utl.write_wave(args.n, y , sr)
