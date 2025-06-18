#!/usr/bin/env python3

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

# Import demo modules
from pose_visualizer import PoseVisualizer
from rotation_demo import RotationDemo
from position_3d_demo import Position3DDemo
from wheel_odometry_demo import WheelOdometryDemo

class OdometryGUIDemo:
    def __init__(self):
        """Initialize the main GUI application"""
        self.root = tk.Tk()
        self.root.title("Odometry & Robotics Demo Suite")
        self.root.geometry("1400x900")
        
        # Configure style
        self.setup_style()
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Initialize demo instances
        self.demo_instances = {}
        
        # Setup status bar first
        self.setup_status_bar()
        
        # Create tabs
        self.create_tabs()
        
        # Setup menu
        self.setup_menu()
        
    def setup_style(self):
        """Setup the application style"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure notebook style
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 10))
        
        # Configure frame style
        style.configure('Main.TFrame', background='#ffffff')
        
    def create_tabs(self):
        """Create all demo tabs"""
        # Tab 1: Pose Visualizer
        self.create_pose_tab()
        
        # Tab 2: Rotation Demo
        self.create_rotation_tab()
        
        # Tab 3: 3D Position Demo
        self.create_3d_position_tab()
        
        # Tab 4: Wheel Odometry Demo
        self.create_wheel_odometry_tab()
        
    def create_pose_tab(self):
        """Create the pose visualization tab"""
        pose_frame = ttk.Frame(self.notebook)
        self.notebook.add(pose_frame, text="Pose Visualizer")
        
        # Create title
        title_label = ttk.Label(pose_frame, text="Pose Visualization Demo", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Create description
        desc_text = """This demo shows 2D pose visualization with position (x, y) and orientation (θ).
        Use the sliders to control the pose parameters and see real-time updates."""
        desc_label = ttk.Label(pose_frame, text=desc_text, wraplength=600, 
                              font=('Arial', 10))
        desc_label.pack(pady=5)
        
        # Create matplotlib figure
        self.pose_fig = Figure(figsize=(10, 6), dpi=100)
        self.pose_canvas = FigureCanvasTkAgg(self.pose_fig, pose_frame)
        self.pose_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create toolbar
        pose_toolbar = NavigationToolbar2Tk(self.pose_canvas, pose_frame)
        pose_toolbar.update()
        
        # Create controls frame
        controls_frame = ttk.Frame(pose_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Sliders
        self.create_pose_controls(controls_frame)
        
        # Initialize pose visualizer
        self.pose_visualizer = PoseVisualizer(self.pose_fig)
        self.demo_instances['pose'] = self.pose_visualizer
        
    def create_pose_controls(self, parent):
        """Create controls for pose visualization"""
        # X position slider
        ttk.Label(parent, text="X Position:").grid(row=0, column=0, padx=5, pady=5)
        self.x_slider = ttk.Scale(parent, from_=-5, to=5, orient=tk.HORIZONTAL, 
                                 command=self.update_pose)
        self.x_slider.set(0)
        self.x_slider.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Y position slider
        ttk.Label(parent, text="Y Position:").grid(row=1, column=0, padx=5, pady=5)
        self.y_slider = ttk.Scale(parent, from_=-5, to=5, orient=tk.HORIZONTAL, 
                                 command=self.update_pose)
        self.y_slider.set(0)
        self.y_slider.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # Orientation slider
        ttk.Label(parent, text="Orientation (deg):").grid(row=2, column=0, padx=5, pady=5)
        self.theta_slider = ttk.Scale(parent, from_=-180, to=180, orient=tk.HORIZONTAL, 
                                     command=self.update_pose)
        self.theta_slider.set(0)
        self.theta_slider.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        # Configure grid weights
        parent.columnconfigure(1, weight=1)
        
    def create_rotation_tab(self):
        """Create the rotation demo tab"""
        rotation_frame = ttk.Frame(self.notebook)
        self.notebook.add(rotation_frame, text="Rotation Demo")
        
        # Create title
        title_label = ttk.Label(rotation_frame, text="2D & 3D Rotation Demo", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Create description
        desc_text = """This demo shows 2D point rotation, 2D vector rotation, and 3D vector rotation.
        Use the theta slider to control rotation angle and see real-time matrix transformations."""
        desc_label = ttk.Label(rotation_frame, text=desc_text, wraplength=600, 
                              font=('Arial', 10))
        desc_label.pack(pady=5)
        
        # Create matplotlib figure
        self.rotation_fig = Figure(figsize=(12, 8), dpi=100)
        self.rotation_canvas = FigureCanvasTkAgg(self.rotation_fig, rotation_frame)
        self.rotation_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create toolbar
        rotation_toolbar = NavigationToolbar2Tk(self.rotation_canvas, rotation_frame)
        rotation_toolbar.update()
        
        # Create controls frame
        controls_frame = ttk.Frame(rotation_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Initialize rotation demo
        self.rotation_demo = RotationDemo(self.rotation_fig)
        self.demo_instances['rotation'] = self.rotation_demo
        
        # Create rotation controls
        self.create_rotation_controls(controls_frame)
        
    def create_rotation_controls(self, parent):
        """Create controls for rotation demo"""
        # Theta slider
        ttk.Label(parent, text="Rotation Angle (deg):").grid(row=0, column=0, padx=5, pady=5)
        self.theta_rotation_slider = ttk.Scale(parent, from_=0, to=360, orient=tk.HORIZONTAL, 
                                             command=self.update_rotation)
        self.theta_rotation_slider.set(0)
        self.theta_rotation_slider.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Animation controls
        ttk.Button(parent, text="Play", command=self.start_rotation_animation).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(parent, text="Pause", command=self.stop_rotation_animation).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(parent, text="Reset", command=self.reset_rotation).grid(row=0, column=4, padx=5, pady=5)
        
        # Configure grid weights
        parent.columnconfigure(1, weight=1)
        
    def create_3d_position_tab(self):
        """Create the 3D position demo tab"""
        pos3d_frame = ttk.Frame(self.notebook)
        self.notebook.add(pos3d_frame, text="3D Position Demo")
        
        # Create title
        title_label = ttk.Label(pos3d_frame, text="3D Position & Coordinate Systems", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Create description
        desc_text = """This demo shows 3D position representation with orthogonal basis vectors.
        Use the sliders to control the 3D position and see coordinate transformations."""
        desc_label = ttk.Label(pos3d_frame, text=desc_text, wraplength=600, 
                              font=('Arial', 10))
        desc_label.pack(pady=5)
        
        # Create matplotlib figure
        self.pos3d_fig = Figure(figsize=(10, 8), dpi=100)
        self.pos3d_canvas = FigureCanvasTkAgg(self.pos3d_fig, pos3d_frame)
        self.pos3d_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create toolbar
        pos3d_toolbar = NavigationToolbar2Tk(self.pos3d_canvas, pos3d_frame)
        pos3d_toolbar.update()
        
        # Create controls frame
        controls_frame = ttk.Frame(pos3d_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Initialize 3D position demo
        self.pos3d_demo = Position3DDemo(self.pos3d_fig)
        self.demo_instances['pos3d'] = self.pos3d_demo
        
        # Create 3D position controls
        self.create_3d_position_controls(controls_frame)
        
    def create_3d_position_controls(self, parent):
        """Create controls for 3D position demo"""
        # X position slider
        ttk.Label(parent, text="X Position:").grid(row=0, column=0, padx=5, pady=5)
        self.x3d_slider = ttk.Scale(parent, from_=-3, to=3, orient=tk.HORIZONTAL, 
                                   command=self.update_3d_position)
        self.x3d_slider.set(0)
        self.x3d_slider.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Y position slider
        ttk.Label(parent, text="Y Position:").grid(row=1, column=0, padx=5, pady=5)
        self.y3d_slider = ttk.Scale(parent, from_=-3, to=3, orient=tk.HORIZONTAL, 
                                   command=self.update_3d_position)
        self.y3d_slider.set(0)
        self.y3d_slider.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # Z position slider
        ttk.Label(parent, text="Z Position:").grid(row=2, column=0, padx=5, pady=5)
        self.z3d_slider = ttk.Scale(parent, from_=-3, to=3, orient=tk.HORIZONTAL, 
                                   command=self.update_3d_position)
        self.z3d_slider.set(0)
        self.z3d_slider.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        # Configure grid weights
        parent.columnconfigure(1, weight=1)
        
    def create_wheel_odometry_tab(self):
        """Create the wheel odometry demo tab"""
        odometry_frame = ttk.Frame(self.notebook)
        self.notebook.add(odometry_frame, text="Wheel Odometry Demo")
        
        # Create title
        title_label = ttk.Label(odometry_frame, text="Wheel Odometry & EKF Localization", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Create description
        desc_text = """This demo shows wheel odometry with sensor noise, landmark-based corrections using EKF,
        and error analysis. Compare simple odometry vs. EKF performance."""
        desc_label = ttk.Label(odometry_frame, text=desc_text, wraplength=600, 
                              font=('Arial', 10))
        desc_label.pack(pady=5)
        
        # Create matplotlib figure
        self.odometry_fig = Figure(figsize=(14, 10), dpi=100)
        self.odometry_canvas = FigureCanvasTkAgg(self.odometry_fig, odometry_frame)
        self.odometry_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create toolbar
        odometry_toolbar = NavigationToolbar2Tk(self.odometry_canvas, odometry_frame)
        odometry_toolbar.update()
        
        # Create controls frame
        controls_frame = ttk.Frame(odometry_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Initialize wheel odometry demo
        self.odometry_demo = WheelOdometryDemo(self.odometry_fig)
        self.odometry_demo.set_plot_update_callback(self.update_odometry_plots)
        self.demo_instances['odometry'] = self.odometry_demo
        
        # Create odometry controls
        self.create_odometry_controls(controls_frame)
        
    def create_odometry_controls(self, parent):
        """Create controls for wheel odometry demo"""
        # Control buttons
        ttk.Button(parent, text="Play", command=self.start_odometry_simulation).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(parent, text="Pause", command=self.stop_odometry_simulation).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Reset", command=self.reset_odometry_simulation).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(parent, text="Step", command=self.step_odometry_simulation).grid(row=0, column=3, padx=5, pady=5)
        
        # Landmarks toggle
        self.landmarks_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Use Landmarks", variable=self.landmarks_var, 
                       command=self.toggle_landmarks).grid(row=0, column=4, padx=5, pady=5)
        
        # Parameter sliders
        ttk.Label(parent, text="Total Time (s):").grid(row=1, column=0, padx=5, pady=5)
        self.total_time_slider = ttk.Scale(parent, from_=10, to=100, orient=tk.HORIZONTAL, 
                                          command=self.update_odometry_params)
        self.total_time_slider.set(50)
        self.total_time_slider.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='ew')
        
        ttk.Label(parent, text="Linear Noise:").grid(row=2, column=0, padx=5, pady=5)
        self.linear_noise_slider = ttk.Scale(parent, from_=0, to=0.5, orient=tk.HORIZONTAL, 
                                           command=self.update_odometry_params)
        self.linear_noise_slider.set(0.1)
        self.linear_noise_slider.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky='ew')
        
        # Configure grid weights
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(2, weight=1)
        
    def setup_menu(self):
        """Setup the application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def update_pose(self, value=None):
        """Update pose visualization"""
        try:
            x = self.x_slider.get()
            y = self.y_slider.get()
            theta = np.radians(self.theta_slider.get())
            
            self.pose_visualizer.update_pose(x, y, theta)
            self.pose_canvas.draw()
            self.status_bar.config(text=f"Pose: x={x:.2f}, y={y:.2f}, θ={self.theta_slider.get():.1f}°")
        except Exception as e:
            self.status_bar.config(text=f"Error: {str(e)}")
            
    def update_rotation(self, value=None):
        """Update rotation demo"""
        try:
            theta = np.radians(self.theta_rotation_slider.get())
            self.rotation_demo.update_rotation(theta)
            self.rotation_canvas.draw()
            self.status_bar.config(text=f"Rotation angle: {self.theta_rotation_slider.get():.1f}°")
        except Exception as e:
            self.status_bar.config(text=f"Error: {str(e)}")
            
    def update_3d_position(self, value=None):
        """Update 3D position demo"""
        try:
            x = self.x3d_slider.get()
            y = self.y3d_slider.get()
            z = self.z3d_slider.get()
            
            self.pos3d_demo.update_position(x, y, z)
            self.pos3d_canvas.draw()
            self.status_bar.config(text=f"3D Position: x={x:.2f}, y={y:.2f}, z={z:.2f}")
        except Exception as e:
            self.status_bar.config(text=f"Error: {str(e)}")
            
    def start_rotation_animation(self):
        """Start rotation animation"""
        self.rotation_demo.start_animation()
        self.status_bar.config(text="Rotation animation started")
        
    def stop_rotation_animation(self):
        """Stop rotation animation"""
        self.rotation_demo.stop_animation()
        self.status_bar.config(text="Rotation animation stopped")
        
    def reset_rotation(self):
        """Reset rotation demo"""
        self.rotation_demo.reset()
        self.theta_rotation_slider.set(0)
        self.rotation_canvas.draw()
        self.status_bar.config(text="Rotation demo reset")
        
    def start_odometry_simulation(self):
        """Start wheel odometry simulation"""
        self.odometry_demo.start_simulation()
        self.odometry_canvas.draw()
        self.status_bar.config(text="Odometry simulation started")
        
    def stop_odometry_simulation(self):
        """Stop wheel odometry simulation"""
        self.odometry_demo.stop_simulation()
        self.status_bar.config(text="Odometry simulation stopped")
        
    def reset_odometry_simulation(self):
        """Reset wheel odometry simulation"""
        self.odometry_demo.reset_simulation()
        self.odometry_canvas.draw()
        self.status_bar.config(text="Odometry simulation reset")
        
    def step_odometry_simulation(self):
        """Step wheel odometry simulation"""
        self.odometry_demo.step_simulation()
        self.odometry_canvas.draw()
        self.status_bar.config(text="Odometry simulation stepped")
        
    def toggle_landmarks(self):
        """Toggle landmark usage in odometry"""
        use_landmarks = self.landmarks_var.get()
        self.odometry_demo.toggle_landmarks(use_landmarks)
        self.status_bar.config(text=f"Landmarks {'enabled' if use_landmarks else 'disabled'}")
        
    def update_odometry_params(self, value=None):
        """Update odometry parameters"""
        try:
            total_time = self.total_time_slider.get()
            linear_noise = self.linear_noise_slider.get()
            
            self.odometry_demo.update_parameters(total_time, linear_noise)
            self.status_bar.config(text=f"Parameters updated: T={total_time}s, noise={linear_noise:.3f}")
        except Exception as e:
            self.status_bar.config(text=f"Error: {str(e)}")
            
    def update_odometry_plots(self):
        """Update odometry plots (called from animation thread)"""
        try:
            # Schedule the canvas update in the main thread
            self.odometry_canvas.draw()
        except Exception as e:
            # Ignore errors from background thread updates
            pass
            
    def show_about(self):
        """Show about dialog"""
        about_text = """Odometry & Robotics Demo Suite

A comprehensive GUI application demonstrating:
• 2D Pose Visualization
• 2D & 3D Rotation
• 3D Position & Coordinate Systems
• Wheel Odometry with EKF Localization

Created for educational and research purposes.
"""
        messagebox.showinfo("About", about_text)
        
    def run(self):
        """Run the GUI application"""
        # Initialize first tab
        self.update_pose()
        self.pose_canvas.draw()
        
        self.update_rotation()
        self.rotation_canvas.draw()
        
        self.update_3d_position()
        self.pos3d_canvas.draw()
        
        # Start the main loop
        self.root.mainloop()

def main():
    """Main function to run the GUI application"""
    print("Odometry & Robotics Demo Suite")
    print("=" * 50)
    print("Starting GUI application...")
    
    try:
        app = OdometryGUIDemo()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main() 