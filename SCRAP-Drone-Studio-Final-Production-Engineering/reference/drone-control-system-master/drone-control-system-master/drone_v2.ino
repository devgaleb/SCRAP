/*
 * Drone Control System v2.0
 *
 * A complete quadcopter flight control system for Arduino featuring:
 * - IMU sensor fusion (MPU-9255)
 * - Barometric altitude control (BMP280)
 * - Cascaded PID control for stability
 * - Multiple flight modes (Acro, Normal, Altitude Hold)
 * - PPM RC receiver support
 *
 * Hardware: Arduino Mega 2560 recommended
 * Sensors: MPU-9255 IMU + BMP280 barometer
 * RC: PPM receiver with 6+ channels
 *
 * Author: Miha Smrekar
 * License: MIT
 * Repository: https://github.com/username/drone-control-arduino
 */

#include <PPMReader.h>
#include <PID_regulator.h>
#include <Servo.h>
#include <TripleFilter.h>
#include <BMP280_DEV.h>

// Configuration flags
#define DEBUGGING_MODE 0  // Set to 1 for debugging output

const char comma[] PROGMEM = {","};

// BMP280
BMP280_DEV bmp280;
float pressure, temperature, altitude, altitude_prev, vertical_speed_BMP;
// MPU9255
#include <Wire.h>

#define MPU9250_ADDRESS 0x68
#define MAG_ADDRESS 0x0C
#define GYRO_FULL_SCALE_250_DPS 0x00 
#define GYRO_FULL_SCALE_500_DPS 0x08
#define GYRO_FULL_SCALE_1000_DPS 0x10
#define GYRO_FULL_SCALE_2000_DPS 0x18
#define ACC_FULL_SCALE_2_G 0x00 
#define ACC_FULL_SCALE_4_G 0x08
#define ACC_FULL_SCALE_8_G 0x10
#define ACC_FULL_SCALE_16_G 0x18

#define GYRO_RANGE 500/32768*0.01745329251994 // rad/s
#define ACC_RANGE 8/32768*9.82 // m/s^2

volatile bool intFlag=false;

int16_t ax,ay,az,gx,gy,gz,mx,my,mz;

// Servo stuff
Servo ESC_Servo_1, ESC_Servo_2, ESC_Servo_3, ESC_Servo_4;

// RC stuff
#define NUMCHANNELS 6  // Number of channels
#define PIN_RECEIVER 2  // rc receiver PPM pin

PPMReader ppm(PIN_RECEIVER, NUMCHANNELS);
float channel_norm[NUMCHANNELS];
bool remote_armed = false;
int remote_status = -2;
int channel;
float thrust_rc = 0;
float pitch_rc = 0.5;
float roll_rc = 0.5;
float yaw_rc = 0.5;
int value_channel;
float last_flight_mode = -2;

// time variables

unsigned long time_now, time_prev;
float dt;
int freq, counter;

// time pressure variables
unsigned long time_now_pressure, time_prev_pressure;
float dt_pressure;



// set up main data arrays
float acceleration[3];  // m/s^2
float omega[3];  // rad/s
float omega_prime_z;
float omega_prev_z;

float angle_acc[2];  // rads
float angle[3];  // rads
float angle_deg[3];  // degs

float vertical_acceleration_imu;
float vertical_speed;
float vertical_speed_imu;

float offset_acceleration[3] = {-2.12184054,-8.72099018,1.94126243};
float offset_omega[3] = {0.04509204,0.01935469,0.01090463};

// Omega filter
#define  Q_w   0.5   // Process noise (wind/driver input)
#define  R_w   2.5e-7   // sensor inaccuracy. more = more innacurate

// Acceleration filter
#define  Q_a   0.5   // Process noise (wind/driver input)
#define  R_a   2.5e-7   // sensor inaccuracy. more = more innacurate

// LPF
LPF LPF_roll_rc,LPF_pitch_rc,LPF_thrust_rc,LPF_yaw_rc;
#define f_c 100 // Hz, cutoff frequency
#define f_c_rc 4 // Hz, cutoff freuqency RC

