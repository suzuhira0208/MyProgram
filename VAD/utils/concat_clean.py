"""---指定時間クリーン音声を結合するプログラム---"""
import argparse
import numpy as np
import wave
import os
import array
###--- utilsディレクトリをインポートするための処理 ---###
import sys
sys.path.append('../utils')
import vad_utils
import random

def get_args():
    parser = argparse.ArgumentParser(description = 'Get path of wavfiles directory')
    parser.add_argument('--input_dir', type = str, default = 'speech_data/musan/musan_datasets/cut_clean', help = 'スピーチ音声が格納されているディレクトリを指定')
    parser.add_argument('--output_wav', type = str, default = 'clean_concat1.wav', help = '出力音声ネームを指定')
    parser.add_argument('--delay_time', type = int, default = 3, help = '1~指定時間秒までのランダムディレイ区間')
    parser.add_argument('--time', type = int, default = 60, help = 'time(minute)')
    return check_args(parser.parse_args())

def check_args(args):
    if not os.path.exists(args.input_dir):
        os.makedirs(args.input_dir)
    return args

def cal_amp(wf):
    buf = wf.readframes(wf.getnframes())
    amp = (np.frombuffer(buf, dtype = "int16")).astype(np.float64)
    return amp

if __name__  == "__main__":


    """---get directry and wav data path---"""
    args = get_args()
    delay_time = args.delay_time
    second = args.time * 60

    path_input_dir = vad_utils.get_path(args.input_dir) #get input path of de-silence file
    output_wav = vad_utils.get_path(args.output_wav)

    path_input_wav = vad_utils.get_wav_data(path_input_dir)

    """---concat clean wav data ---"""
    concat_data = np.empty(0)
    random_time = random.uniform(1, delay_time)
    wf = wave.open(path_input_wav[0], "r")
    sr = wf.getframerate()
    amp = cal_amp(wf)

    interval_time = np.zeros(int(wf.getframerate() * random_time))
    amp = np.concatenate([interval_time, amp])

    concat_data = np.concatenate([concat_data, amp])
    wf.close()


    sum_frames = second * sr
    cnt = 1;

    while(sum_frames >  len(concat_data)):
        random_time = random.uniform(1, delay_time)
        wf = wave.open(path_input_wav[cnt], "r")
        amp = cal_amp(wf)
        interval_time = np.zeros(int(wf.getframerate() * random_time))
        amp = np.concatenate([interval_time, amp])
        concat_data = np.concatenate([concat_data, amp])
        wf.close()


        print(path_input_wav[cnt])
        cnt += 1

    concat_data = np.array(concat_data)
    output_data = wave.Wave_write(output_wav)
    output_data.setparams(wf.getparams())
    output_data.writeframes(array.array('h', concat_data.astype(np.int16)).tostring())
    output_data.close()
