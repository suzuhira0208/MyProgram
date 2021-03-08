"""--- Extract MFCC features and add correct label
       Using MFCC feature for 12 dimension, delta, double delta, and (rmse)
       Sum = 37 or 38 dimension---"""

import numpy as np
import os
import librosa
import scipy.io.wavfile as wav
import argparse
import glob
import wave
import csv
import pandas as pd
import pprint

import sys
sys.path.append('../utils')
import vad_utils




def get_args():
    parser = argparse.ArgumentParser(description = 'MFCC特徴量をCSVファイルで出力するプログラム')
    parser.add_argument('--i', type = str, default = '', help = '入力wavデータを指定')
    parser.add_argument('--l', type = str, default = '', help = 'ラベルファイル（CSV）を指定')
    parser.add_argument('--o', type = str, default = 'MFCC_extraction.csv', help = '出力ファイルネーム')
    parser.add_argument('--d', type = int, default = 1, help = 'add delta')
    parser.add_argument('--dd', type = int, default = 1, help = 'add double delta')
    #parser.add_argument('--n_fft', type = int, default = 320)
    return parser.parse_args()

def get_mfcc(i, d, dd):
    n_fft = 320
    hop_length = int(n_fft / 2) #１秒あたりの時刻ビン数　＝ sr /　hop_length
    n_mfcc = 12 #次元数
    input_data, sr = librosa.load(i, sr = 16000)
    mfcc = librosa.feature.mfcc(input_data, sr = sr, hop_length = hop_length, n_mfcc = n_mfcc)
    #MFCC deltas
    if d == 1:
        mfcc_delta = librosa.feature.delta(mfcc)
    #MFCC double deltas
    if dd == 1:
        mfcc_delta2 = librosa.feature.delta(mfcc, order = 2)

    mel_spectogram = librosa.feature.melspectrogram(
                    input_data, sr = sr,
                    n_fft = n_fft,
                    hop_length = hop_length,
                    )

    rms = librosa.feature.rms(
            S = mel_spectogram,
            frame_length = 255,
            hop_length = hop_length
            )

    mfcc = np.asarray(mfcc)
    mfcc_delta = np.asarray(mfcc_delta)
    mfcc_delta2 = np.asarray(mfcc_delta2)
    rms = np.asarray(rms)

    feature = np.concatenate((mfcc, mfcc_delta, mfcc_delta2, rms), axis = 0)
    feature = feature.T

    print("Feature data shape:",feature.shape)

    return feature

if __name__ == "__main__":
    """ --- Get path --- """
    args = get_args()
    path_i = vad_utils.get_path(args.i)
    path_o = vad_utils.get_path(args.o)
    path_l = vad_utils.get_path(args.l)

    """---ラベルファイル読み込み---"""
    labels = [] #ラベル格納用配列
    cnt = 0
    with open(path_l) as f:
        #str型をfloat型にキャストしつつ読み込み
        for row in csv.reader(f, quoting = csv.QUOTE_NONNUMERIC):
            if cnt != 0:
                labels.append(row)
                print(f"Row: {row}")
            cnt += 1

    labels = np.asarray(labels)
    #labels = labels[:,1]
    labels = labels.astype(float)
    labels = labels.astype(int)

    """---特徴量抽出---"""
    feature = get_mfcc(path_i, args.d, args.dd)
    feature = np.delete(feature, len(labels), 0)
    feature = np.asarray(feature)

    print(np.shape(labels))
    print(np.shape(feature))


    """---特徴量とラベルを結合---"""
    labels = labels.reshape(-1, 1)
    datasets = np.concatenate((feature, labels), axis = 1)
    print(datasets)

    """---データフレーム化---"""
    datasets = pd.DataFrame(datasets)

    """---csv形式で出力---"""
    datasets.to_csv(path_o, index = False)
