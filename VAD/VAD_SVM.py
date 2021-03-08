"""--- VAD using SVM by MFCC feature ---"""
import numpy as np
import argparse
import os
import pandas as pd
import sklearn
import utils.vad_utils as utls
import scipy.io.wavfile as wav
import librosa
import math
import optuna

from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def get_args():
    parser = argparse.ArgumentParser(description = '---SVMでVADを行うプログラム---')
    parser.add_argument('--train', type = str, default = 'Label_Train/White_MFCC37_train_snr0.csv', help = "学習用CSVファイルを指定")
    parser.add_argument('--test', type = str, default = 'Label_Test/White_MFCC37_test_snr0.csv', help = "検証用CSVファイルを指定")
    parser.add_argument('--o', type = str, default = "Output_SVM/SVM_MFCC37_snr0.csv")
    args = parser.parse_args()
    return args


def get_csv(i_csv):
    """--- get csv file to traning ---"""

    df = pd.read_csv(i_csv, engine = 'python')

    """--- データフレームの各列の欠損値でないデータ数、データ型を確認 ---"""
    df.info()

    """--- 空のデータセットの生成 ---"""
    features = sklearn.utils.Bunch()

    """--- データの格納 ---"""
    features['data'] = df.iloc[:,0:37]
    features['target'] = df.iloc[:,37] #ラベルを格納
    return features

if __name__ == '__main__':

    """--- パスを取得 ---"""
    args = get_args()
    train_csv = utls.get_path(args.train)
    test_csv = utls.get_path(args.test)
    path_o = utls.get_path(args.o)


    """--- データセットを取得 ---"""
    train_data = get_csv(train_csv)
    test_data = get_csv(test_csv)
    X_train, y_train = train_data.data, train_data.target
    X_test, y_test = test_data.data, test_data.target

    """---0ラベルを-1に変換---"""
    y_train = np.where(y_train > 0, 1, -1)
    y_test = np.where(y_test > 0, 1, -1)
    """--- 標準化　---"""
    sc = StandardScaler()
    sc.fit(X_train)
    X_train = sc.transform(X_train)
    X_test = sc.transform(X_test)

    print("test")


    """---識別器モデル(SVM)---"""
    model = SVC()
    model.fit(X_train, y_train)

    print("test1")

    score = model.score(X_test, y_test)
    test_labels = model.predict(X_test)
    accuracies_test = accuracy_score(y_test, pred_test)
    print("Accuracies : ", accuracies_test * 100)

    print("test2")

    """--- -1ラベルを0に変換"""
    test_labels = np.where(test_labels > 0, 1, 0)

    """---csv出力---"""
    svm_labels = pd.DataFrame(test_labels)
    svm_labels.to_csv(path_o, index = False)
    print("test3")
    print('accuracy:', score * 100)
    print(model._gamma)
