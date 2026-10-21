/**
 * Kalman Filter Class
 *
 * Implements a simple 1D Kalman filter for sensor fusion and noise reduction.
 * Uses constant velocity model (A=1, H=1) for applications like altitude estimation.
 *
 * Process: x(k) = x(k-1) + w(k-1)
 * Measurement: z(k) = x(k) + v(k)
 *
 * Where w ~ N(0,Q) and v ~ N(0,R)
 */
class KalmanFilter {

    public:
    // Filter parameters
    float Q, R, P, x, K;  // Process noise, measurement noise, error covariance, state, kalman gain
    float A=1;            // State transition matrix (constant velocity model)
    float H=1;            // Measurement matrix

    // Constructor
    KalmanFilter();

    // Main filter function
    float Output(float input);

    // Configuration
    void change_parameters(float Q, float R, float initial_x);

};