#include "LPF.h"
#include <Arduino.h>

LPF::LPF() {
    this->y = 0;
}

float LPF::Output(float x, float Ts) {
    alpha = Ts/(Ts+(1/(2*PI*fc)));
    y=y+alpha*(x-y);
    return y;
}

void LPF::change_parameters(float fc, float initial_y) {
    this->fc = fc;
    this->y = initial_y;
}
