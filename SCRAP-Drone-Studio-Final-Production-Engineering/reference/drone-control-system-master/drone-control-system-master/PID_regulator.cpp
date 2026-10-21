#include "PID_regulator.h"

PID_regulator::PID_regulator() {
	
}


void PID_regulator::set_parameters(float Kp, float Ki, float Kd, float bias1) {
	this->Kp=Kp;
	this->Ki=Ki;
	this->Kd=Kd;
	this->bias=bias;
	this->error=0.0f;
	this->integral=0.0f;
	this->output=0.0f;
	this->integral_prior=0.0f;
	this->error_prior=0.0f;
}

float PID_regulator::Output(float input, float desired_value, float dt, bool stop_integration) {
	actual_value=input;
	error=desired_value-actual_value;
	if (stop_integration) {
		integral = integral_prior;
	} else {
		integral=integral_prior+error*dt;
	}
	derivative=(error-error_prior)/dt;
	output=(Kp*error+Ki*integral+Kd*derivative+bias);
	error_prior=error;
	integral_prior=integral;
	return output;
}

void PID_regulator::ResetID() {
	this->error=0.0f;
	this->error_prior=0.0f;
	this->integral=0.0f;
	this->integral_prior=0.0f;
}


void PID_regulator::ResetOutput() {
	this->error=0.0f;
	this->error_prior=0.0f;
	this->integral=0.0f;
	this->integral_prior=0.0f;
	this->output=0.0f;
}
