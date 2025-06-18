#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons, TextBox
import math
from scipy.spatial.distance import cdist
import threading
import time

class WheelOdometryDemo:
    def __init__(self, fig=None):
        """Initialize the wheel odometry demonstration"""
        if fig is None:
            self.fig = plt.figure(figsize=(16, 12))
        else:
            self.fig = fig
            
        # Configurable parameters
        self.total_time = 50.0  # Total simulation time (configurable)
        self.landmark_count = 5  # Number of landmarks (configurable)
        
        # Setup plots
        self.setup_plots()
        
        # Setup simulation
        self.setup_simulation()
        
        # Setup controls
        self.setup_controls()
        
        # Initialize EKF
        self.initialize_ekf()
        
        # Animation control
        self.is_animating = False
        self.animation_thread = None
        self.plot_update_callback = None  # Callback for GUI plot updates
        
    def setup_plots(self):
        """Setup the subplots for wheel odometry demonstration"""
        # Main trajectory plot
        self.ax1 = self.fig.add_subplot(2, 3, 1)
        self.ax1.set_xlim(-2, 12)
        self.ax1.set_ylim(-2, 10)
        self.ax1.set_aspect('equal')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_title('Wheel Odometry Trajectory', fontsize=14, fontweight='bold')
        self.ax1.set_xlabel('X (m)')
        self.ax1.set_ylabel('Y (m)')
        
        # Position error plot
        self.ax2 = self.fig.add_subplot(2, 3, 2)
        self.ax2.set_title('Position Error', fontsize=12, fontweight='bold')
        self.ax2.set_xlabel('Time (s)')
        self.ax2.set_ylabel('Error (m)')
        self.ax2.grid(True, alpha=0.3)
        
        # Angle error plot
        self.ax3 = self.fig.add_subplot(2, 3, 3)
        self.ax3.set_title('Angle Error', fontsize=12, fontweight='bold')
        self.ax3.set_xlabel('Time (s)')
        self.ax3.set_ylabel('Error (deg)')
        self.ax3.grid(True, alpha=0.3)
        
        # Linear velocity plot
        self.ax4 = self.fig.add_subplot(2, 3, 4)
        self.ax4.set_title('Linear Velocity', fontsize=12, fontweight='bold')
        self.ax4.set_xlabel('Time (s)')
        self.ax4.set_ylabel('Velocity (m/s)')
        self.ax4.grid(True, alpha=0.3)
        
        # Angular velocity plot
        self.ax5 = self.fig.add_subplot(2, 3, 5)
        self.ax5.set_title('Angular Velocity', fontsize=12, fontweight='bold')
        self.ax5.set_xlabel('Time (s)')
        self.ax5.set_ylabel('Angular Velocity (rad/s)')
        self.ax5.grid(True, alpha=0.3)
        
        # Configuration panel
        self.ax6 = self.fig.add_subplot(2, 3, 6)
        self.ax6.axis('off')
        self.ax6.set_title('Configuration', fontsize=12, fontweight='bold')
        
        # plt.tight_layout()  # Removed to avoid compatibility warning
        
    def setup_simulation(self):
        """Initialize simulation parameters and state"""
        # Simulation parameters
        self.dt = 0.1  # Time step
        self.times = np.arange(0, self.total_time, self.dt)
        
        # Robot parameters
        self.robot_width = 0.3  # Robot width (m)
        self.wheel_radius = 0.05  # Wheel radius (m)
        
        # Noise parameters
        self.linear_noise_std = 0.1  # Linear velocity noise std (m/s)
        self.angular_noise_std = 0.05  # Angular velocity noise std (rad/s)
        self.landmark_noise_std = 0.1  # Landmark ranging noise std (m)
        self.landmark_angle_noise_std = 0.02  # Landmark angle noise std (rad)
        
        # Generate landmarks based on configurable count
        self.landmarks = self.generate_landmarks()
        
        # Simulation state
        self.is_playing = False
        self.current_step = 0
        self.use_landmarks = True
        self.landmark_update_freq = 10  # Update landmarks every N steps (increased for stability)
        
        # Initialize trajectories
        self.initialize_trajectories()
        
        # Setup plot elements
        self.setup_trajectory_plot()
        self.setup_error_plot()
        self.setup_sensor_plots()
        self.update_configuration_display()
        
    def generate_landmarks(self):
        """Generate landmarks based on configurable count"""
        landmarks = []
        
        if self.landmark_count >= 1:
            landmarks.append([2, 2])  # Bottom-left
        if self.landmark_count >= 2:
            landmarks.append([8, 2])  # Bottom-right
        if self.landmark_count >= 3:
            landmarks.append([8, 6])  # Top-right
        if self.landmark_count >= 4:
            landmarks.append([2, 6])  # Top-left
        if self.landmark_count >= 5:
            landmarks.append([5, 4])  # Center
        if self.landmark_count >= 6:
            landmarks.append([1, 1])  # Far bottom-left
        if self.landmark_count >= 7:
            landmarks.append([9, 1])  # Far bottom-right
        if self.landmark_count >= 8:
            landmarks.append([9, 7])  # Far top-right
        if self.landmark_count >= 9:
            landmarks.append([1, 7])  # Far top-left
        if self.landmark_count >= 10:
            landmarks.append([3, 3])  # Inner bottom-left
        if self.landmark_count >= 11:
            landmarks.append([7, 3])  # Inner bottom-right
        if self.landmark_count >= 12:
            landmarks.append([7, 5])  # Inner top-right
        if self.landmark_count >= 13:
            landmarks.append([3, 5])  # Inner top-left
        
        return np.array(landmarks)
    
    def initialize_trajectories(self):
        """Initialize true and estimated trajectories"""
        # True trajectory (rectangle)
        self.true_trajectory = self.generate_rectangle_trajectory()
        
        # Estimated trajectory - start from initial position and evolve with noise
        # Initialize with zeros, will be updated step by step based on noisy measurements
        self.estimated_trajectory = np.zeros_like(self.true_trajectory)
        # Set initial position (same as true trajectory starting point)
        self.estimated_trajectory[0] = self.true_trajectory[0]
        
        # EKF trajectory
        self.ekf_trajectory = []
        
        # Reset EKF state
        self.initialize_ekf()
        
        # Sensor data
        self.linear_velocities = []
        self.angular_velocities = []
        self.true_linear_velocities = []
        self.true_angular_velocities = []
        
        # Error tracking
        self.position_errors = []
        self.orientation_errors = []
        self.ekf_position_errors = []
        self.ekf_orientation_errors = []
        
    def generate_rectangle_trajectory(self):
        """Generate a rectangular trajectory"""
        trajectory = []
        x, y, theta = 0, 0, 0  # Start at origin
        
        # Rectangle parameters
        width, height = 10, 8
        velocity = 0.5  # m/s
        
        # Calculate time for each segment
        segment_times = [width/velocity, height/velocity, width/velocity, height/velocity]
        total_segment_time = sum(segment_times)
        
        # Generate trajectory points
        for t in self.times:
            # Determine which segment we're in
            segment_time = t % total_segment_time
            cumulative_time = 0
            
            for i, seg_time in enumerate(segment_times):
                if segment_time < cumulative_time + seg_time:
                    # Calculate position in this segment
                    local_time = segment_time - cumulative_time
                    progress = local_time / seg_time
                    
                    if i == 0:  # Bottom edge (left to right)
                        x = progress * width
                        y = 0
                        theta = 0
                    elif i == 1:  # Right edge (bottom to top)
                        x = width
                        y = progress * height
                        theta = np.pi/2
                    elif i == 2:  # Top edge (right to left)
                        x = width - progress * width
                        y = height
                        theta = np.pi
                    else:  # Left edge (top to bottom)
                        x = 0
                        y = height - progress * height
                        theta = -np.pi/2
                    
                    break
                cumulative_time += seg_time
            
            trajectory.append([x, y, theta])
        
        return np.array(trajectory)
    
    def add_sensor_noise(self, true_linear_vel, true_angular_vel):
        """Add noise to sensor measurements"""
        noisy_linear_vel = true_linear_vel + np.random.normal(0, self.linear_noise_std)
        noisy_angular_vel = true_angular_vel + np.random.normal(0, self.angular_noise_std)
        
        return noisy_linear_vel, noisy_angular_vel
    
    def calculate_landmark_measurements(self, robot_pos):
        """Calculate landmark ranging and bearing measurements"""
        measurements = []
        
        for landmark in self.landmarks:
            # Calculate true range and bearing
            dx = landmark[0] - robot_pos[0]
            dy = landmark[1] - robot_pos[1]
            true_range = np.sqrt(dx**2 + dy**2)
            true_bearing = np.arctan2(dy, dx) - robot_pos[2]
            
            # Add noise
            noisy_range = true_range + np.random.normal(0, self.landmark_noise_std)
            noisy_bearing = true_bearing + np.random.normal(0, self.landmark_angle_noise_std)
            
            measurements.append([noisy_range, noisy_bearing])
        
        return measurements
    
    def update_odometry(self, linear_vel, angular_vel, dt):
        """Update odometry using wheel encoder measurements"""
        # Simple differential drive model
        x, y, theta = self.estimated_trajectory[self.current_step - 1]  # Use previous step
        
        # Update position
        new_x = x + linear_vel * dt * np.cos(theta)
        new_y = y + linear_vel * dt * np.sin(theta)
        new_theta = theta + angular_vel * dt
        
        return new_x, new_y, new_theta
    
    def setup_trajectory_plot(self):
        """Setup the main trajectory plot"""
        # True trajectory
        self.true_traj_line, = self.ax1.plot([], [], 'b-', linewidth=2, label='True Trajectory')
        
        # Estimated trajectory (simple odometry)
        self.estimated_traj_line, = self.ax1.plot([], [], 'r-', linewidth=2, label='Simple Odometry')
        
        # EKF trajectory
        self.ekf_traj_line, = self.ax1.plot([], [], 'g-', linewidth=2, label='EKF Estimate')
        
        # Robot position
        self.robot_pos_plot = self.ax1.plot([], [], 'ko', markersize=8, label='Robot Position')[0]
        
        # Landmarks (will be updated dynamically)
        self.landmark_plots = []
        self.measurement_lines = []
        
        # Update landmark plots
        self.update_landmark_plots()
        
        self.ax1.legend()
        
    def update_landmark_plots(self):
        """Update landmark plots based on current landmark count"""
        # Clear existing landmark plots
        if hasattr(self, 'landmark_plots'):
            for plot in self.landmark_plots:
                plot.remove()
        if hasattr(self, 'measurement_lines'):
            for line in self.measurement_lines:
                line.remove()
        
        self.landmark_plots = []
        self.measurement_lines = []
        
        # Create new landmark plots
        for i, landmark in enumerate(self.landmarks):
            plot = self.ax1.plot(landmark[0], landmark[1], 'g^', markersize=10, 
                               label=f'Landmark {i+1}' if i == 0 else "")[0]
            self.landmark_plots.append(plot)
        
        # Create measurement lines
        for _ in range(len(self.landmarks)):
            line, = self.ax1.plot([], [], 'g--', alpha=0.5, linewidth=1)
            self.measurement_lines.append(line)
        
    def setup_error_plot(self):
        """Setup the error analysis plots with separate subplots for position and angle errors"""
        # Position error lines
        self.pos_error_line, = self.ax2.plot([], [], 'b-', linewidth=2, label='Simple Odometry')
        self.ekf_pos_error_line, = self.ax2.plot([], [], 'g-', linewidth=2, label='EKF')
        self.ax2.legend()
        
        # Angle error lines (in degrees)
        self.angle_error_line, = self.ax3.plot([], [], 'r--', linewidth=2, label='Simple Odometry')
        self.ekf_angle_error_line, = self.ax3.plot([], [], 'm--', linewidth=2, label='EKF')
        self.ax3.legend()
        
    def setup_sensor_plots(self):
        """Setup the sensor data plots"""
        # Linear velocity
        self.true_linear_line, = self.ax4.plot([], [], 'b-', linewidth=2, label='True')
        self.measured_linear_line, = self.ax4.plot([], [], 'r-', linewidth=2, label='Measured')
        self.ax4.legend()
        
        # Angular velocity
        self.true_angular_line, = self.ax5.plot([], [], 'b-', linewidth=2, label='True')
        self.measured_angular_line, = self.ax5.plot([], [], 'r-', linewidth=2, label='Measured')
        self.ax5.legend()
        
    def update_plots(self):
        """Update all plots with current simulation state"""
        # Update trajectory plot
        self.true_traj_line.set_data(self.true_trajectory[:self.current_step+1, 0], 
                                    self.true_trajectory[:self.current_step+1, 1])
        self.estimated_traj_line.set_data(self.estimated_trajectory[:self.current_step+1, 0], 
                                        self.estimated_trajectory[:self.current_step+1, 1])
        
        # Update EKF trajectory
        if len(self.ekf_trajectory) > 0:
            ekf_traj = np.array(self.ekf_trajectory)
            self.ekf_traj_line.set_data(ekf_traj[:, 0], ekf_traj[:, 1])
        
        # Update robot position
        if self.current_step < len(self.true_trajectory):
            true_pos = self.true_trajectory[self.current_step]
            
            # Use EKF state for robot position if available, otherwise use true position
            if len(self.ekf_trajectory) > 0:
                est_pos = self.ekf_trajectory[-1]
            else:
                est_pos = self.estimated_trajectory[self.current_step]
            
            self.robot_pos_plot.set_data([true_pos[0]], [true_pos[1]])
            
            # Update landmark measurements using EKF state
            if self.use_landmarks and len(self.ekf_trajectory) > 0:
                measurements = self.calculate_landmark_measurements(est_pos)
                for i, (range_meas, bearing_meas) in enumerate(measurements):
                    landmark = self.landmarks[i]
                    # Draw line from robot to landmark (showing the range measurement)
                    # The bearing is relative to robot's orientation
                    robot_to_landmark_angle = est_pos[2] + bearing_meas
                    end_x = est_pos[0] + range_meas * np.cos(robot_to_landmark_angle)
                    end_y = est_pos[1] + range_meas * np.sin(robot_to_landmark_angle)
                    self.measurement_lines[i].set_data([est_pos[0], end_x], [est_pos[1], end_y])
            else:
                for line in self.measurement_lines:
                    line.set_data([], [])
        
        # Update error plot
        if len(self.position_errors) > 0:
            self.pos_error_line.set_data(self.times[:len(self.position_errors)], self.position_errors)
            
        if len(self.ekf_position_errors) > 0:
            self.ekf_pos_error_line.set_data(self.times[:len(self.ekf_position_errors)], self.ekf_position_errors)
            
        if len(self.orientation_errors) > 0:
            self.angle_error_line.set_data(self.times[:len(self.orientation_errors)], self.orientation_errors)
            
        if len(self.ekf_orientation_errors) > 0:
            self.ekf_angle_error_line.set_data(self.times[:len(self.ekf_orientation_errors)], self.ekf_orientation_errors)
        
        # Update error plot axis limits
        if len(self.position_errors) > 0 or len(self.ekf_position_errors) > 0:
            max_pos_error = max(max(self.position_errors) if self.position_errors else 0,
                              max(self.ekf_position_errors) if self.ekf_position_errors else 0)
            self.ax2.set_xlim(0, self.times[min(len(self.position_errors), len(self.times)-1)])
            self.ax2.set_ylim(0, max_pos_error * 1.1)
            
        if len(self.orientation_errors) > 0 or len(self.ekf_orientation_errors) > 0:
            max_angle_error = max(max(self.orientation_errors) if self.orientation_errors else 0,
                                max(self.ekf_orientation_errors) if self.ekf_orientation_errors else 0)
            self.ax3.set_xlim(0, self.times[min(len(self.orientation_errors), len(self.times)-1)])
            self.ax3.set_ylim(0, max_angle_error * 1.1)
        
        # Update sensor plots
        if len(self.linear_velocities) > 0:
            self.true_linear_line.set_data(self.times[:len(self.true_linear_velocities)], self.true_linear_velocities)
            self.measured_linear_line.set_data(self.times[:len(self.linear_velocities)], self.linear_velocities)
        
        if len(self.angular_velocities) > 0:
            self.true_angular_line.set_data(self.times[:len(self.true_angular_velocities)], self.true_angular_velocities)
            self.measured_angular_line.set_data(self.times[:len(self.angular_velocities)], self.angular_velocities)
        
        # Update axis limits for sensor plots
        if len(self.linear_velocities) > 0:
            self.ax4.set_xlim(0, self.times[min(len(self.linear_velocities), len(self.times)-1)])
            self.ax4.set_ylim(min(self.linear_velocities + self.true_linear_velocities) - 0.1,
                             max(self.linear_velocities + self.true_linear_velocities) + 0.1)
        
        if len(self.angular_velocities) > 0:
            self.ax5.set_xlim(0, self.times[min(len(self.angular_velocities), len(self.times)-1)])
            self.ax5.set_ylim(min(self.angular_velocities + self.true_angular_velocities) - 0.1,
                             max(self.angular_velocities + self.true_angular_velocities) + 0.1)
        
    def update_configuration_display(self):
        """Update the configuration display text"""
        # Clear previous text
        self.ax6.clear()
        self.ax6.set_xlim(0, 1)
        self.ax6.set_ylim(0, 1)
        self.ax6.axis('off')
        
        config_text = "Configuration:\n"
        config_text += f"  Total Time: {self.total_time:.1f}s\n"
        config_text += f"  Landmark Count: {self.landmark_count}\n"
        config_text += f"  Step: {self.current_step}/{len(self.times)-1}\n"
        config_text += f"  Time: {self.times[self.current_step]:.1f}s\n\n"
        
        config_text += f"Noise Parameters:\n"
        config_text += f"  Linear Velocity: {self.linear_noise_std:.3f} m/s\n"
        config_text += f"  Angular Velocity: {self.angular_noise_std:.3f} rad/s\n"
        config_text += f"  Landmark Range: {self.landmark_noise_std:.3f} m\n"
        config_text += f"  Landmark Angle: {self.landmark_angle_noise_std:.3f} rad\n\n"
        
        config_text += f"Landmarks:\n"
        config_text += f"  Count: {len(self.landmarks)}\n"
        config_text += f"  Enabled: {'Yes' if self.use_landmarks else 'No'}\n"
        config_text += f"  Update Freq: {self.landmark_update_freq} steps\n\n"
        
        if len(self.position_errors) > 0:
            config_text += f"Current Error:\n"
            config_text += f"  Simple Odometry: {self.position_errors[-1]:.3f} m\n"
            if len(self.orientation_errors) > 0:
                config_text += f"  Orientation: {self.orientation_errors[-1]:.1f}°\n"
            
            if len(self.ekf_position_errors) > 0:
                config_text += f"  EKF: {self.ekf_position_errors[-1]:.3f} m\n"
                if len(self.ekf_orientation_errors) > 0:
                    config_text += f"  EKF Orientation: {self.ekf_orientation_errors[-1]:.1f}°"
        
        self.ax6.text(0.05, 0.95, config_text, transform=self.ax6.transAxes, 
                     fontsize=9, verticalalignment='top', fontfamily='monospace')
        
    def setup_controls(self):
        """Setup interactive controls"""
        # Add space for controls
        plt.subplots_adjust(bottom=0.25)
        
        # Play/Pause button
        ax_play = plt.axes([0.1, 0.15, 0.08, 0.03])
        self.play_button = Button(ax_play, 'Play', color='lightgreen')
        self.play_button.on_clicked(self.toggle_play)
        
        # Reset button
        ax_reset = plt.axes([0.2, 0.15, 0.08, 0.03])
        self.reset_button = Button(ax_reset, 'Reset', color='lightcoral')
        self.reset_button.on_clicked(self.reset_simulation)
        
        # Step button
        ax_step = plt.axes([0.3, 0.15, 0.08, 0.03])
        self.step_button = Button(ax_step, 'Step', color='lightblue')
        self.step_button.on_clicked(self.step_simulation)
        
        # Landmarks toggle
        ax_landmarks = plt.axes([0.4, 0.15, 0.12, 0.03])
        self.landmarks_checkbox = CheckButtons(ax_landmarks, ['Use Landmarks'], [self.use_landmarks])
        self.landmarks_checkbox.on_clicked(self.toggle_landmarks)
        
        # Total time slider
        ax_total_time = plt.axes([0.1, 0.10, 0.6, 0.02])
        self.total_time_slider = Slider(
            ax_total_time, 'Total Time (s)', 5, 100, valinit=self.total_time,
            valstep=1, color='blue'
        )
        self.total_time_slider.on_changed(self.on_total_time_change)
        
        # Landmark count slider
        ax_landmark_count = plt.axes([0.1, 0.07, 0.6, 0.02])
        self.landmark_count_slider = Slider(
            ax_landmark_count, 'Landmark Count', 1, 13, valinit=self.landmark_count,
            valstep=1, color='green'
        )
        self.landmark_count_slider.on_changed(self.on_landmark_count_change)
        
        # Linear noise slider
        ax_linear_noise = plt.axes([0.1, 0.04, 0.6, 0.02])
        self.linear_noise_slider = Slider(
            ax_linear_noise, 'Linear Noise', 0, 0.5, valinit=self.linear_noise_std,
            valstep=0.01, color='red'
        )
        self.linear_noise_slider.on_changed(self.on_linear_noise_change)
        
    def toggle_play(self, event):
        """Toggle play/pause"""
        self.is_animating = not self.is_animating
        if self.is_animating:
            self.play_button.label.set_text('Pause')
            self.play_button.color = 'lightyellow'
            self.start_simulation()
        else:
            self.play_button.label.set_text('Play')
            self.play_button.color = 'lightgreen'
            
    def reset_simulation(self, event=None):
        """Reset simulation to initial state"""
        self.current_step = 0
        self.is_animating = False
        
        # Only update button if event was provided (manual reset)
        if event is not None:
            self.play_button.label.set_text('Play')
            self.play_button.color = 'lightgreen'
        
        # Regenerate landmarks and trajectories with current parameters
        self.landmarks = self.generate_landmarks()
        self.times = np.arange(0, self.total_time, self.dt)
        self.initialize_trajectories()
        
        # Clear error plot lines
        self.clear_error_plot()
        
        # Update landmark plots
        self.update_landmark_plots()
        
        # Update plots
        self.update_plots()
        self.update_configuration_display()
        
    def clear_error_plot(self):
        """Clear all error plot lines"""
        self.pos_error_line.set_data([], [])
        self.ekf_pos_error_line.set_data([], [])
        self.angle_error_line.set_data([], [])
        self.ekf_angle_error_line.set_data([], [])
        
        # Reset axis limits
        self.ax2.set_xlim(0, self.total_time)
        self.ax2.set_ylim(0, 1)
        self.ax3.set_xlim(0, self.total_time)
        self.ax3.set_ylim(0, 1)
        
    def step_simulation(self, event=None):
        """Step simulation by one time step"""
        if self.current_step < len(self.times) - 1:
            self.run_single_step()
            
    def toggle_landmarks(self, use_landmarks):
        """Toggle landmark usage"""
        self.use_landmarks = use_landmarks
        
    def on_linear_noise_change(self, val):
        """Handle linear noise slider change"""
        self.linear_noise_std = val
        # Update measurement noise covariance
        self.update_measurement_noise()
        
    def on_total_time_change(self, val):
        """Handle total time slider change"""
        self.total_time = val
        # Auto-reset to apply new configuration
        self.reset_simulation(None)
        
    def on_landmark_count_change(self, val):
        """Handle landmark count slider change"""
        self.landmark_count = val
        # Auto-reset to apply new configuration
        self.reset_simulation(None)
        
    def run_single_step(self):
        """Run a single simulation step"""
        if self.current_step >= len(self.times) - 1:
            return
        
        # Get true velocities from trajectory
        if self.current_step > 0:
            true_pos = self.true_trajectory[self.current_step]
            prev_pos = self.true_trajectory[self.current_step - 1]
            
            # Calculate true velocities
            dx = true_pos[0] - prev_pos[0]
            dy = true_pos[1] - prev_pos[1]
            dtheta = true_pos[2] - prev_pos[2]
            
            true_linear_vel = np.sqrt(dx**2 + dy**2) / self.dt
            true_angular_vel = dtheta / self.dt
            
            # Add noise to measurements
            measured_linear_vel, measured_angular_vel = self.add_sensor_noise(true_linear_vel, true_angular_vel)
            
            # Store velocities
            self.true_linear_velocities.append(true_linear_vel)
            self.true_angular_velocities.append(true_angular_vel)
            self.linear_velocities.append(measured_linear_vel)
            self.angular_velocities.append(measured_angular_vel)
            
            # EKF Prediction step
            self.ekf_predict(measured_linear_vel, measured_angular_vel, self.dt)
            
            # EKF Update step with landmark measurements
            if self.use_landmarks:
                # Use true position for landmark measurements (not EKF estimate to avoid feedback)
                true_pos = self.true_trajectory[self.current_step]
                measurements = self.calculate_landmark_measurements(true_pos)
                self.ekf_update(measurements)
            
            # Store EKF estimate
            self.ekf_trajectory.append(self.x.copy())
            
            # Update estimated trajectory (simple odometry for comparison)
            est_pos = self.estimated_trajectory[self.current_step - 1]
            new_x, new_y, new_theta = self.update_odometry(measured_linear_vel, measured_angular_vel, self.dt)
            self.estimated_trajectory[self.current_step] = [new_x, new_y, new_theta]
            
            # Calculate errors
            true_pos = self.true_trajectory[self.current_step]
            
            # Simple odometry errors
            position_error = np.sqrt((true_pos[0] - new_x)**2 + (true_pos[1] - new_y)**2)
            orientation_error = true_pos[2] - new_theta
            # Wrap angle error to [-pi, pi] range
            orientation_error = np.arctan2(np.sin(orientation_error), np.cos(orientation_error))
            # Convert angle error to degrees
            orientation_error_deg = np.degrees(abs(orientation_error))
            self.position_errors.append(position_error)
            self.orientation_errors.append(orientation_error_deg)
            
            # EKF errors
            ekf_position_error = np.sqrt((true_pos[0] - self.x[0])**2 + (true_pos[1] - self.x[1])**2)
            ekf_orientation_error = true_pos[2] - self.x[2]
            # Wrap angle error to [-pi, pi] range
            ekf_orientation_error = np.arctan2(np.sin(ekf_orientation_error), np.cos(ekf_orientation_error))
            # Convert angle error to degrees
            ekf_orientation_error_deg = np.degrees(abs(ekf_orientation_error))
            self.ekf_position_errors.append(ekf_position_error)
            self.ekf_orientation_errors.append(ekf_orientation_error_deg)
        
        self.current_step += 1
        
        # Update plots
        self.update_plots()
        self.update_configuration_display()
        
    # GUI Integration Methods
    def start_simulation(self):
        """Start the simulation"""
        if not self.is_animating:
            self.is_animating = True
            self.animation_thread = threading.Thread(target=self.animation_loop)
            self.animation_thread.daemon = True
            self.animation_thread.start()
            
    def stop_simulation(self):
        """Stop the simulation"""
        self.is_animating = False
        
    def animation_loop(self):
        """Animation loop for continuous simulation"""
        while self.is_animating and self.current_step < len(self.times) - 1:
            self.run_single_step()
            
            # Trigger GUI plot update if callback is set
            if self.plot_update_callback:
                self.plot_update_callback()
            
    def initialize_ekf(self):
        """Initialize Extended Kalman Filter with appropriate parameters"""
        # State vector: [x, y, theta]
        self.x = np.array([0.0, 0.0, 0.0])  # Initial state estimate
        
        # State covariance matrix (3x3) - start with moderate uncertainty
        # This allows the EKF to converge more quickly from initial errors
        self.P = np.diag([0.1, 0.1, 0.01])  # Initial uncertainty
        
        # Process noise covariance (3x3) - should match sensor noise characteristics
        # Scale with sensor noise parameters for realistic performance
        self.Q = np.diag([self.linear_noise_std**2, self.linear_noise_std**2, self.angular_noise_std**2])
        
        # Measurement noise covariance will be updated dynamically
        self.update_measurement_noise()
        
        # EKF state history for plotting
        self.ekf_trajectory = []
        
    def update_measurement_noise(self):
        """Update measurement noise covariance based on current noise parameters"""
        # Use increased measurement noise for better stability
        # This makes the EKF less sensitive to measurement noise
        self.R = np.diag([self.landmark_noise_std**2 * 2, self.landmark_angle_noise_std**2 * 2])
        
    def ekf_predict(self, linear_vel, angular_vel, dt):
        """EKF prediction step (motion update) with appropriate noise handling"""
        # Current state
        x, y, theta = self.x
        
        # Predict new state
        new_x = x + linear_vel * dt * np.cos(theta)
        new_y = y + linear_vel * dt * np.sin(theta)
        new_theta = theta + angular_vel * dt
        
        # Normalize angle
        new_theta = np.arctan2(np.sin(new_theta), np.cos(new_theta))
        
        # State transition matrix (Jacobian of motion model)
        F = np.array([
            [1, 0, -linear_vel * dt * np.sin(theta)],
            [0, 1,  linear_vel * dt * np.cos(theta)],
            [0, 0,  1]
        ])
        
        # Process noise - scale with time step and sensor noise
        # Use more conservative scaling for better stability
        Q_scaled = self.Q * dt * 0.5  # Reduced scaling factor for stability
        
        # Update state and covariance
        self.x = np.array([new_x, new_y, new_theta])
        self.P = F @ self.P @ F.T + Q_scaled
        
    def ekf_update(self, landmark_measurements):
        """EKF update step (measurement update) with appropriate noise handling"""
        if not landmark_measurements:
            return
            
        for i, (range_meas, bearing_meas) in enumerate(landmark_measurements):
            if i >= len(self.landmarks):
                break
                
            landmark = self.landmarks[i]
            x, y, theta = self.x
            
            # Predicted measurement
            dx = landmark[0] - x
            dy = landmark[1] - y
            predicted_range = np.sqrt(dx**2 + dy**2)
            predicted_bearing = np.arctan2(dy, dx) - theta
            
            # Normalize bearing
            predicted_bearing = np.arctan2(np.sin(predicted_bearing), np.cos(predicted_bearing))
            
            # Measurement Jacobian
            if predicted_range > 0.1:  # Avoid singularity
                H = np.array([
                    [-dx/predicted_range, -dy/predicted_range, 0],
                    [dy/predicted_range**2, -dx/predicted_range**2, -1]
                ])
                
                # Kalman gain
                S = H @ self.P @ H.T + self.R
                
                # Check for numerical stability
                if np.linalg.cond(S) < 1e12:  # Standard condition number check
                    try:
                        K = self.P @ H.T @ np.linalg.inv(S)
                        
                        # Innovation
                        innovation = np.array([range_meas - predicted_range, 
                                             bearing_meas - predicted_bearing])
                        
                        # Normalize bearing innovation
                        innovation[1] = np.arctan2(np.sin(innovation[1]), np.cos(innovation[1]))
                        
                        # Update state and covariance
                        self.x = self.x + K @ innovation
                        self.x[2] = np.arctan2(np.sin(self.x[2]), np.cos(self.x[2]))  # Normalize angle
                        
                        I = np.eye(3)
                        self.P = (I - K @ H) @ self.P
                        
                        # Ensure covariance remains positive definite
                        self.P = (self.P + self.P.T) / 2  # Make symmetric
                        min_eig = np.min(np.real(np.linalg.eigvals(self.P)))
                        if min_eig < 1e-6:
                            self.P += (1e-6 - min_eig) * np.eye(3)
                            
                    except np.linalg.LinAlgError:
                        # Skip update if matrix is singular
                        continue
        
    def update_parameters(self, total_time, linear_noise):
        """Update simulation parameters"""
        self.total_time = total_time
        self.linear_noise_std = linear_noise
        
        # Update EKF parameters
        self.Q = np.diag([self.linear_noise_std**2, self.linear_noise_std**2, self.angular_noise_std**2])
        
        # Reset simulation to apply new parameters
        self.reset_simulation()
        
    def run(self):
        """Run the demonstration"""
        plt.show()

    def set_plot_update_callback(self, callback):
        """Set callback function for GUI plot updates"""
        self.plot_update_callback = callback

def main():
    """Main function to run the wheel odometry demonstration"""
    print("Wheel Odometry Demonstration")
    print("=" * 50)
    print("This demo shows:")
    print("1. True rectangular trajectory")
    print("2. Estimated trajectory with sensor noise")
    print("3. Landmark-based position correction")
    print("4. Error analysis over time")
    print("5. Sensor data visualization")
    print("\nControls:")
    print("- Play/Pause: Start/stop simulation")
    print("- Reset: Return to initial state")
    print("- Step: Advance one time step")
    print("- Use Landmarks: Toggle landmark corrections")
    print("- Linear Noise: Adjust sensor noise level")
    print("\nFeatures:")
    print("- Real-time trajectory visualization")
    print("- Sensor noise simulation")
    print("- Landmark ranging and bearing measurements")
    print("- Error tracking and analysis")
    print("- Interactive configuration")
    
    demo = WheelOdometryDemo()
    demo.run()

if __name__ == "__main__":
    main() 