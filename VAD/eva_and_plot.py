"""評価を行ったCSVファイルを読み込んでそれぞれのラベルと音声ファイルをプロットするプログラム"""

import numpy as np
import os
import librosa
import librosa.display
import argparse
import glob
import csv
import pandas as pd
import pprint
import math
import matplotlib.pyplot as plt


from utils import vad_utils

import random

def get_args():
    parser = argparse.ArgumentParser(description = "CSVファイルを読み込み入力波形と一緒に出力するプログラム")
    parser.add_argument('--clean_wav', type = str, default = 'Wav/clean_signal_test.wav', help = 'クリーンwavデータ(評価用)')
    parser.add_argument('--noisy_wav', type = str, default = 'Wav/noisy_signal_test.wav', help = '雑音音声wavデータ(評価用)')
    parser.add_argument('--mmse_wav', type = str, default = 'Wav/mmse_test_snr0.wav', help = 'MMSE-STSA法による音声強調後のWavデータ')
    parser.add_argument('--cc', type = str, default = 'Label_Correct/White_MFCC37_test_crrect.csv', help = '正解ラベルのCSVデータ')
    parser.add_argument('--cmmse', type = str, default = 'Output_MMSE/mmse_test_seg12_snr0.csv', help = "MMSEのCSVファイル")
    parser.add_argument('--csvm', type = str, default = 'Output_SVM/SVM_MFCC37_snr0.csv', help = "SVM_VADのラベルCSVファイル")
    parser.add_argument('--cdnn', type = str, default = 'Output_DNN/DNN_MFCC37_snr0.csv', help = "DNN_VADラベルCSVファイル")


    parser.add_argument('--s', type = int, default = 10, help = 'プロット秒数')
    parser.add_argument('--p', type = str, default = 'Output_evaluate/VAD_Evaluate.pdf', help = '結果pdf出力')

    return parser.parse_args()


def get_csv(path_csv):
    return pd.read_csv(path_csv, engine = 'python')



class PltLabelSignal():
    """---初期化メソッド---"""
    def __init__(self, num = 5, s = 10):
        self.num = num
        self.s = s #時間(s)
        self.ms = int(s * 100) #時間（ms)
        self.fig = plt.figure(figsize = (12, 6))
        self.cnt = 1

    def random_start(self, sr, length):
        self.sr = sr
        self.N = sr * self.s #出力サンプル数
        self.start = random.randint(0, length - self.N) #波形出力開始サンプル数
        self.start_label = int(self.start / (sr / 100)) #ラベル出力開始配列数



    """---インスタンスメソッド:指定秒wavとラベルを描画---"""
    def draw_label_signal(self, signal, df_labels, title):
        col_num = self.cnt
        assert self.num >= self.cnt, "プロット数が指定範囲数を超えました"

        plt.rcParams["font.size"] = 10
        plt.subplot(self.num, 1, col_num)
        plt.subplots_adjust(wspace = 0.2, hspace = 0.4)
        plt.title(title)
        labels = df_labels.values[:,0]
        print(len(labels))
        section_labels = labels[self.start_label : self.ms + self.start_label]
        section_signal = signal[self.start : self.N + self.start]
        #print(len(section_labels))
        #print(section_labels)

        t = np.arange(0, self.N) / self.sr
        x = np.arange(0, self.s * 100) / 100
        plt.plot(t, section_signal)
        plt.plot(x, section_labels, color = "red")
        plt.grid()

        self.cnt = self.cnt + 1

    """---インスタンスメソッド:プロットと保存---"""
    def plt_and_save(self, path_png):
        plt.xlabel("Time(s)")
        plt.subplots_adjust(left = 0.02, right = 0.99, bottom = 0.07, top = 0.95)
        plt.show()
        self.fig.savefig(path_png)
        plt.close()


if __name__ == "__main__":

    """---引数を取得---"""
    args = get_args()
    clean = vad_utils.get_path(args.clean_wav)
    noisy = vad_utils.get_path(args.noisy_wav)
    mmse = vad_utils.get_path(args.mmse_wav)

    cc = vad_utils.get_path(args.cc)
    cmmse = vad_utils.get_path(args.cmmse)
    csvm = vad_utils.get_path(args.csvm)
    cdnn = vad_utils.get_path(args.cdnn)

    pdf = vad_utils.get_path(args.p)
    s = args.s #秒数s

    """---csvファイルを読み込み---"""
    df_cc = get_csv(cc)
    df_cmmse = get_csv(cmmse)
    df_csvm = get_csv(csvm)
    df_cdnn = get_csv(cdnn)


    """---音声データ読み込み---"""
    mmse_data, sr = librosa.load(mmse, sr = 16000)
    clean_data, sr = librosa.load(clean, sr = 16000)
    noisy_data, sr = librosa.load(noisy, sr = 16000)


    """---PltLabelSignalクラスの宣言と初期化---"""
    #num :　表示データ数
    #s : 秒数
    pltlabelsignal = PltLabelSignal(num = 3, s = s)


    """---ランダムで波形とラベルを指定秒数区間切り出し---"""
    pltlabelsignal.random_start(sr = sr, length = len(clean_data))

    """---drawメソッドをそれぞれのデータで実行---"""
    pltlabelsignal.draw_label_signal(clean_data, df_cc, "Clean signal and corret labels")
    pltlabelsignal.draw_label_signal(mmse_data, df_cmmse, "MMSE_signal and MMSE labels(SNR0)")
    pltlabelsignal.draw_label_signal(noisy_data, df_csvm, "Noisy_signal and SVM labels(SNR0)")
    pltlabelsignal.draw_label_signal(noisy_data, df_cdnn, "Noisy_signal and DNN labels(SNR0)")

    """---plt_and_saveメソッドを実行---"""
    pltlabelsignal.plt_and_save(pdf)
