#include "KalmanFilter.h"

KalmanFilter::KalmanFilter() {
}

float KalmanFilter::Output(float input) {
    // H=1, A=1
    // do a prediction
    x = A * x;
    P = A * P * A + Q;

    // calculate the Kalman gain
    K = P * H / (H * P * H + R);



    // correct
    x = x + K * (input - H * x);
    P = (1 - K * H) * P;

    return x;
}

void KalmanFilter::change_parameters(float Q, float R, float initial_x) {
    this->Q = Q;
    this->R = R;
    this->x = initial_x;
}
