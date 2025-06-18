#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import math
import threading

class RotationDemo:
    def __init__(self, fig=None):
        if fig is None:
            self.fig = plt.figure(figsize=(16, 10))
        else:
            self.fig = fig
        self.setup_plots()
        self.setup_animation()
        self.setup_controls()
        
    def setup_plots(self):
        """Setup the three subplots for different rotation demonstrations"""
        # 2D Point Rotation
        self.ax1 = self.fig.add_subplot(2, 3, 1)
        self.ax1.set_xlim(-2, 2)
        self.ax1.set_ylim(-2, 2)
        self.ax1.set_aspect('equal')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_title('2D Point Rotation', fontsize=12, fontweight='bold')
        self.ax1.set_xlabel('X')
        self.ax1.set_ylabel('Y')
        
        # 2D Vector Rotation
        self.ax2 = self.fig.add_subplot(2, 3, 2)
        self.ax2.set_xlim(-2, 2)
        self.ax2.set_ylim(-2, 2)
        self.ax2.set_aspect('equal')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.set_title('2D Vector Rotation', fontsize=12, fontweight='bold')
        self.ax2.set_xlabel('X')
        self.ax2.set_ylabel('Y')
        
        # 3D Vector Rotation
        self.ax3 = self.fig.add_subplot(2, 3, 3, projection='3d')
        self.ax3.set_xlim(-2, 2)
        self.ax3.set_ylim(-2, 2)
        self.ax3.set_zlim(-2, 2)
        self.ax3.set_title('3D Vector Rotation', fontsize=12, fontweight='bold')
        self.ax3.set_xlabel('X')
        self.ax3.set_ylabel('Y')
        self.ax3.set_zlabel('Z')
        
        # Rotation Matrix Display
        self.ax4 = self.fig.add_subplot(2, 3, 4)
        self.ax4.axis('off')
        self.ax4.set_title('Rotation Matrix', fontsize=12, fontweight='bold')
        
        # Rotation Formula Display
        self.ax5 = self.fig.add_subplot(2, 3, 5)
        self.ax5.axis('off')
        self.ax5.set_title('Rotation Formulas', fontsize=12, fontweight='bold')
        
        # Animation Control
        self.ax6 = self.fig.add_subplot(2, 3, 6)
        self.ax6.axis('off')
        self.ax6.set_title('Controls', fontsize=12, fontweight='bold')
        
        # plt.tight_layout()  # Removed to avoid compatibility warning
        
    def setup_animation(self):
        """Initialize animation elements"""
        # Initial points and vectors
        self.point_2d = np.array([1.0, 0.5])
        self.vector_2d = np.array([1.0, 0.0])
        self.vector_3d = np.array([1.0, 0.0, 0.5])
        
        # Original positions (for reference)
        self.original_point_2d = self.point_2d.copy()
        self.original_vector_2d = self.vector_2d.copy()
        self.original_vector_3d = self.vector_3d.copy()
        
        # Animation state
        self.theta = 0.0
        self.is_animating = False
        self.animation_speed = 0.05
        
        # Setup plot elements
        self.setup_2d_point_plot()
        self.setup_2d_vector_plot()
        self.setup_3d_vector_plot()
        self.update_rotation_matrix_display()
        self.update_formula_display()
        
    def setup_2d_point_plot(self):
        """Setup 2D point rotation plot"""
        # Original point
        self.point_orig, = self.ax1.plot([], [], 'ko', markersize=8, label='Original Point')
        self.point_rot, = self.ax1.plot([], [], 'ro', markersize=8, label='Rotated Point')
        
        # Rotation path
        self.point_path, = self.ax1.plot([], [], 'r-', alpha=0.3, linewidth=1)
        
        # Center point
        self.ax1.plot(0, 0, 'k+', markersize=10, markeredgewidth=2)
        
        self.ax1.legend()
        
    def setup_2d_vector_plot(self):
        """Setup 2D vector rotation plot"""
        # Original vector
        self.vector_orig = self.ax2.arrow(0, 0, 0, 0, head_width=0.05, head_length=0.1, 
                                        fc='blue', ec='blue', alpha=0.7, label='Original Vector')
        self.vector_rot = self.ax2.arrow(0, 0, 0, 0, head_width=0.05, head_length=0.1, 
                                       fc='red', ec='red', alpha=0.7, label='Rotated Vector')
        
        # Vector path
        self.vector_path, = self.ax2.plot([], [], 'r-', alpha=0.3, linewidth=1)
        
        # Center point
        self.center_point_2d = self.ax2.plot(0, 0, 'k+', markersize=10, markeredgewidth=2)[0]
        
        self.ax2.legend()
        
    def setup_3d_vector_plot(self):
        """Setup 3D vector rotation plot"""
        # Original vector
        self.vector3d_orig = self.ax3.quiver(0, 0, 0, 0, 0, 0, color='blue', alpha=0.7, 
                                           arrow_length_ratio=0.2, label='Original Vector')
        self.vector3d_rot = self.ax3.quiver(0, 0, 0, 0, 0, 0, color='red', alpha=0.7, 
                                          arrow_length_ratio=0.2, label='Rotated Vector')
        
        # Rotation axis
        self.rotation_axis = self.ax3.quiver(0, 0, 0, 0, 0, 0, color='green', alpha=0.5, 
                                           arrow_length_ratio=0.3, linewidth=3, label='Rotation Axis')
        
        # Center point
        self.ax3.scatter(0, 0, 0, color='black', s=50, marker='o')
        
        self.ax3.legend()
        
    def rotation_matrix_2d(self, theta):
        """2D rotation matrix"""
        return np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)]
        ])
    
    def rotation_matrix_3d_z(self, theta):
        """3D rotation matrix around Z-axis"""
        return np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1]
        ])
    
    def update_plots(self, theta):
        """Update all plots with new rotation angle"""
        self.theta = theta
        
        # 2D Point Rotation
        R_2d = self.rotation_matrix_2d(theta)
        rotated_point = R_2d @ self.original_point_2d
        
        self.point_orig.set_data([self.original_point_2d[0]], [self.original_point_2d[1]])
        self.point_rot.set_data([rotated_point[0]], [rotated_point[1]])
        
        # Update path (show rotation trajectory)
        angles = np.linspace(0, theta, 50)
        path_x = []
        path_y = []
        for angle in angles:
            R_path = self.rotation_matrix_2d(angle)
            point_path = R_path @ self.original_point_2d
            path_x.append(point_path[0])
            path_y.append(point_path[1])
        self.point_path.set_data(path_x, path_y)
        
        # 2D Vector Rotation
        rotated_vector = R_2d @ self.original_vector_2d
        
        # Remove old arrows and create new ones
        if hasattr(self, 'vector_orig') and self.vector_orig:
            self.vector_orig.remove()
        if hasattr(self, 'vector_rot') and self.vector_rot:
            self.vector_rot.remove()
        
        self.vector_orig = self.ax2.arrow(0, 0, self.original_vector_2d[0], self.original_vector_2d[1], 
                                        head_width=0.05, head_length=0.1, fc='blue', ec='blue', alpha=0.7)
        self.vector_rot = self.ax2.arrow(0, 0, rotated_vector[0], rotated_vector[1], 
                                       head_width=0.05, head_length=0.1, fc='red', ec='red', alpha=0.7)
        
        # Update vector path
        path_x = []
        path_y = []
        for angle in angles:
            R_path = self.rotation_matrix_2d(angle)
            vector_path = R_path @ self.original_vector_2d
            path_x.append(vector_path[0])
            path_y.append(vector_path[1])
        self.vector_path.set_data(path_x, path_y)
        
        # 3D Vector Rotation (around Z-axis)
        R_3d = self.rotation_matrix_3d_z(theta)
        rotated_vector_3d = R_3d @ self.original_vector_3d
        
        # Update 3D vectors
        if hasattr(self, 'vector3d_orig') and self.vector3d_orig:
            self.vector3d_orig.remove()
        if hasattr(self, 'vector3d_rot') and self.vector3d_rot:
            self.vector3d_rot.remove()
        if hasattr(self, 'rotation_axis') and self.rotation_axis:
            self.rotation_axis.remove()
        
        self.vector3d_orig = self.ax3.quiver(0, 0, 0, self.original_vector_3d[0], 
                                           self.original_vector_3d[1], self.original_vector_3d[2], 
                                           color='blue', alpha=0.7, arrow_length_ratio=0.2)
        self.vector3d_rot = self.ax3.quiver(0, 0, 0, rotated_vector_3d[0], 
                                          rotated_vector_3d[1], rotated_vector_3d[2], 
                                          color='red', alpha=0.7, arrow_length_ratio=0.2)
        self.rotation_axis = self.ax3.quiver(0, 0, 0, 0, 0, 1, color='green', alpha=0.5, 
                                           arrow_length_ratio=0.3, linewidth=3)
        
        # Update displays
        self.update_rotation_matrix_display()
        
    def update_rotation_matrix_display(self):
        """Update rotation matrix display"""
        self.ax4.clear()
        self.ax4.axis('off')
        self.ax4.set_title('Rotation Matrix', fontsize=12, fontweight='bold')
        
        # 2D rotation matrix
        R_2d = self.rotation_matrix_2d(self.theta)
        
        matrix_text = "2D Rotation Matrix:\n"
        matrix_text += f"R(θ) = [cos(θ)  -sin(θ)]\n"
        matrix_text += f"       [sin(θ)   cos(θ)]\n\n"
        matrix_text += f"θ = {self.theta:.2f} rad = {np.degrees(self.theta):.1f}°\n\n"
        matrix_text += f"R = [{R_2d[0,0]:.3f}  {R_2d[0,1]:.3f}]\n"
        matrix_text += f"    [{R_2d[1,0]:.3f}  {R_2d[1,1]:.3f}]"
        
        self.ax4.text(0.1, 0.9, matrix_text, transform=self.ax4.transAxes, 
                     fontsize=10, verticalalignment='top', fontfamily='monospace')
        
    def update_formula_display(self):
        """Update formula display"""
        self.ax5.clear()
        self.ax5.axis('off')
        self.ax5.set_title('Rotation Formulas', fontsize=12, fontweight='bold')
        
        formula_text = "2D Point Rotation:\n"
        formula_text += "x' = x·cos(θ) - y·sin(θ)\n"
        formula_text += "y' = x·sin(θ) + y·cos(θ)\n\n"
        formula_text += "2D Vector Rotation:\n"
        formula_text += "v' = R(θ) · v\n\n"
        formula_text += "3D Vector Rotation (Z-axis):\n"
        formula_text += "x' = x·cos(θ) - y·sin(θ)\n"
        formula_text += "y' = x·sin(θ) + y·cos(θ)\n"
        formula_text += "z' = z"
        
        self.ax5.text(0.1, 0.9, formula_text, transform=self.ax5.transAxes, 
                     fontsize=9, verticalalignment='top', fontfamily='monospace')
        
    def setup_controls(self):
        """Setup interactive controls (optional for GUI usage)"""
        try:
            # Add space for controls
            plt.subplots_adjust(bottom=0.15)
            
            # Theta slider
            ax_slider = plt.axes([0.2, 0.05, 0.6, 0.03])
            self.theta_slider = Slider(
                ax_slider, 'θ (radians)', 0, 2*np.pi, valinit=0,
                valstep=0.01, color='lightblue'
            )
            self.theta_slider.on_changed(self.on_slider_change)
            
            # Animation controls
            ax_play = plt.axes([0.2, 0.02, 0.1, 0.02])
            self.play_button = Button(ax_play, 'Play', color='lightgreen')
            self.play_button.on_clicked(self.toggle_animation)
            
            ax_reset = plt.axes([0.35, 0.02, 0.1, 0.02])
            self.reset_button = Button(ax_reset, 'Reset', color='lightcoral')
            self.reset_button.on_clicked(self.reset_animation)
            
            # Display current angle
            self.ax6.text(0.1, 0.8, "Current Angle:", transform=self.ax6.transAxes, fontsize=10)
            self.angle_text = self.ax6.text(0.1, 0.6, "θ = 0.00 rad (0.0°)", 
                                          transform=self.ax6.transAxes, fontsize=10, 
                                          fontfamily='monospace', color='red')
        except Exception as e:
            # If controls setup fails (e.g., in GUI mode), just continue
            print(f"Controls setup skipped: {e}")
            
    def on_slider_change(self, val):
        """Handle slider change"""
        self.update_plots(val)
        self.update_angle_display()
        
    def update_angle_display(self):
        """Update angle display"""
        self.angle_text.set_text(f"θ = {self.theta:.2f} rad ({np.degrees(self.theta):.1f}°)")
        
    def toggle_animation(self, event):
        """Toggle animation on/off"""
        self.is_animating = not self.is_animating
        if self.is_animating:
            self.play_button.label.set_text('Pause')
            self.play_button.color = 'lightyellow'
            self.animate()
        else:
            self.play_button.label.set_text('Play')
            self.play_button.color = 'lightgreen'
            
    def animate(self):
        """Animate rotation"""
        if not self.is_animating:
            return
            
        # Increment theta
        self.theta += self.animation_speed
        if self.theta > 2*np.pi:
            self.theta = 0
            
        # Update slider
        self.theta_slider.set_val(self.theta)
        
        # Update plots and redraw
        self.update_plots(self.theta)
        self.update_angle_display()
        self.fig.canvas.draw()
        
        # Schedule next frame using a timer that works with any backend
        if self.is_animating:
            try:
                # Try to use the canvas timer if available
                if hasattr(self.fig.canvas, 'get_tk_widget'):
                    self.fig.canvas.get_tk_widget().after(50, self.animate)
                else:
                    # Fallback: use a simple approach
                    plt.pause(0.05)
                    if self.is_animating:
                        self.animate()
            except:
                # Final fallback
                plt.pause(0.05)
                if self.is_animating:
                    self.animate()
        
    def reset_animation(self, event):
        """Reset animation to initial state"""
        self.theta = 0
        self.theta_slider.set_val(0)
        self.update_plots(0)
        self.update_angle_display()
        
        if self.is_animating:
            self.toggle_animation(None)  # Stop animation
            
    def update_rotation(self, theta):
        """Update rotation angle (for GUI integration)"""
        self.update_plots(theta)
        self.update_angle_display()
        
    def start_animation(self):
        """Start animation (for GUI integration)"""
        self.is_animating = True
        self.animate()
        
    def stop_animation(self):
        """Stop animation (for GUI integration)"""
        self.is_animating = False
        
    def reset(self):
        """Reset to initial state (for GUI integration)"""
        self.theta = 0
        self.update_plots(0)
        self.update_angle_display()
        if self.is_animating:
            self.stop_animation()
        
    def run(self):
        """Run the demonstration"""
        plt.show()

def main():
    """Main function to run the rotation demonstration"""
    print("Rotation Demonstration")
    print("=" * 50)
    print("This demo shows three types of rotations:")
    print("1. 2D Point Rotation - A point rotating around the origin")
    print("2. 2D Vector Rotation - A vector rotating around the origin")
    print("3. 3D Vector Rotation - A vector rotating around the Z-axis")
    print("\nControls:")
    print("- Use the slider to manually control rotation angle")
    print("- Click 'Play' to start automatic rotation animation")
    print("- Click 'Pause' to stop the animation")
    print("- Click 'Reset' to return to initial position")
    print("\nFeatures:")
    print("- Real-time rotation matrix display")
    print("- Rotation formulas display")
    print("- Trajectory paths showing rotation history")
    print("- Interactive 3D visualization")
    
    demo = RotationDemo()
    demo.run()

if __name__ == "__main__":
    main() 