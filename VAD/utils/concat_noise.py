"""---ノイズをループさせて結合し、任意の時間まで長くするプログラム---"""
import argparse
import numpy as np
import wave
import os
import array

###--- utilsディレクトリをインポートするための処理 ---###
#import sys
#sys.path.append('../utils')
import vad_utils

def get_args():
    parser = argparse.ArgumentParser(description = 'Get path of wavfiles directory')
    parser.add_argument('--input_wav', type = str, default = 'noise_elements/babble_noise.wav', help = '入力ノイズ音声ネーム')
    parser.add_argument('--output_wav', type = str, default = 'babble_noise_cocnat.wav', help = '出力ノイズ音声ネーム')
    parser.add_argument('--time', type = int, default = 60, help = 'time(minute)')

    return parser.parse_args()


def cal_amp(wf):
    buf = wf.readframes(wf.getnframes())
    amp = (np.frombuffer(buf, dtype = "int16")).astype(np.float64)
    return amp

if __name__  == "__main__":


    """---get directry and wav data path---"""
    args = get_args()

    input_wav = vad_utils.get_path(args.input_wav) #get input path of de-silence file
    output_wav = vad_utils.get_path(args.output_wav)



    """---concat clean wav data ---"""
    second = args.time * 60
    concat_data = np.empty(0)


    wf = wave.open(input_wav, "r")
    frames = wf.getnframes()
    sr = wf.getframerate()
    sum_frames = second * sr
    amp= cal_amp(wf)

    #print(amp)
    print(sum_frames)

    while(sum_frames > len(concat_data)):
        concat_data = np.concatenate([concat_data, amp])
        print(len(concat_data))

    wf.close()

    concat_data = np.array(concat_data)
    output_data = wave.Wave_write(output_wav)
    output_data.setparams(wf.getparams())
    output_data.writeframes(array.array('h', concat_data.astype(np.int16)).tostring())
    output_data.close()
