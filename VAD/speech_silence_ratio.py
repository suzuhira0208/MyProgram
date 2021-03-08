"""--- VAD using SVM by MFCC feature ---"""
import numpy as np
import argparse
import os
import pandas as pd
import math
import utils.vad_utils as utls



def get_args():
    parser = argparse.ArgumentParser(description = '---音声、非音声の割合を計算する---')
    parser.add_argument('--l', type = str, default = 'Label_Correct/White_MFCC37_test_correct.csv', help = "入力CSVファイルを指定")
    args = parser.parse_args()
    return args


if __name__ == "__main__":

    args = get_args()

    path_l = utls.get_path(args.l)

    df = pd.read_csv(path_l, engine = 'python')
    print(df)

    index = len(df)
    labels = df.values[:, 0]

    class_0 = 0
    for i in range(index):
        if labels[i] == 0:
            class_0 += 1

    silence_ratio = class_0 / index * 100
    speech_ratio =  (index - class_0) / index * 100

    print("silence ratio:", silence_ratio)
    print("speech ratio:", speech_ratio)
