# Dependencies

This project requires several Arduino libraries to function properly. Below is a complete list of dependencies and installation instructions.

## Required Arduino Libraries

### 1. PPMReader
- **Purpose**: RC receiver signal decoding
- **Author**: Michel Pastor
- **Installation**:
  - Arduino IDE: Tools → Manage Libraries → Search for "PPMReader"
  - Or download from: https://github.com/Nikkilae/PPMReader

### 2. Servo
- **Purpose**: Motor control PWM generation
- **Author**: Arduino
- **Installation**: Built-in with Arduino IDE (no installation required)

### 3. BMP280_DEV
- **Purpose**: Barometric pressure sensor interface
- **Author**: Martin Lindupp
- **Installation**:
  - Arduino IDE: Tools → Manage Libraries → Search for "BMP280_DEV"
  - Or download from: https://github.com/MartinL1/BMP280_DEV

### 4. Wire
- **Purpose**: I2C communication protocol
- **Author**: Arduino
- **Installation**: Built-in with Arduino IDE (no installation required)

## Hardware-Specific Libraries

### For MPU-9255 IMU
The MPU-9255 is accessed directly via I2C using the Wire library. No additional libraries are required.

## PlatformIO Dependencies

If using PlatformIO, all dependencies are automatically managed. See `platformio.ini` for the exact versions used.

## Manual Installation

If your Arduino IDE doesn't have access to the Library Manager:

1. Download the required libraries as ZIP files
2. Arduino IDE: Sketch → Include Library → Add .ZIP Library
3. Select the downloaded ZIP files

## Version Compatibility

- **Arduino IDE**: 1.8.0 or later
- **PPMReader**: 1.0.0 or later
- **BMP280_DEV**: Latest version
- **Board Support**: Arduino Mega 2560 (recommended), Arduino Uno (limited features)

## Troubleshooting

### Library Installation Issues
- Ensure Arduino IDE is closed during installation
- Restart Arduino IDE after installing libraries
- Check for library conflicts in Arduino IDE error messages

### Compilation Errors
- Verify all libraries are installed correctly
- Check that you're using a compatible Arduino board
- Ensure correct board is selected in Tools → Board menu

### Hardware Compatibility
- For Arduino Uno: Set `DEBUGGING_MODE 1` due to limited RAM
- For Arduino Mega: Full feature set available
- Ensure sufficient flash memory and RAM for all features