LPF LPF_alt;
#define f_c_alt 1

// TripleFilter
TripleFilter filt1,filt2,filt3,filt4,filt5,filt6;

// KalmanFilter
KalmanFilter KF_altitude;
#define  Q_alt   0.008   // Process noise (wind/driver input)
#define  R_alt   1e4  // sensor inaccuracy. more = more innacurate

// PID
PID_regulator pid1, pid2, pid3, pid4, pid5, pid6, pid7;
bool stop_integration_3, stop_integration_4;

// PITCH
#define  Kp_w_pitch   0.0003 // PID 1,2 (stopnja B) (omega)
#define  Ki_w_pitch   0.0006
#define  Kd_w_pitch   0.000025

#define  Kp_theta_pitch   5.0   // PID 3,4 (stopnja A) (stopinje)
#define  Ki_theta_pitch   8.0
#define  Kd_theta_pitch   0.05

// ROLL
#define  Kp_w_roll   0.0003 // PID 1,2 (stopnja B) (omega)
#define  Ki_w_roll   0.0006
#define  Kd_w_roll   0.000015

#define  Kp_theta_roll   5.0   // PID 3,4 (stopnja A) (stopinje)
#define  Ki_theta_roll   8.0
#define  Kd_theta_roll   0.05

// YAW
#define  Kp_w_yaw   6   // PID 6 - yaw (omega)
#define  Ki_w_yaw   3
#define  Kd_w_yaw   0

#define  Kp_wp_yaw   0.00028   // PID 6 - yaw (omega prime)
#define  Ki_wp_yaw   0
#define  Kd_wp_yaw   0

// ALTITUDE
#define  Kp_altitude   0.3   // PID ALTITUDE
#define  Ki_altitude   1.2
#define  Kd_altitude   0.005

float setpoint_1,setpoint_2,setpoint_3,setpoint_4,setpoint_5,setpoint_6,setpoint_7 = 0;
float out_1,out_2,out_3,out_4,out_5,out_6, out_7 = 0;

// MAIN OUTPUTS

#define MAX_DEGREES 30 // Max Degrees (Normal mode)
#define MAX_DPS_YAW 180 // Degrees Per Second
#define MAX_DPS_PITCH_ROLL 180 // Degrees Per Second (Acro mode)
#define MAX_VERT_SPEED 0.25 // (Only Altitude hold mode)

#define R2DCONST 57.29578

float F1m, F2m, F3m, F4m;
int pwm_1, pwm_2, pwm_3, pwm_4;

