# Odometry & Robotics Demo Suite

A comprehensive GUI application demonstrating various robotics and odometry concepts with interactive visualizations.

## Features

### 1. Pose Visualizer
- **2D Pose Visualization**: Interactive visualization of 2D poses with position (x, y) and orientation (θ)
- **Real-time Updates**: Sliders to control pose parameters with immediate visual feedback
- **Coordinate Frames**: Shows both world and local coordinate frames
- **Pose Information**: Displays formatted pose information

### 2. Rotation Demo
- **2D Vector Rotation**: Shows rotation of vectors with visual arrows
- **3D Vector Rotation**: 3D vector rotation around Z-axis
- **Matrix Display**: Real-time rotation matrix visualization
- **Formula Display**: Shows mathematical formulas for rotations
- **Animation**: Play/pause/reset controls for continuous rotation

### 3. 3D Position Demo
- **3D Position Visualization**: Interactive 3D position representation
- **Vector Properties**: Displays magnitude, unit vector, and angles
- **Coordinate Systems**: Shows Cartesian, spherical, and cylindrical coordinates
- **Real-time Updates**: Sliders for 3D position control

### 4. Wheel Odometry Demo
- **True Trajectory**: Rectangular trajectory simulation
- **Sensor Noise**: Realistic sensor noise simulation
- **Simple Odometry**: Basic wheel odometry implementation
- **EKF Localization**: Extended Kalman Filter with landmark corrections
- **Error Analysis**: Separate plots for position and angle errors
- **Landmark Measurements**: Ranging and bearing measurements
- **Interactive Controls**: Play/pause/step/reset functionality
- **Parameter Tuning**: Adjustable noise levels and simulation time

## Installation

1. **Prerequisites**:
   ```bash
   pip install numpy matplotlib scipy
   ```

2. **Run the Application**:
   ```bash
   python odometry_gui_demo.py
   ```

## Usage

### Main GUI
- **Tab Navigation**: Use tabs to switch between different demos
- **Interactive Controls**: Each demo has its own set of controls
- **Real-time Updates**: All visualizations update in real-time
- **Status Bar**: Shows current status and parameter values

### Pose Visualizer
- Use X, Y, and Orientation sliders to control the pose
- Watch the coordinate frame and orientation arrow update
- See pose information displayed in real-time

### Rotation Demo
- Use the theta slider to control rotation angle
- Click Play/Pause for continuous animation
- Click Reset to return to zero rotation
- Observe matrix and formula updates

### 3D Position Demo
- Use X, Y, Z sliders to control 3D position
- Watch the orthogonal basis vectors rotate
- See position components and vector properties
- Observe coordinate system transformations

### Wheel Odometry Demo
- Click Play to start simulation
- Click Pause to stop simulation
- Click Step to advance one time step
- Click Reset to restart simulation
- Toggle landmarks on/off
- Adjust total time and noise parameters

## Technical Details

### Architecture
- **Modular Design**: Each demo is a separate class for easy integration
- **GUI Framework**: Uses tkinter with matplotlib for visualizations
- **Threading**: Background animation threads for smooth performance
- **Event-driven**: Responsive to user interactions

### Key Algorithms
- **2D Rotation**: Standard rotation matrices
- **3D Rotation**: Z-axis rotation matrices
- **Wheel Odometry**: Differential drive model
- **EKF**: Extended Kalman Filter for state estimation
- **Landmark SLAM**: Range and bearing measurements

### Performance
- **Real-time Updates**: Optimized for smooth real-time visualization
- **Memory Efficient**: Proper cleanup of plot elements
- **Thread Safe**: Safe threading for animations

## File Structure

```
odometry_demo/
├── odometry_gui_demo.py      # Main GUI application
├── pose_visualizer.py        # 2D pose visualization
├── rotation_demo.py          # 2D/3D rotation demo
├── position_3d_demo.py       # 3D position demo
├── wheel_odometry_demo.py    # Wheel odometry demo
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Educational Value

This demo suite is designed for:
- **Students**: Learning robotics and odometry concepts
- **Researchers**: Prototyping and testing algorithms
- **Engineers**: Understanding sensor fusion and state estimation
- **Educators**: Teaching robotics concepts with visual examples

## Contributing

Feel free to contribute by:
- Adding new demos
- Improving existing visualizations
- Fixing bugs
- Adding documentation

## License

This project is part of the AmbiqSuite and follows the same licensing terms.

## Support

For issues or questions, please refer to the AmbiqSuite documentation or contact the development team. 