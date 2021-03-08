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
#include <fftw3.h>

int main(int ac, char** av)
{
 
  int i,n = 0;
  Opt* op = opt_open(ac, av, av[0]);
  char* ifile = opt_char(op, "-i", NULL, "入力ファイル");
  if(!ifile) errExit("入力ファイルが指定されていません。\n");
  int blk = opt_int(op, "-b", 512, "バッファ長/DFT点数");

  /*time計測用*/
  clock_t start, stop;
  double ms;
  
  
  

  
  /*fftw用*/
  fftw_complex *out = (fftw_complex *)fftw_malloc(sizeof(fftw_complex)* blk);
  fftw_plan fftplan;
  
  
  
  
  
  
  


  SF_INFO si;


  SNDFILE* fpi = sf_open(ifile, SFM_READ, &si);
  if(!fpi) errExit("入力サンドファイル オープン失敗。\n");
  

  


  /*ptsにblkを代入*/
  int pts = 0;

  double* ixx = (double *)malloc(sizeof(double) * blk);
  double* pw = (double *)malloc(sizeof(double) * blk);
  double * h = (double *)malloc(sizeof(double) * blk);
  double * wd = (double *)malloc(sizeof(double) * blk);
 


  //memsetする
  memset(ixx,0,sizeof(double) * blk);
  memset(h,0,sizeof(double) * blk);
  memset(pw,0,sizeof(double) * blk);
  memset(wd,0,sizeof(double) * blk);
  
 



  
  for(i = 0; i < blk; i++){
   
    wd[i] = 0.54 - 0.46 * cos((2 * M_PI * (double)i)/((double)blk - 1));
  }

 

  
  
   

  

  opt_prfp(op,stderr);

  
  
  int cnt = 0;
  /*fftwのプラン宣言*/
  fftplan =  fftw_plan_dft_r2c_1d(blk, h, out,  FFTW_ESTIMATE);

  start = clock();
  while(1){

    pts = sf_readf_double(fpi, &ixx[blk/2], blk/2);
    for(n = 0; n < blk; n++){
	h[n] = ixx[n] * wd[n];
      }
    
    fftw_execute(fftplan);

    for(i = 0; i < blk; i++){
      pw[i]  += out[i][0] * out[i][0] + out[i][1] * out[i][1] ;
    }
    
    
    cnt ++;

    if(pts != blk/2) break;
    memcpy(&ixx[0], &ixx[blk/2], sizeof(double) * blk/2);
  }
  
  

  for(i = 0; i < blk/2; i++){
    printf("%f\t %.3f\t %.3f\n",(double)i * si.samplerate/(double)blk,
	   pw[i]/cnt, 10 * log10(pw[i]/cnt));
  }


  stop = clock();

  ms = (double)(stop - start)/CLOCKS_PER_SEC;

  fprintf(stderr,"秒数 = %f秒\n%d\n",ms,cnt);
  
    
  
  opt_close(op);
  sf_close(fpi);
  free(h);
  fftw_free(out);
  free(ixx);
 
  

  return 0;
}
