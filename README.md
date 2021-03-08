# MyProgram


プログラムの説明


## VAD(Voice Activity Detection)
※CSVファイル、音声ファイルはデータサイズが膨大なため含まれておりません。従って一部入力CSV、音声ファイルを要求するプログラムは動作しません。  
※Linux環境を想定しています。

【メインプログラム】  
・VAD_DNN.py ： DNNによる学習を行います。  
・VAD_SVM.py ： SVMによる学習を行います。  
・mmse_stsa.py : MMSE-STSA法による雑音抑圧プログラムです。出力先はOutput_MMSE内にCSVファイル形式、Wavファイル内にwav音声形式で保存されます。  
・sppech_silence_ratio.py : CSVファイルの発話、非発話の割合を出力します。主にMMSE-STSA法で出力したCSVファイルの割合を算出する際に使用します。  
・eva_and_plot.py ： DNN、SVM、MMSE-STSA法の比較、プロットを行うプログラムです。デフォルトで音声区間をランダムに10秒切り取り表示します。  
・evaluate_mmse.py : MMSE-STSA法の識別率を算出するプログラムです。  

【utils内】  
引数などはプログラム内、もしくはargparseによるヘルプ表示でご覧ください  
・concat_clean.py ： クリーン音声を結合するプログラム  
・concat_noise.py ： ノイズ音声を結合するプログラム  
・de-silence.py : クリーン音声の無音区間を切り取り分割するプログラム  
・extract_MFCC.py : 音声データからMFCC特徴量を算出するプログラム  
・extract_label_webrtcvad.py : クリーン音声に対してVADを行いラベルをCSVファイルとして出力するプログラム  
・gen_mixture_noisy.py : クリーン音声とノイズ音声を任意のSNR比で重畳するプログラム  
・vad_utils.py : ファイルやデータを扱う上で便利な機能をまとめたプログラム  
・whitenoise.py : ホワイトノイズを生成するプログラム  


## GradeDisplay
※radarchart.htmlを読み込んでください

【説明】  
・成績データのCSVファイルを読み込みレーダーチャートでディスプレイ表示を行うプログラムです。  
・チェックされたチェックボックスの成績をレーダーチャートに描画します。  
・科目名をクリックするとその科目の最高点、最低点でソートできます。  
・チェックした学生の成績の、最高点、最低点平均点を算出可能です。  
※レーダーチャートは可視性を考え、生徒一人の各学年の成績表示を想定しています。複数の生徒を対象に比較表示できるようには作られていません。  

## Other
・H_Clustering_Dend_Centroid.py ： 階層的クラスタリングを行いデンドログラム（樹形図）で表示するプログラム。  
・SVM.py : パッケージを用いない自作のSupportVectorMachineプログラム。（このプログラムは未完成です。）  

## PlyRec
C言語で作成した信号処理関係のプログラムです。  
※自身が作成した部分のプログラムコードのみを記載しているため実際には動きません。  
【説明】  
・Ampavg.c ： 入力信号二乗平均振幅、二乗平均平方根を求めるプログラム  
・DFT.c ： DFTプログラム  
・FFT.c ： FFTプログラム  
・Fft.c ： FFTを行う上での関数をまとめたプログラム  
・StreamRecS.c : サイン波を生成、再生、録音を行うプログラム  
