#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import matplotlib.animation as animation

class PoseVisualizer:
    def __init__(self, fig=None):
        """Initialize the pose visualizer"""
        if fig is None:
            self.fig = plt.figure(figsize=(10, 6))
        else:
            self.fig = fig
            
        self.setup_plot()
        
    def setup_plot(self):
        """Setup the pose visualization plot"""
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(-6, 6)
        self.ax.set_ylim(-6, 6)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title('2D Pose Visualization', fontsize=14, fontweight='bold')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        
        # Initialize pose elements
        self.pose_marker = None
        self.orientation_arrow = None
        self.coordinate_frame_elements = []  # List to track all frame elements
        
        # Draw coordinate axes
        self.draw_coordinate_axes()
        
    def draw_coordinate_axes(self):
        """Draw the coordinate system axes"""
        # X-axis
        self.ax.arrow(0, 0, 5, 0, head_width=0.1, head_length=0.2, fc='red', ec='red', alpha=0.7)
        self.ax.text(5.2, 0, 'X', fontsize=12, color='red')
        
        # Y-axis
        self.ax.arrow(0, 0, 0, 5, head_width=0.1, head_length=0.2, fc='green', ec='green', alpha=0.7)
        self.ax.text(0, 5.2, 'Y', fontsize=12, color='green')
        
        # Origin
        self.ax.plot(0, 0, 'ko', markersize=8)
        self.ax.text(-0.3, -0.3, 'O', fontsize=12)
        
    def update_pose(self, x, y, theta):
        """Update the pose visualization"""
        # Clear previous pose elements
        if self.pose_marker is not None:
            self.pose_marker.remove()
            self.pose_marker = None
        if self.orientation_arrow is not None:
            self.orientation_arrow.remove()
            self.orientation_arrow = None
            
        # Clear previous coordinate frame elements
        for element in self.coordinate_frame_elements:
            if element is not None:
                element.remove()
        self.coordinate_frame_elements.clear()
            
        # Draw pose marker
        self.pose_marker = self.ax.plot(x, y, 'bo', markersize=12, label='Pose')[0]
        
        # Draw orientation arrow
        arrow_length = 1.0
        dx = arrow_length * np.cos(theta)
        dy = arrow_length * np.sin(theta)
        self.orientation_arrow = self.ax.arrow(x, y, dx, dy, head_width=0.2, 
                                             head_length=0.3, fc='blue', ec='blue', alpha=0.8)
        
        # Draw local coordinate frame
        self.draw_local_frame(x, y, theta)
        
        # Update legend
        self.ax.legend()
        
    def draw_local_frame(self, x, y, theta):
        """Draw the local coordinate frame at the pose"""
        frame_length = 0.8
        
        # Local X-axis (red)
        dx_x = frame_length * np.cos(theta)
        dy_x = frame_length * np.sin(theta)
        self.coordinate_frame_elements.append(self.ax.arrow(x, y, dx_x, dy_x, head_width=0.1, head_length=0.15, 
                     fc='red', ec='red', alpha=0.6))
        
        # Local Y-axis (green)
        dx_y = frame_length * np.cos(theta + np.pi/2)
        dy_y = frame_length * np.sin(theta + np.pi/2)
        self.coordinate_frame_elements.append(self.ax.arrow(x, y, dx_y, dy_y, head_width=0.1, head_length=0.15, 
                     fc='green', ec='green', alpha=0.6))
        
    def get_pose_info(self, x, y, theta):
        """Get formatted pose information"""
        return f"Position: ({x:.2f}, {y:.2f})\nOrientation: {np.degrees(theta):.1f}°"
        
    def reset(self):
        """Reset the visualization"""
        self.update_pose(0, 0, 0)
        
    def animate_pose(self, x_traj, y_traj, theta_traj, interval=100):
        """Animate pose along a trajectory"""
        def animate(frame):
            if frame < len(x_traj):
                self.update_pose(x_traj[frame], y_traj[frame], theta_traj[frame])
            return []
            
        anim = animation.FuncAnimation(self.fig, animate, frames=len(x_traj), 
                                      interval=interval, blit=False, repeat=True)
        return anim

def main():
    """Standalone demo function"""
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Slider
    
    # Create figure
    fig = plt.figure(figsize=(10, 6))
    
    # Create pose visualizer
    visualizer = PoseVisualizer(fig)
    
    # Add sliders
    ax_x = plt.axes([0.1, 0.1, 0.6, 0.03])
    ax_y = plt.axes([0.1, 0.05, 0.6, 0.03])
    ax_theta = plt.axes([0.1, 0.0, 0.6, 0.03])
    
    x_slider = Slider(ax_x, 'X', -5, 5, valinit=0)
    y_slider = Slider(ax_y, 'Y', -5, 5, valinit=0)
    theta_slider = Slider(ax_theta, 'θ (deg)', -180, 180, valinit=0)
    
    def update(val):
        x = x_slider.val
        y = y_slider.val
        theta = np.radians(theta_slider.val)
        visualizer.update_pose(x, y, theta)
        fig.canvas.draw_idle()
        
    x_slider.on_changed(update)
    y_slider.on_changed(update)
    theta_slider.on_changed(update)
    
    # Initialize
    visualizer.update_pose(0, 0, 0)
    
    plt.show()

if __name__ == "__main__":
    main() 