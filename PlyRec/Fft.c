#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fftw3.h>
#include <malloc.h>
#include <math.h>
#include "Fft.h"



Fft *fft_Open(int blk){
  int n = 0;
  Fft *fft = (Fft *)malloc(sizeof(Fft));
  fft->blk = blk;
  fft->buf = (double *)malloc(sizeof(double)*blk);
  fft->wd = (double *)malloc(sizeof(double)*blk);
  fft->out = (fftw_complex *)fftw_malloc(sizeof(fftw_complex)*blk);
  fft_Clear(fft);
  for(n = 0; n < fft -> blk; n++){
    fft->wd[n] = 0.54 - 0.46 * cos((2 * M_PI * (double)n)/((double)blk - 1));
  }
  fft->plan = fftw_plan_dft_r2c_1d(blk,fft->buf,fft->out,FFTW_ESTIMATE);
  return(fft);
  

  
}

void fft_Close(Fft *fft){
  free(fft -> buf);
  fftw_free(fft -> out);
  free(fft->wd);
  free(fft);
  
}

void fft_Window(Fft *fft, double *ixx){
  int i = 0;
  for(i = 0; i < fft->blk; i++){
    fft->buf[i] = ixx[i] * fft->wd[i];
  }
  
  
}

void fft_Clear(Fft *fft)
{
  memset(fft->buf, 0, sizeof(double) * (fft-> blk));
  memset(fft->wd, 0 , sizeof(double) * (fft-> blk));
  memset(fft->out, 0 , sizeof(fftw_complex) * (fft -> blk));
  
}

void fft_Exec(Fft *fft, double *ixx){
  fft_Window(fft, ixx);
  fftw_execute(fft->plan);

}
