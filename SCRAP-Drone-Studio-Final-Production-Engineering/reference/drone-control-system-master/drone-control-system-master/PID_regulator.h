/**
 * PID Regulator Class
 *
 * Implements a standard PID (Proportional-Integral-Derivative) controller
 * with anti-windup protection and output limiting capabilities.
 *
 * Features:
 * - Configurable PID gains (Kp, Ki, Kd)
 * - Optional bias term
 * - Integral windup prevention
 * - Reset capabilities for mode changes
 */
class PID_regulator {

	public:
	// State variables
	float error_prior;     // Previous error value
	float integral_prior;  // Previous integral value
	float error;           // Current error
	float actual_value;    // Current input value
	float integral;        // Current integral
	float derivative;      // Current derivative
	float output;          // Controller output
	float bias;            // Constant bias term

	// PID gains
	float Kp;  // Proportional gain
	float Ki;  // Integral gain
	float Kd;  // Derivative gain

	// Constructor
	PID_regulator();

	// Configuration
	void set_parameters(float Kp, float Ki, float Kd, float bias=0.0f);

	// Control functions
	float Output(float input, float desired_value, float dt, bool stop_integration=false);

	// Reset functions
	void ResetOutput();  // Reset all state variables
	void ResetID();      // Reset integral and derivative terms only
};