void setup() {
    ESC_Servo_1.attach(3);
    ESC_Servo_2.attach(5);
    ESC_Servo_3.attach(9);
    ESC_Servo_4.attach(11);

    Serial.begin(500000);

    if (!DEBUGGING_MODE) {

        Serial.print(F("Starting ESC calibration sequence...\n"));

        ESC_Servo_1.write(2000);
        ESC_Servo_2.write(2000);
        ESC_Servo_3.write(2000);
        ESC_Servo_4.write(2000);

        delay(5000);

        ESC_Servo_1.write(1000);
        ESC_Servo_2.write(1000);
        ESC_Servo_3.write(1000);
        ESC_Servo_4.write(1000);

        delay(5000);
    } else {
        ESC_Servo_1.write(0);
        ESC_Servo_2.write(0);
        ESC_Servo_3.write(0);
        ESC_Servo_4.write(0);
    }
    

    //int sensorValue = analogRead(A7);
    //float voltage = sensorValue * (5.0/1023.0) * 3.518816f;

    // IMU
    Serial.print(F("Init IMU...\n"));

    // Set accelerometers low pass filter at 5Hz
    I2CwriteByte(MPU9250_ADDRESS,29,0x06);
    // Set gyroscope low pass filter at 5Hz
    I2CwriteByte(MPU9250_ADDRESS,26,0x06);
    // Configure gyroscope range
    I2CwriteByte(MPU9250_ADDRESS,27,GYRO_FULL_SCALE_500_DPS);
    // Configure accelerometers range
    I2CwriteByte(MPU9250_ADDRESS,28,ACC_FULL_SCALE_8_G);
    // Set by pass mode for the magnetometers
    I2CwriteByte(MPU9250_ADDRESS,0x37,0x02);
    // Request continuous magnetometer measurements in 16 bits
    I2CwriteByte(MAG_ADDRESS,0x0A,0x16);

    // set up kalman filters
    filt1.change_parameters(Q_a, R_a, f_c, 0);
    filt2.change_parameters(Q_a, R_a, f_c, 0);
    filt3.change_parameters(Q_a, R_a, f_c, 0);
    
    filt4.change_parameters(Q_w, R_w, f_c, 0);
    filt5.change_parameters(Q_w, R_w, f_c, 0);
    filt6.change_parameters(Q_w, R_w, f_c, 0);

    LPF_yaw_rc.change_parameters(f_c_rc,0.5);
    LPF_thrust_rc.change_parameters(f_c_rc,0);
    LPF_roll_rc.change_parameters(f_c_rc,0.5);
    LPF_pitch_rc.change_parameters(f_c_rc,0.5);
    
    // set up PIDs
    pid1.set_parameters(Kp_w_roll, Ki_w_roll, Kd_w_roll);
    pid2.set_parameters(Kp_w_pitch, Ki_w_pitch, Kd_w_pitch);
    pid3.set_parameters(Kp_theta_roll, Ki_theta_roll, Kd_theta_roll);
    pid4.set_parameters(Kp_theta_pitch, Ki_theta_pitch, Kd_theta_pitch);
    pid5.set_parameters(Kp_altitude, Ki_altitude, Kd_altitude);
    pid6.set_parameters(Kp_w_yaw, Ki_w_yaw, Kd_w_yaw);
    pid7.set_parameters(Kp_wp_yaw, Ki_wp_yaw, Kd_wp_yaw);

    // BMP280 Barometer
    Serial.print(F("initializing BMP"));
    if (!bmp280.begin(BMP280_I2C_ALT_ADDR)) {
        while (!bmp280.begin(BMP280_I2C_ALT_ADDR)) {};
    }
    bmp280.setPresOversampling(OVERSAMPLING_X1);    // Set the pressure oversampling to X4
    bmp280.setTempOversampling(OVERSAMPLING_X1);    // Set the temperature oversampling to X1
    bmp280.setIIRFilter(IIR_FILTER_OFF);              // Set the IIR filter to setting 4
    bmp280.setTimeStandby(TIME_STANDBY_05MS);     // Set the standby time to 2 seconds
    bmp280.startNormalConversion();                 // Start BMP280 continuous conversion in NORMAL_MODE

    // get initial altitude
    for(int i = 0; i<150; i++) {
        bmp280.getMeasurements(temperature, pressure, altitude);
        delay(30);
    }

    KF_altitude.change_parameters(Q_alt,R_alt,altitude);
    LPF_alt.change_parameters(f_c_alt,altitude);
    altitude_prev = altitude;
    
    //calibrate();

    if (!DEBUGGING_MODE) {
        Serial.print(F("Waiting for transmitter... "));
        while (get_rc_status() != 1) {
            Serial.print(F(" "));
            Serial.print(get_rc_status());
            get_rc_data();
            delay(100);
        }
        Serial.print(F("Transmitter detected, starting loop!\n"));
    }
    
    time_prev = micros();
    time_prev_pressure = micros();
}

void loop() {
    get_imu_data();
    get_pressure_data();
    get_rc_data();
    calculate_vertical_speed();
    calculate_PIDs();
    get_time();
    apply_pid_to_pwm();

    if (remote_armed) {
        apply_pwm_to_propellers();
    } else {
        ESC_Servo_1.writeMicroseconds(1000);
        ESC_Servo_2.writeMicroseconds(1000);
        ESC_Servo_3.writeMicroseconds(1000);
        ESC_Servo_4.writeMicroseconds(1000);
    }
    
    if (DEBUGGING_MODE) {
        counter += 1;
        print_stuff();
        if (counter > 500) {
            counter = 0;
            //print_stuff();
        }
    }
}

