#!/usr/bin/env python
import rospy
from std_msgs.msg import Float32, Bool

def main():
    rospy.init_node('flap_control')

    freq_pub = rospy.Publisher('/flap_frequency', Float32, queue_size=10)
    amp_pub = rospy.Publisher('/flap_amplitude', Float32, queue_size=10)
    oscillation_pub = rospy.Publisher('/flap_oscillation', Bool, queue_size=10)
    z_amp_pub = rospy.Publisher('/z_amplitude', Float32, queue_size=10)
    z_freq_pub = rospy.Publisher('/z_frequency', Float32, queue_size=10)

    rate = rospy.Rate(10)  # 10 Hz

    print("Press 's' to start oscillation, 'x' to stop.")
    print("Press 'f' 'F' to increase/decrease frequency, 'a' 'A' to increase/decrease amplitude.")
    print("Press 'z' 'Z' to increase/decrease Z-axis amplitude, 'v' 'V' to increase/decrease Z-axis frequency.")
    print("Press 'q' to quit.")

    frequency = 3.0
    amplitude = 0.1
    z_amplitude = 0.05
    z_frequency = 1.0
    oscillating = False

    while not rospy.is_shutdown():
        key = input("Enter command: ")
        if key == 's':
            oscillating = True
            oscillation_pub.publish(oscillating)
        elif key == 'x':
            oscillating = False
            oscillation_pub.publish(oscillating)
        elif key == 'f':
            frequency += 0.5
            print(f"Frequency set to {frequency} Hz")
            freq_pub.publish(frequency)
        elif key == 'F':
            frequency -= 0.5
            print(f"Frequency set to {frequency} Hz")
            freq_pub.publish(frequency)            
        elif key == 'a':
            amplitude += 0.02
            print(f"Amplitude set to {amplitude} m")
            amp_pub.publish(amplitude)
        elif key == 'A':
            amplitude -= 0.02
            print(f"Amplitude set to {amplitude} m")
            amp_pub.publish(amplitude)            
        elif key == 'z':
            z_amplitude += 0.01
            print(f"Z-axis amplitude set to {z_amplitude} m")
            z_amp_pub.publish(z_amplitude)
        elif key == 'Z':
            z_amplitude -= 0.01
            print(f"Z-axis amplitude set to {z_amplitude} m")
            z_amp_pub.publish(z_amplitude)
        elif key == 'v':
            z_frequency += 0.2
            print(f"Z-axis frequency set to {z_frequency} Hz")
            z_freq_pub.publish(z_frequency)
        elif key == 'V':
            z_frequency -= 0.2
            print(f"Z-axis frequency set to {z_frequency} Hz")
            z_freq_pub.publish(z_frequency)
        elif key == 'q':
            break
        else:
            print("Unknown command.")
        rate.sleep()

if __name__ == "__main__":
    main()