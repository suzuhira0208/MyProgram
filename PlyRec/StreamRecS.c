#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <opt.h>
#include <sndfile.h>
#include <misc.h>
#include "datatype.h"
#include "fmatrix.h"
#include "imatrix.h"
#include "pa-misc.h"
#include "chansel.h"
#include "portaudio.h"
#include "keyin.h"



int main(int ac,char**av)
{
  int i, j, loop = 0, phase = 0;
  char rt;

  Opt* op=opt_open(ac,av,av[0]);


  char* ofile=opt_char(op,"-o",NULL,"録音音声ファイル");
  char* wfile=opt_char(op,"-w",NULL,"書き込み音声ファイル");
  int dev_on = opt_int(op, "-odn", 7, "音声出力デバイス（数字選択）");
  int dev_in = opt_int(op, "-idn", 7, "音声入力デバイス(数字選択)");
  int ch_o = opt_int(op, "-cho", 2, "出力チャネル数");
  int ch_r=opt_int(op,"-chr",1,"録音チャネル数");
  int N = opt_int(op,"-N",512,"ブロック長");


  double fs = opt_double(op, "-fs",192000.0, "サンプリング周波数");
  double Amp = opt_double(op, "-A", 0.5, "振幅");
  double frq = opt_double(op, "-f", 1000.0, "周波数");
  double pha[2] = {0.0, 0.0};
  double phasl[2] = {0.0, 0.0};
  double phaplus[2] = {0.0, 0.0};


  SNDFILE *fpo = NULL,*fpw = NULL;
  SF_INFO sfo,sfw;


  sfo.format = SF_FORMAT_WAV | SF_FORMAT_FLOAT;


  sfo.frames=N;
  sfo.channels=ch_r;
  sfo.samplerate = fs;

  //出力ファイルオープン
  fpo=sf_open(ofile,SFM_WRITE,&sfo);
  if(fpo==NULL){
    fprintf(stderr,"ofile open error (%s)\n",ofile);
    exit(1);
  }

  if(wfile != NULL){
    sfw.format = SF_FORMAT_WAV | SF_FORMAT_FLOAT;
    sfw.frames=N;
    sfw.channels=ch_o;
    sfw.samplerate= fs;

    //書き込みファイルオープン
    fpw=sf_open(wfile,SFM_WRITE,&sfw);
    if(fpw==NULL){
      fprintf(stderr,"wfile open error (%s)\n",wfile);
      exit(1);
    }

  }

  PaError perr;
  PaStream *stream_o,*stream_i;
  PaSampleFormat pafmt = paFloat32;

  if((perr=Pa_Initialize())!=paNoError){
    fprintf(stderr,"Pa_Initialize() Error\n");
    exit(1);
  }

  pa_showDev();
  opt_pr(op);

  ChanSel* csl = chansel_open(op, ch_o, "-co", ch_o);




  printf("dev_on = %d\ndev_in = %d", dev_on,dev_in);


  stream_o = pa_openSimplex(dev_on, 'w', fs, ch_o, N, pafmt);


  if(!stream_o) errExit("output stream open failed\n");
  if((perr = Pa_StartStream(stream_o)) != paNoError)
  pa_prError(perr, "Cannot Start Output Stream");

  //ストリームのオープン


  stream_i = pa_openSimplex(dev_in, 'r', fs, sfo.channels, N, pafmt);

  if(!stream_i) errExit("input stream open failed\n");
  if((perr = Pa_StartStream(stream_i)) != paNoError)
  pa_prError(perr, "Cannot Start Input Stream");

  float *y=(float*)malloc(sizeof(float)*N*sfo.channels);

  float* ixx = fm_1D_create(N*ch_o);
  float* iyy = fm_1D_create(N*ch_o);

  while(1){
    int pts = N;

    //位相を徐々に変えられるようにする
    phaplus[0] = pha[0] / 192;
    phaplus[1] = pha[1] / 192;

    phasl[0] += phaplus[0];
    phasl[1] += phaplus[1];

    //音声録音
    //perr = Pa_ReadStream(stream_i,(void*)y,N);
    //sf_writef_float(fpo,y,N);


    //サイン波を生成
    if(ch_o == 2){


      for(i = 0; i < 192; i++) {
        for(j = 0; j < ch_o; j++) {
          ixx[i * ch_o + j] = (float)( Amp * sin(2 * (M_PI) * frq * (((i + (pts * loop))) / fs) + phasl[j] ));
          phasl[j] += phaplus[j];


        }
      }
      for(i = 192; i < pts; i++) {
        for(j = 0; j < ch_o; j++) {

          ixx[i * ch_o + j] = (float)( Amp * sin(2 * (M_PI) * frq * (((i + (pts * loop))) / fs) + phasl[j]) );

        }
      }




    }else if(ch_o == 1){
      for(i = 0; i < pts; i++) {

        ixx[i] = (float)( Amp * sin(2 * M_PI * frq * (((i + (pts * loop))  / fs)) ));

      }
    }

    chansel_exec(csl, (char*)ixx, (char*)iyy, pa_sampleSize(pafmt), pts);


    if((perr = Pa_WriteStream(stream_o, iyy, pts)) != paNoError) pa_prError(perr, "Write Stream");
    if(wfile != NULL){
      sf_writef_float(fpw, iyy, pts);
    }


    loop ++;

    rt = key_in();
    if(rt == 'a') pha[0] += M_PI / 64;
    if(rt == 'b') pha[0] += M_PI / 32;
    if(rt == 'c') pha[0] += M_PI / 16;
    if(rt == 'd') pha[0] += M_PI / 8;
    if(rt == 'e') pha[0] += M_PI;
    if(rt == '+') phase = 1;
    if(rt == '-') phase = 2;
    if(rt == 's') phase = 0;
    if(rt == 'q') break;

    if(phase == 1){
      pha[0] = M_PI / 192;
    }else if(phase == 2){
      pha[0] = M_PI / 192;
    }
  }

  if((perr = Pa_StopStream(stream_i)) != paNoError) pa_prError(perr, "Stop Stream");
  printf("end while\n");

  //ストリームのストップ
  if(stream_i){
    Pa_StopStream(stream_i);
    Pa_CloseStream(stream_i);
  }

  if(stream_o){
    Pa_StopStream(stream_o);
    Pa_CloseStream(stream_o);
  }

  Pa_Terminate();
  fm_1D_free(ixx);
  fm_1D_free(iyy);
  printf("end pa\n");
  //sf_close(fpi);
  if(fpo)
  sf_close(fpo);
  if(fpw)
  sf_close(fpw);
  printf("end sf\n");
  //free(x);
  free(y);
  printf("end fr\n");
  return 0;
}
