"""mmseによる評価ラベルと元々の正解ラベルを比較して正答率を算出するプログラム"""

import numpy as np
import os
import argparse
import csv
import pandas as pd
import math
import glob


from utils import vad_utils


def get_args():
    parser = argparse.ArgumentParser(description = "CSVファイルを読み込み入力波形と一緒に出力するプログラム")
    parser.add_argument('--mmse', type = str, default = 'Output_MMSE/mmse_labels_test_snr0.csv', help = 'mmseラベル')
    parser.add_argument('--correct', type = str, default = 'Label_Correct/label_clean_test.csv', help = '正解ラベル')
    return parser.parse_args()


def get_csv(path_csv):
    df = pd.read_csv(path_csv, engine = 'python')

    #print("number of Clean feature ==> : \n", df.keys())


    #print("number of Clean index and columns ==> : \n", df.shape)


    df.info()

    return df



if __name__ == "__main__":

    """---引数を取得---"""
    args = get_args()
    path_mmse = vad_utils.get_path(args.mmse)
    path_correct = vad_utils.get_path(args.correct)


    """---csvファイルを読み込み---"""
    df_mmse = get_csv(path_mmse)
    df_correct = get_csv(path_correct)

    """---データフレームを配列に変換+0列目を抽出---"""
    mmse_labels = df_mmse.values[:,0]
    correct_labels = df_correct.values[:,0]

    index = len(mmse_labels)
    print(index)
    cnt = 0
    for i in range(index):
        if mmse_labels[i] == correct_labels[i]:
            cnt = cnt + 1

    acc = cnt / index * 100

    print("accuracies: " + acc)
