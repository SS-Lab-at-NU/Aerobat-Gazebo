#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
from gazebo_msgs.msg import ModelState
from gazebo_msgs.srv import SetModelState
import math

class TeleopMover:
    def __init__(self):
        rospy.init_node("cmd_vel_to_pose")
        self.model_name = "dummy_uav"

        # Pose state
        self.x = 0.0
        self.y = 0.0
        self.z = 1.0
        self.yaw = 0.0

        self.rate = rospy.Rate(20)
        self.last_cmd = Twist()

        # Subscribe to cmd_vel
        rospy.Subscriber("/cmd_vel", Twist, self.cmd_callback)

        # Wait for service
        rospy.wait_for_service("/gazebo/set_model_state")
        self.set_state = rospy.ServiceProxy("/gazebo/set_model_state", SetModelState)

        rospy.loginfo("cmd_vel_to_pose node ready.")
        self.run()

    def cmd_callback(self, msg):
        self.last_cmd = msg

    def run(self):
        while not rospy.is_shutdown():
            dt = 1.0 / 20.0

            # Integrate velocity to position
            dx = self.last_cmd.linear.x * math.cos(self.yaw) * dt
            dy = self.last_cmd.linear.x * math.sin(self.yaw) * dt
            dz = self.last_cmd.linear.z * dt
            dyaw = self.last_cmd.angular.z * dt

            self.x += dx
            self.y += dy
            self.z += dz
            self.yaw += dyaw

            # Build pose
            state = ModelState()
            state.model_name = self.model_name
            state.pose.position.x = self.x
            state.pose.position.y = self.y
            state.pose.position.z = self.z

            import tf.transformations as tft
            quat = tft.quaternion_from_euler(0, 0, self.yaw)
            state.pose.orientation.x = quat[0]
            state.pose.orientation.y = quat[1]
            state.pose.orientation.z = quat[2]
            state.pose.orientation.w = quat[3]

            # Send to Gazebo
            try:
                self.set_state(state)
            except rospy.ServiceException as e:
                rospy.logwarn("Failed to set model state: %s", e)

            self.rate.sleep()

if __name__ == "__main__":
    TeleopMover()