void print_stuff() {
    //print_dt();
    //print_frequency();
    print_rc_data();
    //print_processed_rc_data();
    //print_angle_deg();
    //print_microseconds_data();
    //print_omega_data(); // raw rot. velocity
    //print_acc_raw();
    //print_acc_data(); // raw acceleration
    //print_propeller_thrust_data();
    //print_pwm_data();
    //print_pid_data();
    //print_setpoints();
    //print_raw_acc_data();
    //print_pressure_data();
    //print_angle_rad();
    //print_vertical_speed();
    //get_serial_commands();
    Serial.println(F(""));
}

void calibrate() {
    Serial.println(F("Calibrated!"));
    get_imu_data_raw();
    offset_omega[0] = omega[0];
    offset_omega[1] = omega[1];
    offset_omega[2] = omega[2];

    offset_acceleration[0] = acceleration[0];
    offset_acceleration[1] = acceleration[1];
    offset_acceleration[2] = 9.82+acceleration[2];

    int num_iters = 5000;

    for (int i=0; i<num_iters; i++) {
        get_imu_data_raw();
        print_acc_data();
        print_omega_data();

        offset_omega[0] = omega[0]+offset_omega[0];
        offset_omega[1] = omega[1]+offset_omega[1];
        offset_omega[2] = omega[2]+offset_omega[2];

        offset_acceleration[0] = acceleration[0]+offset_acceleration[0];
        offset_acceleration[1] = acceleration[1]+offset_acceleration[1];
        offset_acceleration[2] = 9.82+acceleration[2]+offset_acceleration[2];
        
        Serial.println(F(""));
    }

    offset_omega[0] = offset_omega[0]/num_iters;
    offset_omega[1] = offset_omega[1]/num_iters;
    offset_omega[2] = offset_omega[2]/num_iters;

    offset_acceleration[0] = offset_acceleration[0]/num_iters;
    offset_acceleration[1] = offset_acceleration[1]/num_iters;
    offset_acceleration[2] = offset_acceleration[2]/num_iters;

    Serial.println(F("Calibrated!"));

    print_offsets();
}

float derivative(float prev_y, float next_y, float Ts) {
    return (next_y-prev_y)/Ts;
}


void get_time() {
    time_now = micros();
    dt = (time_now - time_prev)*1e-6;  // s
    time_prev = time_now;
    freq = 1/dt;
}

void get_time_pressure() {
    time_now_pressure = micros();
    dt_pressure = (time_now_pressure - time_prev_pressure)*1e-6;  // s
    time_prev_pressure = time_now_pressure;
}


