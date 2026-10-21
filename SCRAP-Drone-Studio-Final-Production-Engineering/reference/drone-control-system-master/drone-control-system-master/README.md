# Drone Control System (Arduino)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Arduino](https://img.shields.io/badge/Platform-Arduino-00979D.svg)](https://www.arduino.cc/)

# ⚠️ **CRITICAL SAFETY WARNING**

**This is a PROTOTYPE/RESEARCH SYSTEM - NOT PRODUCTION READY!**

## 🚨 **IMMEDIATE SAFETY CONCERNS**

1. **ESC Calibration Risk**: The system performs automatic ESC calibration on startup by sending maximum throttle signals. **NEVER run this code with propellers attached!** ESCs that don't properly detect the calibration sequence may interpret this as full throttle commands, causing the drone to take off uncontrollably.

2. **No Safety Features**: This system lacks essential safety features found in commercial flight controllers (arming switches, failsafes, motor kill switches, etc.).

3. **Research Prototype**: This code was developed for academic research and testing. It requires modification and thorough testing before use on any drone.

## 🛑 **REQUIRED SAFETY PRECAUTIONS**

- **REMOVE ALL PROPELLERS** before uploading or testing this code
- **Test in a controlled environment** with emergency cutoff capabilities
- **Modify the code** to disable `DEBUGGING_MODE 0` for initial testing
- **Add your own safety features** before flight
- **Test incrementally** - never fly with untested code

**You assume all risks when using this code. The author is not responsible for any damage, injury, or loss.**

---

