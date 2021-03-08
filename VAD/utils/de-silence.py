###スピーチ音声を無音区間毎に切り取るプログラム###
import numpy as np
import librosa
import pandas as pd
import scipy.io.wavfile as wav
from inaSpeechSegmenter import Segmenter
from inaSpeechSegmenter import seg2csv
from pydub import AudioSegment
import sys

###--- utilsディレクトリはdatasetsディレクトリより上の階層にあるので ---###
#sys.path.append('../utils')
import vad_utils


if __name__ == '__main__':


    """---Get all wavdata path---"""
    args = vad_utils.parse_args()
    path_input = vad_utils.get_path(args.input_dir)
    path_output = vad_utils.get_path(args.output_dir)
    clean_test_wav = vad_utils.get_wav_data(path_input)


    """---Generate de-silence data---"""
    path_index = 0
    for i in clean_test_wav:
        #sr, input_data = wav.read(i)
        seg = Segmenter(vad_engine = 'smn', detect_gender = False)
        segmentation = seg(i)

        speech_segment_index = 0
        for segment in segmentation:
            segment_label = segment[0]

            if(segment_label == 'speech'):
                #Convert start time in section from s to ms
                start_time = segment[1] * 1000
                end_time = segment[2] * 1000

                # 分割結果をwavに出力
                newAudio = AudioSegment.from_wav(i)
                newAudio = newAudio[start_time:end_time]
                newAudio.export(path_output + "/segment" + str(path_index) + "_" + str(speech_segment_index) +".wav" , format = "wav")

                speech_segment_index += 1
                del newAudio

        path_index += 1
