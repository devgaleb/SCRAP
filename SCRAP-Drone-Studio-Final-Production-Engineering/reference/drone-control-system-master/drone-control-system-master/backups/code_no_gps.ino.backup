#include <Arduino.h>
#include <PPMReader.h>
#include <KalmanFilter.h>
#include <PID_regulator.h>
#include <Adafruit_MPU6050.h>
#include <Servo.h>

const char comma[] PROGMEM = {","};  // use this form

// Servo stuff
Servo ESC_Servo_1, ESC_Servo_2, ESC_Servo_3, ESC_Servo_4;
int data1, data2, data3, data4;
int offset_servo1, offset_servo2, offset_servo3, offset_servo4;

// MPU stuff
Adafruit_MPU6050 mpu;

// RC stuff
#define kChannelNumber 6  // Number of channels
float channel_norm[12];
#define PIN_RECEIVER 3  // rc receiver PPM pin
PPMReader ppm(PIN_RECEIVER, kChannelNumber);
bool remote_turned_on = false;
bool remote_armed = false;
float thrust_rc = 0;
float pitch_rc = 0.5;
float roll_rc = 0.5;
float yaw_rc = 0.5;
float turnon_rc = 0.0;
unsigned long value_channel;

// time variables
unsigned long time_start, time_now, time_prev, time_elapsed;
float dt, timer_magnetometer;

// set up main data arrays
float acceleration[3];  // m/s^2
float angle_acc[2];  // rads
float angle[3];  // rads
float angle_deg[3];  // degs
float omega[3];  // rad/s
float speed[3] = {0.0f, 0.0f, 0.0f};  // m/s

float offset_acceleration[3] = {0.0f, 0.0f, 0.0f};
float offset_omega[3] = {0.0f, 0.0f, 0.0f};

KalmanFilter filter1, filter2, filter3, filter4,
             filter5, filter6, filter7, filter8;

#define  A_rot   1.0   // factor of real value to previous real value
#define  B_rot   0.0   // factor of real value to real control signal
#define  H_rot   1.0   // sprememba merjene vrednosti zaradi enote/drugo
#define  Q_rot   1.0   // Process noise (wind/driver input)
#define  R_rot   10.0   // sensor inaccuracy. more = more innacurate
#define  P_rot   0.0   // zacetni vrednosti
#define  x_rot   0.0   // zacetni vrednosti

#define  A_pos   1.0   // factor of real value to previous real value
#define  B_pos   0.0   // factor of real value to real control signal
#define  H_pos   1.0   // sprememba merjene vrednosti zaradi enote/drugo
#define  Q_pos   5.0   // Process noise (wind/driver input)
#define  R_pos   10.0   // sensor inaccuracy. more = more innacurate
#define  P_pos   0.0   // zacetni vrednosti
#define  x_pos   0.0   // zacetni vrednosti

PID_regulator pid1, pid2, pid3, pid4, pid6;

#define  Kp   0.02  // PID 2 (omega)
#define  Ki   0.0
#define  Kd   0.0

#define  Kp_r   2.0   // PID 1 (stopinje)
#define  Ki_r   500.0
#define  Kd_r   0.0

#define  Kp_6   0.0   // PID 3 (stopinje)
#define  Ki_6   0.0
#define  Kd_6   0.0

#define CALIBRATION_ITERATIONS 100

float desired_value1;
float output1;
float desired_value2;
float output2;
float desired_value3;
float output3;
float desired_value4;
float output4;
float desired_value6;
float output6;

sensors_event_t a, g, temp;

float F1m, F2m, F3m, F4m;

int pwm_1, pwm_2, pwm_3, pwm_4;