void calculate_PIDs() {
    if (remote_armed == true) {
        if (abs(out_3) > Kp_theta_roll*MAX_DEGREES*2) {
            stop_integration_3 = true;
        } else {
            stop_integration_3 = false;
        }
        if (abs(out_4) > Kp_theta_pitch*MAX_DEGREES*2) {
            stop_integration_4 = true;
        } else {
            stop_integration_4 = false;
        }
        
        if (flight_mode_change() == 1) {
            Serial.println(F("Flight mode changed!\n"));
            pid1.ResetID();
            pid2.ResetID();
            pid3.ResetID();
            pid4.ResetID();
            pid5.ResetID();
            pid6.ResetID();
            pid7.ResetID();
        }
        
        if (get_flight_mode() == 1 || get_flight_mode() == 2) {
            // Normal mode or Altitude hold mode
            setpoint_3 = MAX_DEGREES*(roll_rc-0.5)*2;
            setpoint_4 = MAX_DEGREES*(pitch_rc-0.5)*2;
            
            // PID 3 roll
            out_3 = pid3.Output(-angle_deg[0], -setpoint_3, dt, stop_integration_3);
            // PID 4 pitch
            out_4 = pid4.Output(angle_deg[1], setpoint_4, dt, stop_integration_4);

            // PID 1 omega roll
            out_1 = pid1.Output(r2d(-omega[0]), out_3, dt);
            // PID 2 omega pitch
            out_2 = pid2.Output(r2d(omega[1]), out_4, dt);

        } else if (get_flight_mode() == 0) {
            // Acro mode
            out_3 = 0;
            out_4 = 0;

            setpoint_1 = MAX_DPS_PITCH_ROLL*(roll_rc-0.5)*2;
            setpoint_2 = MAX_DPS_PITCH_ROLL*(pitch_rc-0.5)*2;
            
            // PID 1 omega roll
            out_1 = pid1.Output(r2d(-omega[0]), -setpoint_1, dt);
            // PID 2 omega pitch
            out_2 = pid2.Output(r2d(omega[1]), setpoint_2, dt);

        }

        if (get_flight_mode() == 0 || get_flight_mode() == 1) {
            out_5 = thrust_rc;
        } else {
            setpoint_5 = MAX_VERT_SPEED*(thrust_rc-0.5)*2;
            out_5 = pid5.Output(vertical_speed,setpoint_5,dt);
        }

        setpoint_6 = MAX_DPS_YAW*(yaw_rc-0.5)*2;

        // PID 6 yaw (All modes)
        out_6 = pid6.Output(r2d(omega[2]), -setpoint_6, dt);
        out_7 = pid7.Output(omega_prime_z, out_6, dt);
        //out_6 =  0.2f*(yaw_rc-0.5)*2;

    } else {
        pid1.ResetOutput();
        pid2.ResetOutput();
        pid3.ResetOutput();
        pid4.ResetOutput();
        pid6.ResetOutput();
        pid7.ResetOutput();
        out_1 = 0;
        out_2 = 0;
        out_3 = 0;
        out_4 = 0;
        out_6 = 0;
        out_7 = 0;
    }
}

void apply_pid_to_pwm() {

    F1m = (-out_1-out_2);  // Force magnitude
    F2m = (+out_1-out_2);
    F3m = (-out_1+out_2);
    F4m = (+out_1+out_2);

    F1m += (+out_5 -out_7);  // Force magnitude
    F2m += (+out_5 +out_7);
    F3m += (+out_5 +out_7);
    F4m += (+out_5 -out_7);

    if (F1m < 0) {F1m = 0;}
    if (F2m < 0) {F2m = 0;}
    if (F3m < 0) {F3m = 0;}
    if (F4m < 0) {F4m = 0;}

    if (F1m > 1) {F1m = 1;}
    if (F2m > 1) {F2m = 1;}
    if (F3m > 1) {F3m = 1;}
    if (F4m > 1) {F4m = 1;}

    if (!remote_armed) {
        F1m = 0; F2m = 0; F3m = 0; F4m = 0;
    }

    pwm_1 = static_cast<int>(F1m*255 + 0.5);
    pwm_2 = static_cast<int>(F2m*255 + 0.5);
    pwm_3 = static_cast<int>(F3m*255 + 0.5);
    pwm_4 = static_cast<int>(F4m*255 + 0.5);
}


void get_imu_data_raw() {
    // Read accelerometer and gyroscope
    uint8_t Buf[14];
    I2Cread(MPU9250_ADDRESS,0x3B,14,Buf);

    // Accelerometer
    ax=Buf[0]<<8 | Buf[1];
    ay=Buf[2]<<8 | Buf[3];
    az=Buf[4]<<8 | Buf[5];
    
    // Gyroscope
    gx=Buf[8]<<8  | Buf[9];
    gy=Buf[10]<<8 | Buf[11];
    gz=Buf[12]<<8 | Buf[13];

    // magnetometer
    uint8_t ST1;
    I2Cread(MAG_ADDRESS,0x02,1,&ST1);

    // Read magnetometer data 
    uint8_t Mag[7];
    I2Cread(MAG_ADDRESS,0x03,7,Mag);
    // Magnetometer
    mx=-(Mag[3]<<8 | Mag[2]);
    my=-(Mag[1]<<8 | Mag[0]);
    mz=-(Mag[5]<<8 | Mag[4]);

    omega[0] = -(float)gy*GYRO_RANGE;
    omega[1] = (float)gx*GYRO_RANGE;
    omega[2] = (float)gz*GYRO_RANGE;

    acceleration[0] = (float)ay*ACC_RANGE;
    acceleration[1] = (float)ax*ACC_RANGE;
    acceleration[2] = -(float)az*ACC_RANGE;
}

