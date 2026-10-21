/**
 * Triple Filter Class
 *
 * Implements a cascaded filtering approach: Kalman → LPF → Kalman
 * Provides superior noise reduction for IMU sensor data by combining
 * the strengths of both Kalman filtering and low-pass filtering.
 *
 * Filter chain: Input → KF1 → LPF → KF2 → Output
 */
#include <KalmanFilter.h>
#include <LPF.h>

class TripleFilter {

    public:
    // Filter components
    KalmanFilter KF1, KF2;  // Two Kalman filters for pre and post LPF
    LPF LPF1;               // Low-pass filter in the middle

    // Filter outputs at each stage (for debugging)
    float kf1_out;   // Output of first Kalman filter
    float lpf_out;   // Output of low-pass filter
    float kf2_out;   // Output of second Kalman filter (final output)

    // Constructor
    TripleFilter();

    // Configuration
    void change_parameters(float Q, float R, float fc, float x_init);

    // Main filter function
    float Output(float x, float Ts);

};