void setup() {
    ESC_Servo_1.attach(5);
    ESC_Servo_2.attach(6);
    ESC_Servo_3.attach(9);
    ESC_Servo_4.attach(11);

    ESC_Servo_1.write(0);
    ESC_Servo_2.write(0);
    ESC_Servo_3.write(0);
    ESC_Servo_4.write(0);

    Serial.begin(115200);
    Serial.setTimeout(150);

    delay(500);
    Serial.print(F("Init..."));

    offset_servo1 = 0;
    offset_servo2 = 0;
    offset_servo3 = 0;
    offset_servo4 = 0;

    // IMU stuff
    mpu.begin();

    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);  // 2,4,8,16
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);  // 250,500,1000,2000
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);  // 5,10,21,44,94,184,260 Hz

    // set up kalman filters
    filter1.change_parameters(A_pos, H_pos, Q_pos, R_pos, P_pos, x_pos);
    filter2.change_parameters(A_pos, H_pos, Q_pos, R_pos, P_pos, x_pos);
    filter3.change_parameters(A_pos, H_pos, Q_pos, R_pos, P_pos, x_pos);
    filter4.change_parameters(A_rot, H_rot, Q_rot, R_rot, P_rot, x_rot);
    filter5.change_parameters(A_rot, H_rot, Q_rot, R_rot, P_rot, x_rot);
    filter6.change_parameters(A_rot, H_rot, Q_rot, R_rot, P_rot, x_rot);

    // set up PIDs
    pid1.set_parameters(Kp, Ki, Kd);
    pid2.set_parameters(Kp, Ki, Kd);
    pid3.set_parameters(Kp_r, Ki_r, Kd_r);
    pid4.set_parameters(Kp_r, Ki_r, Kd_r);
    pid6.set_parameters(Kp_6, Ki_6, Kd_6);

    desired_value1 = 0;
    desired_value2 = 0;
    desired_value3 = 0;
    desired_value4 = 0;

    desired_value6 = 0;

    output1 = 0;
    output2 = 0;
    output3 = 0;
    output4 = 0;

    output6 = 0;

    offset_acceleration[0] = 0.79f;
    offset_acceleration[1]=-0.08f;
    offset_acceleration[2]=-0.82f;

    offset_omega[0]=-0.24f;
    offset_omega[1]=-0.02f;
    offset_omega[2]=-0.01f;

    //calibrate_IMU();
    channel_norm[0]=-1.0f;
    //Serial.print(F("Initialization complete, starting loop...\n"));

    time_start = micros();
    time_prev = time_start;
    time_elapsed = 0;
}

void loop() {
    get_time();
    get_imu_data(); 
    apply_kalman_filters();
    get_rc_data();
    calculate_PIDs();

    print_dt();
    //print_rc_data();
    //print_angle_deg();
    //print_omega_data();
    //print_acc_data();
    //print_propeller_thrust_data();
    print_pwm_data();
    //print_pid_data();

    //get_serial_commands();
    Serial.println(F(""));
}

void calibrate_IMU() {
    Serial.println(F("IMU cal..."));
    for (int i = 0; i < CALIBRATION_ITERATIONS; i++) {
        mpu.getEvent(&a, &g, &temp);
        offset_omega[0] += g.gyro.x;
        offset_omega[1] += g.gyro.y;
        offset_omega[2] += g.gyro.z;
        offset_acceleration[0] += a.acceleration.x;
        offset_acceleration[1] += a.acceleration.y;
        offset_acceleration[2] += a.acceleration.z;
        delay(10);
    }
    offset_omega[0] = offset_omega[0]/CALIBRATION_ITERATIONS;
    offset_omega[1] = offset_omega[1]/CALIBRATION_ITERATIONS;
    offset_omega[2] = offset_omega[2]/CALIBRATION_ITERATIONS;
    offset_acceleration[0] = offset_acceleration[0]/CALIBRATION_ITERATIONS;
    offset_acceleration[1] = offset_acceleration[1]/CALIBRATION_ITERATIONS;
    offset_acceleration[2] = offset_acceleration[2]/CALIBRATION_ITERATIONS+9.82f;
    print_offsets();
}


void get_time() {
    time_now = micros();
    time_elapsed = time_now-time_start;
    dt = (time_now - time_prev)*1e-6;  // s
    time_prev = time_now;
}


