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

int main(int ac, char** av)
{

  int i = 0;




  Opt* op = opt_open(ac, av, av[0]);
  char* ifile = opt_char(op, "-i", NULL, "入力ファイル");
  if(!ifile) errExit("入力ファイルが指定されていません。\n");
  int blk = opt_int(op, "-b", 512, "バッファ長");

  /*time計測用*/
  clock_t start, stop;
  double ms;

  float savg = 0;
  float aavg = 0;














  SF_INFO si;


  SNDFILE* fpi = sf_open(ifile, SFM_READ, &si);
  if(!fpi) errExit("入力サンドファイル オープン失敗。\n");





  /*ptsにblkを代入*/
  int pts = 0;


#ifdef PAFLOAT
  PaSampleFormat pafmt = paFloat32;
  float* ixx = fm_1D_create(blk*si.channels);
  float* iyy = fm_1D_create(blk*si.channels);





#else
  PaSampleFormat pafmt = paInt32;
  int* ixx = im_1D_create(blk*si.channels);
  int* iyy = im_1D_create(blk*si.channels);





#endif

  //memsetする
  memset(ixx,0,sizeof(float) * blk);
  memset(iyy,0,sizeof(float) * blk);

















  opt_prfp(op,stderr);



  int cnt = 0;

  start = clock();
  while(1){


    pts = sf_readf_float(fpi,ixx, blk);





    for(i=0; i<blk; i++){
      iyy[i] = ixx[i] * ixx[i];
      savg += iyy[i];
    }


    cnt ++;

    if(pts != blk) break;
  }


  savg = savg/(cnt * blk);
  aavg = sqrt(savg);


  stop = clock();

  ms = (double)(stop - start)/CLOCKS_PER_SEC;

  fprintf(stderr,"秒数 = %f秒\n",ms);
  fprintf(stderr,"二乗平均振幅 = %f\n",savg);
  fprintf(stderr,"RMS振幅 = %f\n",aavg);






  opt_close(op);
  sf_close(fpi);


#ifdef PAFLOAT
  fm_1D_free(ixx);
  fm_1D_free(iyy);

#else
  im_1D_free(ixx);
  im_1D_free(iyy);

#endif
  return 0;
}
