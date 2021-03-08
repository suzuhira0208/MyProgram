import sys
import os
import argparse
import glob
import pandas as pd
import sklearn
import wave
import librosa
import contextlib
import matplotlib.pyplot as plt
import matplotlib as mpl


""" import argument and check exist directry """
def parse_args():
    parser = argparse.ArgumentParser(description = 'Get path of wavfiles')
    parser.add_argument('--datasets_dir', type = str, default = 'datasets', help = '')
    parser.add_argument('--input_dir', type = str, default = 'datasets/input', help = '')
    parser.add_argument('--output_dir', type = str, default = 'datasets/output', help = '')
    return check_args(parser.parse_args())

def check_args(args):
    if not os.path.exists(args.datasets_dir):
        os.makedirs(args.datasets_dir)
    if not os.path.exists(args.input_dir):
        os.makedirs(args.input_dir)
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    return args


""" get path in  each datasets """
def get_path(args):
    PATH_ROOT = os.getcwd()
    # path_datasets = os.path.join(PATH_ROOT, args.datasets_dir)
    # path_input = os.path.join(PATH_ROOT, args.input_dir)
    # path_output = os.path.join(PATH_ROOT, args.output_dir)
    PATH = os.path.join(PATH_ROOT, args)
    return PATH


""" get wav data in input directory """

def get_wav_data(PATH):
    wav_data = glob.glob(PATH + '/*.wav')
    return wav_data

""" --- get csv file to machine learning --- """
def get_csv(file):
    """--- get csv file to traning ---"""

    df = pd.read_csv(file)

    """---　特徴量・データ数の確認 ---"""
    print("number of mfcc feature ==> : \n", df.keys())
    print("number of index and columns ==> : \n", df.shape)

    """--- データフレームの各列の欠損値でないデータ数、データ型を確認 ---"""
    df.info()

    """--- 空のデータセットの生成 ---"""
    vad_mfcc_features = sklearn.utils.Bunch()

    """--- データの格納 ---"""
    vad_mfcc_features['target'] = df['20'] #ラベルを格納
    vad_mfcc_features['data'] = df.loc[:, ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                                       '11', '12', '13', '14', '15', '16', '17', '18', '19']]
    return vad_mfcc_features


def plot_wav(path_i, sr, name):
    fig = plt.figure()
    plt.title(name)
    y, sr = librosa.load(path_i, sr = sr)
    t = np.arange(0, len(y)) / sr
    plt.plot(t, y)
    plt.grid()
    plt.show()
    plt.close()

def read_wave(path_i):
    with contextlib.closing(wave.open(path_i, "rb")) as wf:
        num_channels = wf.getnchannels()
        assert num_chnnels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate

def write_wave(path_o, data, sr):
    with contextlib.closing(wave.open(path_o, "wb")) as wf:
        wf.setnchannels(1) #mono
        wf.setsampwidth(2) #16bit
        wf.setframerate(sr)
        wf.writeframes(data)
