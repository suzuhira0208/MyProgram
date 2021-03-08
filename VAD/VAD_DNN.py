"""--- VAD using DNN"""

import numpy as np
import argparse
import os
import pandas as pd
import sklearn
import sys

import utils.vad_utils as utls
import librosa
import math
import matplotlib.pyplot as plt



from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Activation, LSTM, Dropout
from tensorflow.keras.optimizers import Adam, Adagrad, RMSprop, SGD
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard
from keras.initializers import TruncatedNormal
from keras.layers.core import Dropout
from keras.utils.np_utils import to_categorical


def get_args():
    parser = argparse.ArgumentParser(description = '---DNNでVADを行うプログラム(デフォルトSNR = 0)---')
    parser.add_argument('--train', type = str, default = 'Label_Train/White_MFCC37_train_snr0.csv', help = "学習用CSVファイルを指定")
    parser.add_argument('--test', type = str, default = 'Label_Test/White_MFCC37_test_snr0.csv', help = "検証用CSVファイルを指定")
    parser.add_argument('--o', type = str, default = "Output_DNN/DNN_MFCC37_snr0.csv")
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

    """--- 標準化　---"""
    sc = StandardScaler()
    sc.fit(X_train)
    X_train = sc.transform(X_train)
    sc.fit(X_test)
    X_test = sc.transform(X_test)


    """ --- DNNのモデルの生成 ---"""
    model = Sequential()

    #入力ユニット数 36次元
    #全結合ユニット数 256
    input_dim = 37
    model.add(Dense(64, input_dim = input_dim))

    #活性化関数
    model.add(Activation("relu"))

    #Dropout(rate:削除率)
    model.add(Dropout(rate = 0.2))

    #全結合層ユニット数
    model.add(Dense(128))
    model.add(Activation("relu"))
    model.add(Dropout(rate = 0.5))


    #全結合層ユニット数
    model.add(Dense(128))
    model.add(Activation("relu"))
    model.add(Dropout(rate = 0.5))

    #出力ユニット数:2
    model.add(Dense(2))

    #活性化関数:softmax(確率値に変換)
    model.add(Activation("softmax"))

    #最適化関数(Lr:学習率)
    optimizer = Adam(lr = 0.01)

    #モデルコンパイル(学習設定)
    model.compile(
        optimizer = optimizer,
        loss = "sparse_categorical_crossentropy",
        metrics = ["accuracy"]
    )

    model.summary()


    # EarlyStopping
    # 監視する値の変化が停止したときに学習を終了
    early_stopping = EarlyStopping(
        monitor = 'var_loss', #監視する値
        patience = 10, #値が改善しなくなってからのエポック数
        verbose = 1
    )

    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.1,
        patience=3,
        verbose=1
        )

    #log for TensorBoard
    logging = TensorBoard(log_dir = "log/")


    """---識別器学習---"""

    history = model.fit(
        X_train,
        y_train,
        verbose = 1,
        epochs = 10,
        batch_size = 32,
        validation_split = 0.2,
        callbacks = [early_stopping, reduce_lr, logging]
        )

    """---モデル評価---"""
    score = model.evaluate(X_test, y_test, verbose = 1)
    print("evaluate loss: {0[0]}".format(score))
    print("evaluate acc: {0[1]}".format(score))

    predict_labels = model.predict(X_test)

    predict_labels = pd.DataFrame(predict_labels)
    predict_labels.to_csv(path_o, index = False)