void calculate_PIDs() {
    desired_value3 = 45.0*(roll_rc-0.5);
    desired_value4 = 45.0*(pitch_rc-0.5);

    // PID 3 roll
    output3 = pid3.Output(angle_deg[0], 0, dt);

    // PID 4 pitch
    output4 = pid4.Output(angle_deg[1], 0, dt);

    // PID 1 omega roll
    output1 = pid1.Output(omega[0],-output3,dt);

    // PID 2 omega pitch
    output2 = pid2.Output(omega[1],output4,dt);

    //desired_value6 = 10*(yaw_rc-0.5);

    // PID 6 yaw
    //output6 = pid6.Output(omega[2], desired_value6, dt);
    output6 = 0;

    F1m = (-output1-output2);  // Force magnitude
    F2m = (+output1-output2);
    F3m = (-output1+output2);
    F4m = (+output1+output2);

    F1m += (+thrust_rc -output6);  // Force magnitude
    F2m += (+thrust_rc +output6);
    F3m += (+thrust_rc +output6);
    F4m += (+thrust_rc -output6);

    F1m += offset_servo1;  // Force magnitude
    F2m += offset_servo2;
    F3m += offset_servo3;
    F4m += offset_servo4;


    if (F1m < 0) {F1m = 0;}
    if (F2m < 0) {F2m = 0;}
    if (F3m < 0) {F3m = 0;}
    if (F4m < 0) {F4m = 0;}

    if (F1m > 1) {F1m = 1;}
    if (F2m > 1) {F2m = 1;}
    if (F3m > 1) {F3m = 1;}
    if (F4m > 1) {F4m = 1;}


    if (!remote_turned_on) {
        F1m = 0; F2m = 0; F3m = 0; F4m = 0;
    }

    if (!remote_armed) {
        F1m = 0; F2m = 0; F3m = 0; F4m = 0;
    }

    if (turnon_rc < 0.5f) {
        F1m = 0; F2m = 0; F3m = 0; F4m = 0;
    }

    pwm_1 = (int)(F1m*255 + 0.5);
    pwm_2 = (int)(F2m*255 + 0.5);
    pwm_3 = (int)(F3m*255 + 0.5);
    pwm_4 = (int)(F4m*255 + 0.5);

    apply_pwm_to_propellers();
}

void get_imu_data() {
    mpu.getEvent(&a, &g, &temp);

    omega[0] = (g.gyro.x-offset_omega[0]);
    omega[1] = (g.gyro.y-offset_omega[1]);
    omega[2] = (g.gyro.z-offset_omega[2]);

    acceleration[0] = (a.acceleration.x-offset_acceleration[0]);
    acceleration[1] = (a.acceleration.y-offset_acceleration[1]);
    acceleration[2] = (a.acceleration.z-offset_acceleration[2]);

    angle_acc[0] = atan2(acceleration[1], sqrt(acceleration[2] * acceleration[2] + acceleration[0] * acceleration[0]));
    angle_acc[1] = atan2(acceleration[0], sqrt(acceleration[2] * acceleration[2] + acceleration[1] * acceleration[1]));

    angle[0] = (0.95f * (angle[0] + omega[0] * dt)) + (0.05f * angle_acc[0]);
    angle[1] = (0.95f * (angle[1] + omega[1] * dt)) + (0.05f * angle_acc[1]);
    // angle[2] = omega[2]*dt+angle[2];
    angle[2] = 0.0f;

    angle_deg[0] = wrap(r2d(angle[0]));
    angle_deg[1] = wrap(r2d(angle[1]));
    angle_deg[2] = wrap(r2d(angle[2]));

    if (abs(angle[0]) < 1.0) {
        angle[0] = 0;
    }
    if (abs(angle[1]) < 1.0) {
        angle[1] = 0;
    }
}

void apply_pwm_to_propellers() {
    data1 = map(pwm_1, 0, 256, 1000, 2000);
    data2 = map(pwm_2, 0, 256, 1000, 2000);
    data3 = map(pwm_3, 0, 256, 1000, 2000);
    data4 = map(pwm_4, 0, 256, 1000, 2000);

    ESC_Servo_1.write(data1);
    ESC_Servo_2.write(data2);
    ESC_Servo_3.write(data3);
    ESC_Servo_4.write(data4);
}

void apply_kalman_filters() {
    acceleration[0] = filter1.Output(acceleration[0]);
    acceleration[1] = filter2.Output(acceleration[1]);
    acceleration[2] = filter3.Output(acceleration[2]);

    omega[0] = filter4.Output(omega[0]);
    omega[1] = filter5.Output(omega[1]);
    omega[2] = filter6.Output(omega[2]);
}