void get_imu_data() {
    get_imu_data_raw();

    //subtract offset
    omega[0] = omega[0] - offset_omega[0];
    omega[1] = omega[1] - offset_omega[1];
    omega[2] = omega[2] - offset_omega[2];

    //subtract acc
    acceleration[0] = acceleration[0] - offset_acceleration[0];
    acceleration[1] = acceleration[1] - offset_acceleration[1];
    acceleration[2] = acceleration[2] - offset_acceleration[2];

    // APPLY FILT
    acceleration[0] = filt1.Output(acceleration[0],dt);
    acceleration[1] = filt2.Output(acceleration[1],dt);
    acceleration[2] = filt3.Output(acceleration[2],dt);

    omega[0] = filt4.Output(omega[0],dt);
    omega[1] = filt5.Output(omega[1],dt);
    omega[2] = filt6.Output(omega[2],dt);

    // Get omega prime z (yaw)
    omega_prime_z = derivative(omega[2],omega_prev_z,dt);
    omega_prev_z = omega[2];

    angle_acc[0] = atan2(acceleration[1], sqrt(acceleration[2] * acceleration[2] + acceleration[0] * acceleration[0]));
    angle_acc[1] = atan2(acceleration[0], sqrt(acceleration[2] * acceleration[2] + acceleration[1] * acceleration[1]));

    angle[0] = (0.99f * (angle[0] + omega[0] * dt)) + (0.01f * angle_acc[0]);
    angle[1] = (0.99f * (angle[1] + omega[1] * dt)) + (0.01f * angle_acc[1]);
    angle[2] = 0.0f;

    angle_deg[0] = wrap(r2d(angle[0]));
    angle_deg[1] = wrap(r2d(angle[1]));
    angle_deg[2] = wrap(r2d(angle[2]));
}


void calculate_vertical_speed() {
    vertical_acceleration_imu =  -(acceleration[2]*cos(angle[0])*cos(angle[1]) - acceleration[0]*sin(angle[1]) - acceleration[1]*cos(angle[1])*sin(angle[0])+9.82);
    vertical_speed_imu = vertical_speed + vertical_acceleration_imu*dt;
    vertical_speed = 0.98*vertical_speed_imu+0.02*vertical_speed_BMP;
}

void get_pressure_data() {
    if (bmp280.dataReady()) {
        bmp280.getCurrentMeasurements(temperature,pressure,altitude);
        get_time_pressure();
        //Serial.print(F("f_pressure:"));
        //Serial.print(1/dt_pressure);
        //Serial.print(F(",alt:"));
        //Serial.print(altitude);
        altitude = KF_altitude.Output(altitude);
        //altitude = LPF_alt.Output(altitude,dt_pressure);
        //Serial.print(F(",alt_f:"));
        //Serial.print(altitude);
        //Serial.print(F(","));
        //Serial.println(F(""));
        vertical_speed_BMP = (altitude - altitude_prev)/dt_pressure; // m/s
        altitude_prev = altitude;
    }
}


