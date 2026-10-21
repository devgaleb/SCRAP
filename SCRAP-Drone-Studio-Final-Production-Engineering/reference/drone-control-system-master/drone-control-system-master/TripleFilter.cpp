#include <Arduino.h>
#include "TripleFilter.h"

TripleFilter::TripleFilter(){
};

float TripleFilter::Output(float x, float Ts) {
	kf1_out = KF1.Output(x);
	lpf_out = LPF1.Output(kf1_out,Ts);
	kf2_out = KF2.Output(lpf_out);
	return kf2_out;
}

void TripleFilter::change_parameters(float Q, float R, float fc, float x_init) {
	this->KF1.change_parameters(Q,R,x_init);
	this->KF2.change_parameters(Q,R,x_init);
	this->LPF1.change_parameters(fc,x_init);
}