void get_rc_data() {
    for (int channel = 0; channel < kChannelNumber; channel++) {
        value_channel = ppm.rawChannelValue(channel+1);
        channel_norm[channel] = ((float)value_channel - 1000)/1000;
    }

    if (!remote_turned_on) {
        if (channel_norm[0] != -1.0f) {
            remote_turned_on = true;
        }
    }

    if (!remote_armed) {
        if (remote_turned_on == true) {
            if (channel_norm[2] < 0.1) {
                if (channel_norm[4] < 0.5) {
                    remote_armed = true;
                }
            }
        }
    }

    roll_rc = channel_norm[0];
    pitch_rc = channel_norm[1];
    thrust_rc = channel_norm[2];
    yaw_rc = channel_norm[3];
    turnon_rc = channel_norm[4];
}

float r2d(float degrees) {
    return (degrees * 57.2958f);
}

void get_serial_commands() {
    if (Serial.available() > 0) {
        String incoming = Serial.readString();
        if (incoming == "reset") {
        }
    }
}

static float wrap(float angle) {
    while (angle > +180) angle -= 360;
    while (angle < -180) angle += 360;
    return angle;
}

void print_omega_data() {
    Serial.print(F("OmgX:"));
    Serial.print(omega[0]);
    Serial.print(F(",OmgY:"));
    Serial.print(omega[1]);
    Serial.print(F(",OmgZ:"));
    Serial.print(omega[2]);
    delimiter();
}

void print_acc_data() {
    Serial.print(F("aX:"));
    Serial.print(acceleration[0]);
    Serial.print(F(",aY:"));
    Serial.print(acceleration[1]);
    Serial.print(F(",aZ:"));
    Serial.print(acceleration[2]);
    delimiter();
}

void print_raw_acc_data() {
    Serial.print(F("aXr:"));
    Serial.print(a.acceleration.x);
    Serial.print(F(",aYr:"));
    Serial.print(a.acceleration.y);
    Serial.print(F(",aZr:"));
    Serial.print(a.acceleration.z);
    delimiter();
}

void print_rc_data() {
    for (int i = 0; i < (kChannelNumber); i++) {
        Serial.print(F("RC"));
        Serial.print(i+1);
        Serial.print(F(":"));
        Serial.print(channel_norm[i],4);
        delimiter();
    }
    Serial.print(F("REMOTE:"));
    Serial.print(remote_turned_on);
    delimiter();
}

void print_angle_deg() {
    Serial.print(F("AngX:"));
    Serial.print(angle_deg[0]);
    Serial.print(F(",AngY:"));
    Serial.print(angle_deg[1]);
    Serial.print(F(",AngZ:"));
    Serial.print(angle_deg[2]);
    delimiter();
}

void print_pwm_data() {
    Serial.print(F("pwm1:"));
    Serial.print(pwm_1);
    Serial.print(F(",pwm2:"));
    Serial.print(pwm_2);
    Serial.print(F(",pwm3:"));
    Serial.print(pwm_3);
    Serial.print(F(",pwm4:"));
    Serial.print(pwm_4);
    delimiter();
}

void print_propeller_thrust_data() {
    Serial.print(F("F1m:"));
    Serial.print(F1m);
    Serial.print(F(",F2m:"));
    Serial.print(F2m);
    Serial.print(F(",F3m:"));
    Serial.print(F3m);
    Serial.print(F(",F4m:"));
    Serial.print(F4m);
    delimiter();
}

void print_offsets() {
    Serial.println(F("Offsets:"));
    Serial.print(offset_acceleration[0]);
    delimiter();
    Serial.print(offset_acceleration[1]);
    delimiter();
    Serial.print(offset_acceleration[2]);
    Serial.println(F(","));
    Serial.println(F("Offsets omega:"));
    Serial.print(offset_omega[0]);
    delimiter();
    Serial.print(offset_omega[1]);
    delimiter();
    Serial.print(offset_omega[2]);
    Serial.println(F(","));
}

void print_desired_values() {
    Serial.print(F("desired_roll:"));
    Serial.print(desired_value3);
    Serial.print(F(",desired_pitch:"));
    Serial.print(desired_value4);
    Serial.print(F(","));
}

void print_pid_data() {
    Serial.print(F("pid1:"));
    Serial.print(output1);
    Serial.print(F(",pid2:"));
    Serial.print(output2);
    Serial.print(F(",pid3:"));
    Serial.print(output3);
    Serial.print(F(",pid4:"));
    Serial.print(output4);
    Serial.print(F(","));
}

void print_dt() {
    Serial.print(F("dt:"));
    Serial.print(dt);
    Serial.print(F(","));
}

void delimiter() {
    Serial.print(comma[0]);
}