A complete quadcopter/drone flight control system implemented on Arduino, featuring advanced sensor fusion, PID control algorithms, and multiple flight modes. This project was developed as part of a master's thesis on UAV control systems.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Software Dependencies](#software-dependencies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Flight Modes](#flight-modes)
- [PID Tuning](#pid-tuning)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Citation](#citation)

## 🎯 Overview

This flight control system implements a cascaded PID control architecture for quadcopter stabilization and navigation. The system integrates multiple sensors including IMU (MPU-9255) and barometric pressure sensor (BMP280) to provide robust attitude estimation and altitude control.

The project includes custom implementations of:
- **PID Regulator**: Cascaded PID control for attitude and rate stabilization
- **Kalman Filter**: Sensor fusion for altitude estimation
- **Low-Pass Filter**: RC input smoothing and sensor noise reduction
- **Triple Filter**: Advanced sensor filtering combining Kalman and LPF

## ✨ Features

### Flight Control
- **Cascaded PID Control**: Separate rate and attitude control loops
- **Multiple Flight Modes**: Acro, Normal, and Altitude Hold modes
- **Arming/Disarming**: Safe RC-based arming procedure
- **Failsafe Protection**: Automatic disarm on signal loss

### Sensor Integration
- **MPU-9255 IMU**: 9-DOF sensor with accelerometer, gyroscope, and magnetometer
- **BMP280 Barometer**: High-precision altitude estimation
- **PPM Receiver**: Standard RC protocol support (up to 6 channels)

### Advanced Filtering
- **Kalman Filter**: Altitude estimation with process and measurement noise tuning
- **Low-Pass Filters**: Configurable cutoff frequencies for different signals
- **Triple Filter**: Combined Kalman-LPF-Kalman filtering for IMU data

### Hardware Control
- **ESC Calibration**: Automated Electronic Speed Controller setup
- **PWM Output**: Precise motor control with 1000-2000μs range
- **Quadcopter Layout**: Standard X configuration

## 🔧 Hardware Requirements

### Core Components
- **Arduino Board**: Compatible with Arduino Mega/Uno (tested on Mega)
- **IMU Sensor**: MPU-9255 (I2C interface)
- **Barometric Sensor**: BMP280 (I2C interface)
- **RC Receiver**: PPM output (6+ channels recommended)
- **ESCs**: 4x Electronic Speed Controllers (SimonK/BLHeli firmware)
- **Motors**: 4x Brushless DC motors (quadcopter configuration)
- **Battery**: 3S-4S LiPo battery with appropriate voltage regulator
- **Frame**: Quadcopter frame (appropriate size for motors)

### Pin Connections
```
Arduino Pin | Component       | Purpose
------------|-----------------|---------
2           | PPM Receiver    | RC input signal
3,5,9,11    | ESCs            | Motor PWM output (ESC1-ESC4)
SDA (20)    | MPU9255/BMP280  | I2C data line
SCL (21)    | MPU9255/BMP280  | I2C clock line
GND         | All sensors      | Common ground
5V          | Sensors/Receiver | Power supply
```

### RC Transmitter Setup (6+ channels)
1. **Channel 1**: Roll (Aileron)
2. **Channel 2**: Pitch (Elevator)
3. **Channel 3**: Thrust (Throttle)
4. **Channel 4**: Yaw (Rudder)
5. **Channel 5**: Arming switch
6. **Channel 6**: Flight mode switch

## 📦 Software Dependencies

### Arduino Libraries
- **PPMReader**: RC receiver signal decoding
- **Servo**: Motor control PWM generation
- **BMP280_DEV**: Barometric pressure sensor interface
- **Wire**: I2C communication protocol

### Custom Classes
- **PID_regulator**: PID control implementation
- **KalmanFilter**: Kalman filtering for sensor fusion
- **LPF**: Low-pass filter implementation
- **TripleFilter**: Combined filtering approach

For detailed installation instructions, see [`dependencies.md`](dependencies.md).

## 🚀 Installation

### 1. Arduino IDE Setup
1. Install Arduino IDE (version 1.8.0 or later)
2. Install required libraries via Library Manager:
   - PPMReader
   - Servo
   - BMP280_DEV

### 2. Hardware Assembly
1. Mount Arduino board on quadcopter frame
2. Connect IMU and barometric sensors to I2C bus
3. Connect PPM receiver to digital pin 2
4. Connect ESCs to PWM pins (3, 5, 9, 11)
5. Power distribution setup (separate power for Arduino and ESCs)

### 3. Upload Code

#### Option A: Arduino IDE
1. Open `drone_v2.ino` in Arduino IDE
2. Select appropriate board and port
3. Configure DEBUGGING_MODE if needed
4. Upload the code

#### Option B: PlatformIO (Recommended)
1. Install [PlatformIO](https://platformio.org/)
2. Open project folder in VS Code with PlatformIO extension
3. Run `pio run -t upload` or use the upload button
4. For debugging: `pio run -t upload --environment debug`

### 4. ESC Calibration

> 🚨 **DANGER**: ESC calibration sends maximum throttle signals that can cause motors to spin at full speed!

**CRITICAL SAFETY REQUIREMENT**: **REMOVE ALL PROPELLERS** before performing ESC calibration. ESCs that don't properly detect calibration signals may spin motors at 100% throttle.

The system performs **automatic ESC calibration on EVERY boot** when `DEBUGGING_MODE` is disabled:
1. **ENSURE NO PROPELLERS ARE ATTACHED**
2. Power on the system
3. Wait for "Starting ESC calibration sequence" message
4. **System automatically sends maximum (2000μs) then minimum (1000μs) throttle signals**
5. Wait for calibration to complete (10 seconds total)
6. **RE-ATTACH PROPELLERS ONLY AFTER** confirming calibration worked correctly

**Note**: To skip calibration for testing, set `DEBUGGING_MODE 1` in the code.

## ⚙️ Configuration

### PID Tuning Parameters

Edit the defines in `drone_v2.ino`:

```cpp
// Pitch control
#define Kp_w_pitch   0.0003   // Rate PID proportional gain
#define Ki_w_pitch   0.0006   // Rate PID integral gain
#define Kd_w_pitch   0.000025  // Rate PID derivative gain
#define Kp_theta_pitch   5.0   // Attitude PID proportional gain
#define Ki_theta_pitch   8.0   // Attitude PID integral gain
#define Kd_theta_pitch   0.05  // Attitude PID derivative gain

// Roll control (similar structure)
// Yaw control (rate-only PID)
// Altitude control (single PID loop)
```

### Filter Parameters

```cpp
// IMU filtering
#define Q_w   0.5   // Gyro process noise
#define R_w   2.5e-7   // Gyro measurement noise
#define Q_a   0.5   // Accel process noise
#define R_a   2.5e-7   // Accel measurement noise

// RC input filtering
#define f_c_rc 4    // RC cutoff frequency (Hz)

// Altitude filtering
#define f_c_alt 1  // Altitude cutoff frequency (Hz)
#define Q_alt   0.008   // Altitude process noise
#define R_alt   1e4     // Altitude measurement noise
```

### Flight Limits

```cpp
#define MAX_DEGREES 30          // Maximum tilt angle (Normal mode)
#define MAX_DPS_YAW 180         // Maximum yaw rate
#define MAX_DPS_PITCH_ROLL 180  // Maximum pitch/roll rate (Acro mode)
#define MAX_VERT_SPEED 0.25     // Maximum vertical speed (Altitude hold)
```

## ✈️ Flight Modes

### 1. Acro Mode (Flight Mode Switch: Forward)
- **Direct Rate Control**: RC inputs directly control rotation rates
- **No Attitude Stabilization**: Requires pilot skill
- **Best for**: Aerobatic maneuvers, experienced pilots

### 2. Normal Mode (Flight Mode Switch: Middle)
- **Attitude Stabilization**: RC inputs control angle (self-leveling)
- **Cascaded PID**: Rate and attitude control loops
- **Best for**: General flying, beginners

### 3. Altitude Hold Mode (Flight Mode Switch: Back)
- **Altitude Stabilization**: Maintains constant altitude
- **Vertical Speed Control**: Thrust input controls climb/sink rate
- **Best for**: Photography, cruise flight

## 🎛️ PID Tuning

### Tuning Process
1. **Start with Rate PIDs** (inner loop): Set I and D to zero, increase P until oscillations occur, then reduce by half
2. **Tune Rate I and D**: Add integral for steady-state accuracy, derivative for stability
3. **Tune Attitude PIDs** (outer loop): Start with low values, increase until responsive
4. **Fine-tune**: Adjust all gains for smooth response

### Tuning Tips
- **Overshoot**: Reduce P gains
- **Oscillations**: Reduce P or increase D gains
- **Drift**: Increase I gains (carefully)
- **Sluggish response**: Increase P gains

## 🏗️ Architecture

### Control Loop Structure
```
RC Input → Low-Pass Filter → PID Controllers → Motor Mixing → PWM Output
                    ↓
Sensor Data → Filtering → Attitude Estimation → PID Controllers
```

### Data Flow
1. **Sensor Reading**: IMU and barometric data acquisition
2. **Filtering**: Triple filtering for IMU, Kalman for altitude
3. **Attitude Estimation**: Complementary filter combining accel/gyro
4. **PID Control**: Cascaded control for each axis
5. **Motor Mixing**: Convert control outputs to individual motor commands
6. **PWM Generation**: Send commands to ESCs

## 📚 API Reference

### PID_regulator Class
```cpp
PID_regulator pid;
pid.set_parameters(Kp, Ki, Kd, bias);
float output = pid.Output(input, setpoint, dt, stop_integration);
```

### KalmanFilter Class
```cpp
KalmanFilter kf;
kf.change_parameters(Q, R, initial_value);
float filtered = kf.Output(measurement);
```

### LPF Class
```cpp
LPF filter;
filter.change_parameters(cutoff_freq, initial_value);
float filtered = filter.Output(input, dt);
```

## 🔧 Troubleshooting

### Common Issues

**Drone won't arm:**
- Check RC transmitter battery and signal
- Verify PPM receiver connection (pin 2)
- Ensure throttle is at minimum position

**Unstable flight:**
- Check IMU calibration (run calibrate() function)
- Verify PID gains are not too aggressive
- Check motor balance and propeller tracking

**Altitude drifting:**
- Recalibrate barometric sensor
- Adjust altitude PID gains
- Check for air leaks in enclosure

**No sensor data:**
- Verify I2C connections and pull-up resistors
- Check sensor power supply voltage
- Use I2C scanner sketch to verify addresses

### Debug Mode
Set `DEBUGGING_MODE 1` to enable serial debugging:
- Real-time sensor data output
- PID controller status
- RC input monitoring
- System frequency information

## 🤝 Contributing

We welcome contributions! This project is open source and we encourage community involvement. Here's how you can contribute:

### Ways to Contribute
1. **Report Bugs**: Open issues for any bugs you find
2. **Feature Requests**: Suggest new features or improvements
3. **Code Contributions**: Submit pull requests with bug fixes or enhancements
4. **Documentation**: Improve documentation, add tutorials, or fix typos
5. **Testing**: Test on different hardware configurations and share results
6. **PID Tuning**: Share your tuning experiences and parameter sets

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

### Guidelines
- Follow Arduino coding conventions
- Add comments for complex logic
- Test on real hardware when possible
- Update documentation for any new features
- Keep commits focused and descriptive

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📖 Citation

If you use this code in your research or project, please cite the original master's thesis:

```bibtex
@mastersthesis{smrekar2022modeling,
  title={Modelling and production of the control system and propellers of an unmanned aerial vehicle},
  author={Smrekar, Miha},
  year={2022},
  school={Faculty of Energy, University of Maribor},
  address={Kr\v{s}ko, Slovenia},
  url={https://dk.um.si/IzpisGradiva.php?id=81118}
}
```

### Related Research
- Mathematical modeling of UAV dynamics
- BEM analysis of propeller performance
- PID controller design for multi-rotor systems
- Sensor fusion techniques for attitude estimation

---

# 🚨 **FINAL SAFETY WARNING**

**This is a PROTOTYPE RESEARCH SYSTEM - NOT A COMMERCIAL FLIGHT CONTROLLER!**

- **No Commercial Guarantees**: This code lacks the safety features and testing of production flight controllers
- **Research Use Only**: Developed for academic purposes and requires significant modification for safe operation
- **Your Responsibility**: You are solely responsible for ensuring safe operation when using this code
- **No Liability**: The author assumes no responsibility for any damage, injury, or loss resulting from use of this software

**Always fly in designated areas, maintain visual contact, and be prepared for immediate emergency cutoff. Never fly over people or property.**