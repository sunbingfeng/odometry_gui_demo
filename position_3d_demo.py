#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from mpl_toolkits.mplot3d import Axes3D
import math

class Position3DDemo:
    def __init__(self, fig=None):
        if fig is None:
            self.fig = plt.figure(figsize=(16, 12))
        else:
            self.fig = fig
        self.setup_plots()
        self.setup_animation()
        self.setup_controls()
        
    def setup_plots(self):
        """Setup the subplots for 3D position demonstration"""
        # Main 3D coordinate system (larger, takes more space)
        self.ax1 = self.fig.add_subplot(1, 3, (1, 2), projection='3d')
        self.ax1.set_xlim(-3, 3)
        self.ax1.set_ylim(-3, 3)
        self.ax1.set_zlim(-3, 3)
        self.ax1.set_title('3D Coordinate System & Position Vector', fontsize=14, fontweight='bold')
        self.ax1.set_xlabel('X')
        self.ax1.set_ylabel('Y')
        self.ax1.set_zlabel('Z')
        
        # Vector magnitude and direction
        self.ax2 = self.fig.add_subplot(1, 3, 3)
        self.ax2.axis('off')
        self.ax2.set_title('Vector Properties', fontsize=12, fontweight='bold')
        
        # plt.tight_layout()  # Removed to avoid 3D axes compatibility warning
        
    def setup_animation(self):
        """Initialize animation elements"""
        # Initial position vector
        self.position = np.array([1.5, 1.0, 0.8])
        self.original_position = self.position.copy()
        
        # Animation state
        self.is_animating = False
        self.animation_speed = 0.02
        self.rotation_angle = 0.0
        
        # Coordinate system properties
        self.show_bases = True
        self.show_components = True
        self.show_grid = True
        
        # Setup plot elements
        self.setup_3d_coordinate_system()
        self.update_vector_properties()
        
    def setup_3d_coordinate_system(self):
        """Setup the main 3D coordinate system"""
        # Origin point
        self.origin = self.ax1.scatter(0, 0, 0, color='black', s=100, marker='o', label='Origin')
        
        # Coordinate axes
        self.x_axis = self.ax1.quiver(0, 0, 0, 2, 0, 0, color='red', alpha=0.7, 
                                    arrow_length_ratio=0.1, linewidth=2, label='X-axis')
        self.y_axis = self.ax1.quiver(0, 0, 0, 0, 2, 0, color='green', alpha=0.7, 
                                    arrow_length_ratio=0.1, linewidth=2, label='Y-axis')
        self.z_axis = self.ax1.quiver(0, 0, 0, 0, 0, 2, color='blue', alpha=0.7, 
                                    arrow_length_ratio=0.1, linewidth=2, label='Z-axis')
        
        # Position vector
        self.position_vector = self.ax1.quiver(0, 0, 0, 0, 0, 0, color='purple', alpha=0.8, 
                                             arrow_length_ratio=0.15, linewidth=3, label='Position Vector')
        
        # Position point
        self.position_point = self.ax1.scatter(0, 0, 0, color='purple', s=150, marker='o', 
                                             label='Position Point')
        
        # Component vectors
        self.x_component = self.ax1.quiver(0, 0, 0, 0, 0, 0, color='red', alpha=0.5, 
                                         arrow_length_ratio=0.1, linewidth=1, linestyle='--')
        self.y_component = self.ax1.quiver(0, 0, 0, 0, 0, 0, color='green', alpha=0.5, 
                                         arrow_length_ratio=0.1, linewidth=1, linestyle='--')
        self.z_component = self.ax1.quiver(0, 0, 0, 0, 0, 0, color='blue', alpha=0.5, 
                                         arrow_length_ratio=0.1, linewidth=1, linestyle='--')
        
        # Grid lines
        self.setup_grid_lines()
        
        self.ax1.legend()
        
    def setup_grid_lines(self):
        """Setup grid lines for the coordinate system"""
        # Create grid points
        x_grid = np.linspace(-2, 2, 5)
        y_grid = np.linspace(-2, 2, 5)
        z_grid = np.linspace(-2, 2, 5)
        
        # X-direction grid lines
        for y in y_grid:
            for z in z_grid:
                self.ax1.plot([-2, 2], [y, y], [z, z], 'k-', alpha=0.1, linewidth=0.5)
        
        # Y-direction grid lines
        for x in x_grid:
            for z in z_grid:
                self.ax1.plot([x, x], [-2, 2], [z, z], 'k-', alpha=0.1, linewidth=0.5)
        
        # Z-direction grid lines
        for x in x_grid:
            for y in y_grid:
                self.ax1.plot([x, x], [y, y], [-2, 2], 'k-', alpha=0.1, linewidth=0.5)
        
        
        
    def update_plots(self, position):
        """Update all plots with new position"""
        self.position = position
        
        # Update main 3D plot
        self.update_3d_plot()
        
        # Update vector properties
        self.update_vector_properties()
        
    def update_3d_plot(self):
        """Update the main 3D coordinate system plot"""
        # Update position vector
        if hasattr(self, 'position_vector') and self.position_vector:
            self.position_vector.remove()
        self.position_vector = self.ax1.quiver(0, 0, 0, self.position[0], self.position[1], self.position[2], 
                                             color='purple', alpha=0.8, arrow_length_ratio=0.15, linewidth=3)
        
        # Update position point
        if hasattr(self, 'position_point') and self.position_point:
            self.position_point.remove()
        self.position_point = self.ax1.scatter(self.position[0], self.position[1], self.position[2], 
                                             color='purple', s=150, marker='o')
        
        # Update component vectors
        if hasattr(self, 'x_component') and self.x_component:
            self.x_component.remove()
        if hasattr(self, 'y_component') and self.y_component:
            self.y_component.remove()
        if hasattr(self, 'z_component') and self.z_component:
            self.z_component.remove()
        
        self.x_component = self.ax1.quiver(0, 0, 0, self.position[0], 0, 0, color='red', alpha=0.5, 
                                         arrow_length_ratio=0.1, linewidth=1, linestyle='--')
        self.y_component = self.ax1.quiver(self.position[0], 0, 0, 0, self.position[1], 0, color='green', alpha=0.5, 
                                         arrow_length_ratio=0.1, linewidth=1, linestyle='--')
        self.z_component = self.ax1.quiver(self.position[0], self.position[1], 0, 0, 0, self.position[2], color='blue', alpha=0.5, 
                                         arrow_length_ratio=0.1, linewidth=1, linestyle='--')
        
    def update_vector_properties(self):
        """Update vector properties display"""
        self.ax2.clear()
        self.ax2.axis('off')
        self.ax2.set_title('Vector Properties', fontsize=12, fontweight='bold')
        
        # Calculate vector properties
        magnitude = np.linalg.norm(self.position)
        unit_vector = self.position / magnitude if magnitude > 0 else np.zeros(3)
        
        # Calculate angles
        angle_xy = np.arctan2(self.position[1], self.position[0])  # Angle in XY plane
        angle_xz = np.arctan2(self.position[2], self.position[0])  # Angle in XZ plane
        angle_yz = np.arctan2(self.position[2], self.position[1])  # Angle in YZ plane
        
        # Display properties
        properties_text = f"Current Position:\n"
        properties_text += f"r = ({self.position[0]:.2f}, {self.position[1]:.2f}, {self.position[2]:.2f})\n\n"
        properties_text += f"Vector Properties:\n"
        properties_text += f"Magnitude: |r| = {magnitude:.3f}\n\n"
        properties_text += f"Unit Vector: r̂ = ({unit_vector[0]:.3f}, {unit_vector[1]:.3f}, {unit_vector[2]:.3f})\n\n"
        properties_text += f"Components:\n"
        properties_text += f"  X: {self.position[0]:.3f}\n"
        properties_text += f"  Y: {self.position[1]:.3f}\n"
        properties_text += f"  Z: {self.position[2]:.3f}\n\n"
        properties_text += f"Angles:\n"
        properties_text += f"  XY-plane: {np.degrees(angle_xy):.1f}°\n"
        properties_text += f"  XZ-plane: {np.degrees(angle_xz):.1f}°\n"
        properties_text += f"  YZ-plane: {np.degrees(angle_yz):.1f}°"
        
        self.ax2.text(0.05, 0.95, properties_text, transform=self.ax2.transAxes, 
                     fontsize=10, verticalalignment='top', fontfamily='monospace')
        
    def setup_controls(self):
        """Setup interactive controls"""
        # Add space for controls
        plt.subplots_adjust(bottom=0.15)
        
        # X coordinate slider
        ax_x_slider = plt.axes([0.2, 0.08, 0.6, 0.02])
        self.x_slider = Slider(
            ax_x_slider, 'X', -3, 3, valinit=self.position[0],
            valstep=0.1, color='red'
        )
        self.x_slider.on_changed(self.on_x_change)
        
        # Y coordinate slider
        ax_y_slider = plt.axes([0.2, 0.05, 0.6, 0.02])
        self.y_slider = Slider(
            ax_y_slider, 'Y', -3, 3, valinit=self.position[1],
            valstep=0.1, color='green'
        )
        self.y_slider.on_changed(self.on_y_change)
        
        # Z coordinate slider
        ax_z_slider = plt.axes([0.2, 0.02, 0.6, 0.02])
        self.z_slider = Slider(
            ax_z_slider, 'Z', -3, 3, valinit=self.position[2],
            valstep=0.1, color='blue'
        )
        self.z_slider.on_changed(self.on_z_change)
        
        # Animation controls
        ax_play = plt.axes([0.85, 0.08, 0.1, 0.02])
        self.play_button = Button(ax_play, 'Animate', color='lightgreen')
        self.play_button.on_clicked(self.toggle_animation)
        
        ax_reset = plt.axes([0.85, 0.05, 0.1, 0.02])
        self.reset_button = Button(ax_reset, 'Reset', color='lightcoral')
        self.reset_button.on_clicked(self.reset_position)
        
        # Display current position
        # Note: Removed the controls panel display since we removed ax5
        # The position is now shown in the vector properties panel
        
    def on_x_change(self, val):
        """Handle X coordinate change"""
        self.position[0] = val
        self.update_plots(self.position)
        self.update_position_display()
        
    def on_y_change(self, val):
        """Handle Y coordinate change"""
        self.position[1] = val
        self.update_plots(self.position)
        self.update_position_display()
        
    def on_z_change(self, val):
        """Handle Z coordinate change"""
        self.position[2] = val
        self.update_plots(self.position)
        self.update_position_display()
        
    def update_position_display(self):
        """Update position display"""
        # Note: Removed the controls panel display since we removed ax5
        # The position is now shown in the vector properties panel
        
    def toggle_animation(self, event):
        """Toggle animation on/off"""
        self.is_animating = not self.is_animating
        if self.is_animating:
            self.play_button.label.set_text('Stop')
            self.play_button.color = 'lightyellow'
            self.animate()
        else:
            self.play_button.label.set_text('Animate')
            self.play_button.color = 'lightgreen'
            
    def animate(self):
        """Animate position vector movement"""
        if not self.is_animating:
            return
            
        # Create a circular motion in XY plane
        t = self.rotation_angle
        radius = 2.0
        height = 1.0 + 0.5 * np.sin(2 * t)
        
        new_position = np.array([
            radius * np.cos(t),
            radius * np.sin(t),
            height
        ])
        
        # Update sliders and position
        self.x_slider.set_val(new_position[0])
        self.y_slider.set_val(new_position[1])
        self.z_slider.set_val(new_position[2])
        
        self.position = new_position
        self.rotation_angle += self.animation_speed
        
        # Update plots
        self.update_plots(self.position)
        self.update_position_display()
        
        # Schedule next frame
        if self.is_animating:
            try:
                if hasattr(self.fig.canvas, 'get_tk_widget'):
                    self.fig.canvas.get_tk_widget().after(50, self.animate)
                else:
                    plt.pause(0.05)
                    if self.is_animating:
                        self.animate()
            except:
                plt.pause(0.05)
                if self.is_animating:
                    self.animate()
            
    def reset_position(self, event):
        """Reset position to original"""
        self.position = self.original_position.copy()
        self.rotation_angle = 0.0
        
        self.x_slider.set_val(self.position[0])
        self.y_slider.set_val(self.position[1])
        self.z_slider.set_val(self.position[2])
        
        self.update_plots(self.position)
        self.update_position_display()
        
        if self.is_animating:
            self.toggle_animation(None)  # Stop animation
            
    def run(self):
        """Run the demonstration"""
        plt.show()

    def update_position(self, x, y, z):
        """Update position (for GUI integration)"""
        position = np.array([x, y, z])
        self.update_plots(position)

def main():
    """Main function to run the 3D position demonstration"""
    print("3D Position Vector Demonstration")
    print("=" * 50)
    print("This demo shows:")
    print("1. 3D Coordinate System - Interactive 3D space with position vector")
    print("2. Vector Properties - Magnitude, unit vector, angles")
    print("\nControls:")
    print("- Use X, Y, Z sliders to manually control position")
    print("- Click 'Animate' to start automatic circular motion")
    print("- Click 'Stop' to stop the animation")
    print("- Click 'Reset' to return to initial position")
    print("\nFeatures:")
    print("- Real-time 3D visualization")
    print("- Vector properties calculation")
    print("- Interactive coordinate system")
    
    demo = Position3DDemo()
    demo.run()

if __name__ == "__main__":
    main() 