void apply_pwm_to_propellers() {
    if (!DEBUGGING_MODE) {
        ESC_Servo_1.writeMicroseconds(map(pwm_1, 0, 256, 1000, 2000));
        ESC_Servo_2.writeMicroseconds(map(pwm_2, 0, 256, 1000, 2000));
        ESC_Servo_3.writeMicroseconds(map(pwm_3, 0, 256, 1000, 2000));
        ESC_Servo_4.writeMicroseconds(map(pwm_4, 0, 256, 1000, 2000));
    } else {
        ESC_Servo_1.writeMicroseconds(1000);
        ESC_Servo_2.writeMicroseconds(1000);
        ESC_Servo_3.writeMicroseconds(1000);
        ESC_Servo_4.writeMicroseconds(1000);
    }
}


void get_rc_data() {
    for (channel = 0; channel < NUMCHANNELS; channel++) {
        value_channel = ppm.latestValidChannelValue(channel+1,0);
        channel_norm[channel] = (value_channel - 1000)*0.001; // TODO: this line eats up 400 ms of time....
    }

    roll_rc = LPF_roll_rc.Output(channel_norm[0],dt);
    pitch_rc = LPF_pitch_rc.Output(channel_norm[1],dt);
    thrust_rc = LPF_thrust_rc.Output(channel_norm[2],dt);
    yaw_rc = LPF_yaw_rc.Output(channel_norm[3],dt);

    remote_status = get_rc_status();

    if (remote_status == 2) {
        if (remote_armed == false) {
            if (thrust_rc < 0.05) {
                remote_armed = true;
            }
        }
    } else {
        remote_armed = false;
    }
}

float r2d(float degrees) {
    return (degrees * R2DCONST);
}

static float wrap(float angle) {
    while (angle > +180) angle -= 360;
    while (angle < -180) angle += 360;
    return angle;
}

int get_rc_status() {
    if (channel_norm[4] < -0.5) {
        // receiver connected, transmitter not connected
        return -1;
    } else if (channel_norm[4] > -0.1 && channel_norm[4] < 0.1) {
        // fall back mode
        return 0;
    } else if (channel_norm[4] > 0.4 && channel_norm[4] < 0.6) {
        // receiver connected, transmitter connected (NOT ARMED)
        return 1;
    } else if (channel_norm[4] > 0.9) {
        // receiver connected, transmitter connected (ARMED)
        return 2;
    }
}

int get_flight_mode() {
    if (channel_norm[5] < -0.5) {
        // receiver connected, transmitter not connected
        return -1;
    } else if (channel_norm[5] > -0.1 && channel_norm[5] < 0.1) {
        // switch all the way forward
        return 0;
    } else if (channel_norm[5] > 0.4 && channel_norm[5] < 0.6) {
        // switch in the middle
        return 1;
    } else if (channel_norm[5] > 0.9) {
        // switch all the way back
        return 2;
    }
}

bool flight_mode_change() {
    if (get_flight_mode() != last_flight_mode) {
        last_flight_mode = get_flight_mode();
        return 1;
    } else {
        last_flight_mode = get_flight_mode();
        return 0;
    }
}


void I2Cread(uint8_t Address, uint8_t Register, uint8_t Nbytes, uint8_t* Data) {
    // Set register address
    Wire.beginTransmission(Address);
    Wire.write(Register);
    Wire.endTransmission();
    // Read Nbytes
    Wire.requestFrom(Address, Nbytes); 
    uint8_t index=0;
    while (Wire.available())
    Data[index++]=Wire.read();
}

void I2CwriteByte(uint8_t Address, uint8_t Register, uint8_t Data) {
    // Set register address
    Wire.beginTransmission(Address);
    Wire.write(Register);
    Wire.write(Data);
    Serial.println(F("ending"));
    Wire.endTransmission();
}

void print_frequency() {
    Serial.print(F("f:"));
    Serial.print(freq);
    delimiter();
}

void delimiter() {
    Serial.print(comma[0]);
}


void print_omega_data() {
    Serial.print(F("OmgX:"));
    Serial.print(omega[0],5);
    Serial.print(F(",OmgY:"));
    Serial.print(omega[1],5);
    Serial.print(F(",OmgZ:"));
    Serial.print(omega[2],5);
    delimiter();
}

