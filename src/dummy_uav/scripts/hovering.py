#!/usr/bin/env python3
# filepath: /home/sslab/sim_ws/src/dummy_uav/scripts/hover_oscillate.py

import rospy
import math
from gazebo_msgs.srv import SetModelState
from gazebo_msgs.msg import ModelState
from geometry_msgs.msg import Twist
import threading

class HoverOscillate:
    def __init__(self):
        rospy.init_node('hover_oscillate', anonymous=True)
        
        # Parameters
        self.amplitude = rospy.get_param('~amplitude', 0.8)
        self.frequency = rospy.get_param('~frequency', 1.5)
        self.hover_height = rospy.get_param('~hover_height', 2.0)
        self.model_name = rospy.get_param('~model_name', 'dummy_uav')
        self.noise_amplitude = rospy.get_param('~noise_amplitude', 0.1)
        
        # Hover position (can be changed via cmd_vel)
        self.hover_x = 0.0
        self.hover_y = 0.0
        self.target_hover_x = 0.0
        self.target_hover_y = 0.0
        
        # Movement smoothing
        self.move_speed = 1.0  # m/s
        
        # Services and subscribers
        self.set_model_state = rospy.ServiceProxy('/gazebo/set_model_state', SetModelState)
        self.cmd_vel_sub = rospy.Subscriber('/cmd_vel', Twist, self.cmd_vel_callback)
        
        rospy.wait_for_service('/gazebo/set_model_state')
        
        self.rate = rospy.Rate(30)  # 30 Hz
        self.start_time = rospy.Time.now()
        
        rospy.loginfo(f"Hover Oscillate started - Hover height: {self.hover_height}m")
        rospy.loginfo("Use cmd_vel to move hover position, robot will oscillate around that point")
        
    def cmd_vel_callback(self, msg):
        """Handle cmd_vel messages to change hover position"""
        # Update target hover position based on cmd_vel
        self.target_hover_x += msg.linear.x * 0.1  # Scale down the movement
        self.target_hover_y += msg.linear.y * 0.1
        
        # Update hover height with up/down commands
        if msg.linear.z > 0:
            self.hover_height += 0.05
        elif msg.linear.z < 0:
            self.hover_height = max(0.5, self.hover_height - 0.05)  # Don't go too low
            
        rospy.loginfo_throttle(1.0, f"Target hover: [{self.target_hover_x:.2f}, {self.target_hover_y:.2f}, {self.hover_height:.2f}]")
        
    def get_oscillating_position(self, current_time):
        """Calculate oscillating position around hover point"""
        import random
        
        dt = (current_time - self.start_time).to_sec()
        omega = 2 * math.pi * self.frequency
        
        # Smooth movement toward target hover position
        hover_diff_x = self.target_hover_x - self.hover_x
        hover_diff_y = self.target_hover_y - self.hover_y
        max_step = self.move_speed / 30.0  # 30 Hz rate
        
        if abs(hover_diff_x) > max_step:
            self.hover_x += max_step if hover_diff_x > 0 else -max_step
        else:
            self.hover_x = self.target_hover_x
            
        if abs(hover_diff_y) > max_step:
            self.hover_y += max_step if hover_diff_y > 0 else -max_step
        else:
            self.hover_y = self.target_hover_y
        
        # Primary vertical oscillation
        z_oscillation = self.amplitude * math.sin(omega * dt)
        z_vel = self.amplitude * omega * math.cos(omega * dt)
        
        # Add some noise for rough movement
        noise_x = random.uniform(-self.noise_amplitude, self.noise_amplitude)
        noise_y = random.uniform(-self.noise_amplitude, self.noise_amplitude)
        noise_z = random.uniform(-self.noise_amplitude * 0.3, self.noise_amplitude * 0.3)
        
        # Add slight oscillations around hover point
        x_wiggle = 0.1 * math.sin(omega * dt * 2)  # Small horizontal wiggle
        y_wiggle = 0.05 * math.cos(omega * dt * 1.5)
        
        # Final position
        x_pos = self.hover_x + x_wiggle + noise_x
        y_pos = self.hover_y + y_wiggle + noise_y
        z_pos = self.hover_height + z_oscillation + noise_z
        
        return x_pos, y_pos, z_pos, z_vel
        
    def run(self):
        """Main control loop"""
        while not rospy.is_shutdown():
            current_time = rospy.Time.now()
            
            # Get oscillating position
            x_pos, y_pos, z_pos, z_vel = self.get_oscillating_position(current_time)
            
            # Create model state
            model_state = ModelState()
            model_state.model_name = self.model_name
            
            # Set position
            model_state.pose.position.x = x_pos
            model_state.pose.position.y = y_pos
            model_state.pose.position.z = z_pos
            model_state.pose.orientation.w = 1.0
            model_state.pose.orientation.x = 0.0
            model_state.pose.orientation.y = 0.0
            model_state.pose.orientation.z = 0.0
            
            # Set velocity for realistic IMU readings
            model_state.twist.linear.x = 0.0
            model_state.twist.linear.y = 0.0
            model_state.twist.linear.z = z_vel
            model_state.twist.angular.x = 0.0
            model_state.twist.angular.y = 0.0
            model_state.twist.angular.z = 0.0
            
            # Update robot position
            try:
                self.set_model_state(model_state)
            except rospy.ServiceException as e:
                rospy.logwarn_throttle(5.0, f"Failed to set model state: {e}")
            
            self.rate.sleep()

if __name__ == '__main__':
    try:
        controller = HoverOscillate()
        controller.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("Hover oscillation stopped")