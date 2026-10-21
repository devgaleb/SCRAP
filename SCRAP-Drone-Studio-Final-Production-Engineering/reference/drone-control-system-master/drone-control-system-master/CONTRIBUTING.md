# Contributing to Drone Control System

Thank you for your interest in contributing to the Drone Control System! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork** the repository on GitHub
2. **Clone** your fork locally: `git clone https://github.com/your-username/drone-control-arduino.git`
3. **Create** a feature branch: `git checkout -b feature/your-feature-name`
4. **Make** your changes and test them
5. **Commit** your changes: `git commit -m "Add your descriptive commit message"`
6. **Push** to your fork: `git push origin feature/your-feature-name`
7. **Create** a Pull Request on GitHub

## 🛠️ Development Setup

### Option 1: PlatformIO (Recommended)

1. Install [PlatformIO IDE](https://platformio.org/platformio-ide) or VS Code extension
2. Open the project folder
3. Build and upload: `pio run -t upload`

### Option 2: Arduino IDE

1. Install Arduino IDE 1.8.0 or later
2. Install required libraries (see `dependencies.md`)
3. Open `drone_v2.ino`
4. Select Arduino Mega 2560 board
5. Upload the code

## 🧪 Testing

### Hardware Testing
- **Always test on real hardware** when making control-related changes
- Start with `DEBUGGING_MODE 1` for serial output verification
- Test in a safe, open area with proper safety measures
- Have a way to immediately stop motors (kill switch)

### Unit Testing
- Test individual components (PID, filters) with known inputs
- Verify mathematical correctness of algorithms
- Check edge cases and error conditions

## 📝 Code Style Guidelines

### C++ Standards
- Use C++11 features compatible with Arduino
- Follow Arduino naming conventions
- Use meaningful variable and function names
- Add comments for complex logic

### Documentation
- Add Doxygen-style comments for classes and functions
- Document algorithm parameters and limitations
- Include usage examples where helpful

### File Organization
```
drone-control-arduino/
├── src/                    # Source files
│   ├── drone_v2.ino       # Main sketch
│   ├── PID_regulator.*    # PID controller
│   ├── KalmanFilter.*     # Kalman filter
│   ├── LPF.*             # Low-pass filter
│   └── TripleFilter.*    # Triple filter
├── examples/              # Example sketches
├── backups/               # Backup files
├── platformio.ini         # PlatformIO config
└── README.md             # Documentation
```

## 🔧 Types of Contributions

### 🐛 Bug Fixes
- Fix issues with existing functionality
- Improve stability and error handling
- Address hardware compatibility issues

### ✨ New Features
- Add new flight modes
- Implement additional sensors
- Enhance filtering algorithms
- Improve RC protocols

### 📚 Documentation
- Improve README and guides
- Add code comments and examples
- Create tutorials and troubleshooting guides

### 🧪 Testing
- Add unit tests for algorithms
- Create hardware test procedures
- Document test results and configurations

## 🔍 Code Review Process

1. **Automated Checks**: CI/CD pipeline runs basic checks
2. **Peer Review**: At least one maintainer reviews changes
3. **Testing**: Changes tested on hardware when applicable
4. **Merge**: Approved changes are merged to main branch

## 🚨 Important Notes

### Safety First
- **Never fly without proper safety measures**
- Test in controlled environments
- Have emergency stop procedures
- Respect local regulations for UAV operation

### Hardware Variations
- Document hardware-specific changes
- Consider compatibility with different Arduino boards
- Test with multiple sensor configurations

### Backwards Compatibility
- Avoid breaking changes without deprecation notices
- Document migration paths for major changes
- Maintain API stability where possible

## 📞 Getting Help

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for general questions
- **Documentation**: Check README and wiki first

## 📜 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to the Drone Control System! 🎯