void print_omega_data_filter() {
    Serial.print(F("OmgX_f:"));
    Serial.print(omega[0]);
    Serial.print(F(",OmgY_f:"));
    Serial.print(omega[1]);
    Serial.print(F(",OmgZ_f:"));
    Serial.print(omega[2]);
    delimiter();
}

void print_acc_raw() {
    Serial.print(F("ax:"));
    Serial.print(ax);
    Serial.print(F(",ay:"));
    Serial.print(ay);
    Serial.print(F(",az:"));
    Serial.print(az);
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

void print_yaw_data() {

}

void print_acc_data_filter() {
    Serial.print(F("aX_f:"));
    Serial.print(acceleration[0]);
    Serial.print(F(",aY_f:"));
    Serial.print(acceleration[1]);
    Serial.print(F(",aZ_f:"));
    Serial.print(acceleration[2]);
    delimiter();
}

void print_rc_data() {
    for (int i = 0; i < (NUMCHANNELS); i++) {
        Serial.print(F("RC"));
        Serial.print(i+1);
        Serial.print(F(":"));
        Serial.print(channel_norm[i],4);
        delimiter();
    }
    Serial.print(F("RC_STATUS:"));
    Serial.print(get_rc_status());
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

void print_angle_rad() {
    Serial.print(F("AngX:"));
    Serial.print(angle[0]);
    Serial.print(F(",AngY:"));
    Serial.print(angle[1]);
    Serial.print(F(",AngZ:"));
    Serial.print(angle[2]);
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
    Serial.print(offset_acceleration[0],8);
    delimiter();
    Serial.print(offset_acceleration[1],8);
    delimiter();
    Serial.print(offset_acceleration[2],8);
    delimiter();
    Serial.println(F(""));
    Serial.println(F("Offsets omega:"));
    Serial.print(offset_omega[0],8);
    delimiter();
    Serial.print(offset_omega[1],8);
    delimiter();
    Serial.print(offset_omega[2],8);
    Serial.println(F(",\n"));
}

void print_pid_data() {
    Serial.print(F("pid1:"));
    Serial.print(out_1);
    Serial.print(F(",pid2:"));
    Serial.print(out_2);
    Serial.print(F(",pid3:"));
    Serial.print(out_3);
    Serial.print(F(",pid4:"));
    Serial.print(out_4);
    Serial.print(F(",pid5:"));
    Serial.print(out_5);
    delimiter();
}

void print_setpoints() {
    Serial.print(F("setpoint1:"));
    Serial.print(out_1);
    Serial.print(F(",setpoint2:"));
    Serial.print(out_2);
    Serial.print(F(",setpoint3:"));
    Serial.print(setpoint_3);
    Serial.print(F(",setpoint4:"));
    Serial.print(setpoint_4);
    delimiter();
}

void print_processed_rc_data() {
    Serial.print(F("roll:"));
    Serial.print(roll_rc,4);                    // Display the results    
    Serial.print(F(",pitch:"));
    Serial.print(pitch_rc,4);    
    Serial.print(F(",thrust:"));
    Serial.print(thrust_rc,4);
    Serial.print(F(",yaw:"));
    Serial.print(yaw_rc,4);
    delimiter();
}

void print_pressure_data() {
    Serial.print(F("pressure:"));
    Serial.print(pressure,4);                    // Display the results    
    Serial.print(F(",temperature:"));
    Serial.print(temperature,4);    
    Serial.print(F(",altitude:"));
    Serial.print(altitude,4);
    Serial.print(F(",altitude_prev:"));
    Serial.print(altitude_prev,4);
    delimiter();
}

void print_vertical_speed() {
    Serial.print(F("vertical_speed_BMP:"));
    Serial.print(vertical_speed_BMP);                    // Display the results    
    Serial.print(F(",vertical_speed_imu:"));
    Serial.print(vertical_speed_imu);    
    Serial.print(F(",vertical_speed:"));
    Serial.print(vertical_speed);
    delimiter();
}