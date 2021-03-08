#ifndef fft_h
#define fft_h

typedef struct Fft{
  int blk;
  double *buf;
  double *wd;
  fftw_complex *out;
  fftw_plan plan;

} Fft;


Fft * fft_Open(int blk);

void fft_Window(Fft *fft, double *ixx);
void fft_Close(Fft *fft);
void fft_Clear(Fft *fft);
void fft_Exec(Fft *fft, double *ixx);


#endif
