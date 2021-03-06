#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "portaudio.h"
#include "datatype.h"
#include "opt.h"
#include "misc.h"
#include "pa-misc.h"
#include "chansel.h"
#include "imatrix.h"
#include "fmatrix.h"
#include "chansel.h"
#include "sndfile.h"
#include "setopt.h"
#include <time.h>
#include <malloc.h>
#include <string.h>

void DFTSLOW(float *h, int blk, float *pw){
  int j,i = 0;
  for(j = 0; j < blk; j++){
    float re=0.0,im=0.0;


    for(i = 0; i < blk; i++){

      re += h[i]*cos((-2 * M_PI * (float)j * (float)i)/(float)blk);
      im += h[i]*sin((-2 * M_PI * (float)j * (float)i)/(float)blk);

    }
    pw[j]+=re*re+im*im;
  }

}

void DFTFAST(float *h, float *Co, float *Si, int blk, float *pw){
  int j,i = 0;
  for(j = 0; j < blk; j++){
    float re = 0.0, im = 0.0;

    for(i = 0; i < blk; i++){
      re += h[i] * Co[(i * j)%blk];
      im += h[i] * Si[(i * j)%blk];
    }
    pw[j] += re*re + im*im;
  }



}

int main(int ac, char** av)
{
  /*
  PaError err = Pa_Initialize();
  if( err != paNoError )
    return pa_prError(err, "Initialize");
  pa_showDev();
  */

  //float chr;
  //int L;
  int n,i,j = 0;
  //int count = 0;

  /*実部と虚部*/
  //double Re;
  //double Im;



  Opt* op = opt_open(ac, av, av[0]);
  char* ifile = opt_char(op, "-i", NULL, "入力ファイル");
  char* ofile = opt_char(op, "-o", NULL, "出力ファイル");
  if(!ifile) errExit("入力ファイルが指定されていません。\n");
  int blk = opt_int(op, "-b", 512, "バッファ長/DFT点数");
  int fft = opt_flg(op, "-ta", "テーブル化");

  /*time計測用*/
  clock_t start, stop;
  double ms;














  SF_INFO si;


  SNDFILE* fpi = sf_open(ifile, SFM_READ, &si);
  if(!fpi) errExit("入力サンドファイル オープン失敗。\n");

  FILE* fp = fopen("exam1.txt","w");





  /*ptsにblkを代入*/
  int pts = 0;


#ifdef PAFLOAT
  PaSampleFormat pafmt = paFloat32;
  float* ixx = fm_1D_create(blk*si.channels);
  //float* iyy = fm_1D_create(blk*si.channels);
  float* ire = fm_1D_create(blk*si.channels);
  float* iim = fm_1D_create(blk*si.channels);
  float* pw = fm_1D_create(blk*si.channels);
  float * h = (float *)malloc(sizeof(float) * blk);
  float * Si = (float *)malloc(sizeof(float) * blk);
  float * Co = (float *)malloc(sizeof(float) * blk);
  float * wd = (float *)malloc(sizeof(float) * blk);



  //memset(h, 0, sizeof(double) * L);
#else
  PaSampleFormat pafmt = paInt32;
  int* ixx = im_1D_create(blk*si.channels);
  //int* iyy = im_1D_create(blk*si.channels);
  int* ire = im_1D_create(blk*si.channels);
  int* iim = im_1D_create(blk*si.channels);
  int* pw = im_1D_create(blk*si.channels);
  int * h = (int *)malloc(sizeof(int) * blk);

  int * Si = (int *)malloc(sizeof(int) * blk);
  int * Co = (int *)malloc(sizeof(int) * blk);
  int * wd = (int *)malloc(sizeof(int) * blk);



  //memset(h, 0, sizeof(int) * L);
#endif

  //memsetする
  memset(ixx,0,sizeof(float) * blk);
  memset(h,0,sizeof(float) * blk);
  memset(ire,0, sizeof(float) * blk);
  memset(iim,0, sizeof(float) * blk);

  memset(Si, 0, sizeof(float) * blk);
  memset(Co, 0, sizeof(float) * blk);





  for(i = 0; i < blk; i++){
    Si[i] = sin((i * 2 * M_PI)/blk);
    Co[i] = cos((i * 2 * M_PI)/blk);
    wd[i] = 0.54 - 0.46 * cos((2 * M_PI * (float)i)/((float)blk - 1));
  }









  opt_prfp(op,stderr);



  int cnt = 0;

  start = clock();
  while(1){
    n = 0;
    j = 0;
    i = 0;

    pts = sf_readf_float(fpi, &ixx[blk/2], blk/2);
    for(n = 0; n < blk; n++){
	h[n] = ixx[n] * wd[n];
      }

    if(fft == 0){
      DFTSLOW(h,blk,pw);
    }else if(fft == 1){
      DFTFAST(h,Co,Si,blk,pw);
    }



    //chansel_exec(csl, (char*)ixx, (char*)iyy, pa_sampleSize(pafmt), pts);
    //if((err = Pa_WriteStream(stream, iyy, pts)) != paNoError) pa_prError(err, "Write Stream");

    //sf_write_float(fpi2, iyy, blk);


    cnt ++;

    if(pts != blk/2) break;
    memcpy(&ixx[0], &ixx[blk/2], sizeof(float) * blk/2);
  }


  for(i = 0; i < blk; i++){
    printf("%f\t %.3f\t %.3f\n",(float)i * si.samplerate/(float)blk, pw[i]/cnt, 10 * log10(pw[i]/cnt));
    fprintf(fp, "%f\t %.3f\t %.3f\n",(float)i * si.samplerate/(float)blk, pw[i]/cnt, 10 * log10(pw[i]/cnt));
  }


  stop = clock();

  ms = (double)(stop - start)/CLOCKS_PER_SEC;

  fprintf(stderr,"秒数 = %f秒\n",ms);





  //if((err = Pa_StopStream(stream)) != paNoError) pa_prError(err, "Stop Stream");

  //Pa_CloseStream(stream);
  //Pa_Terminate();
  opt_close(op);
  sf_close(fpi);
  free(h);
  free(Si);
  free(Co);
  fclose(fp);

#ifdef PAFLOAT
  fm_1D_free(ixx);
  fm_1D_free(ire);
  fm_1D_free(iim);
#else
  im_1D_free(ixx);
  im_1D_free(ire);
  im_1D_free(iim);
#endif
  return 0;
}
