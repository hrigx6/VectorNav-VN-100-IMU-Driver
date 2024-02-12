#!/usr/bin/env python3

import rospy
from rospy import Time
import serial
from imu_driver.msg import imu_msg
from imu_driver.msg import *
import sys
import math

port = sys.argv[1]

print("DRIVER STARTED")
pub = rospy.Publisher('imu', imu_msg, queue_size=10)
rospy.init_node('imu_driver', anonymous=True)
serial_port = rospy.get_param('~port',port)
serial_baud = rospy.get_param('~baudrate',115200)
# rate = rospy.Rate(1)
imu_msg = imu_msg()
port = serial.Serial(serial_port,serial_baud)
imu_msg.Header.seq = 0
imu_msg.Header.frame_id = "IMS1_Frame" 


def driver():
    
    while not rospy.is_shutdown():
        try:
            line = port.readline()
            print(str(line))
            if "$VNYMR" in str(line):
                try:
                    data = str(line).split(',')
                    print(data)


                    time=rospy.get_rostime()
                    imu_msg.Header.stamp.secs=time.secs 
                    imu_msg.Header.stamp.nsecs=time.nsecs


                    yaw = float(data[1])
                    pitch = float(data[2])
                    roll = float(data[3])
                    magX = float(data[4])
                    magY = float(data[5])
                    magZ = float(data[6])
                    accX = float(data[7])
                    accY = float(data[8])
                    accZ = float(data[9])
                    gyroX = float(data[10])
                    gyroY = float(data[11])
                    gyroZ = float(data[12][0:9])

                    cy = math.cos(yaw/2)
                    sy = math.sin(yaw/2)
                    cp = math.cos(pitch/2)
                    sp = math.sin(pitch/2)
                    cr = math.cos(roll/2)
                    sr = math.sin(roll/2)

                    q_w = cy * cp * cr + sy * sp * sr
                    q_x = cy * cp * sr - sy * sp * cr
                    q_y = sy * cp * sr + cy * sp * cr
                    q_z = sy * cp * cr - cy * sp * sr


                    imu_msg.IMU.orientation.w = q_w
                    imu_msg.IMU.orientation.x = q_x
                    imu_msg.IMU.orientation.y = q_y
                    imu_msg.IMU.orientation.z = q_z

                    imu_msg.IMU.linear_acceleration.x = accX
                    imu_msg.IMU.linear_acceleration.y = accY
                    imu_msg.IMU.linear_acceleration.z = accZ
                    imu_msg.IMU.angular_velocity.x = gyroX
                    imu_msg.IMU.angular_velocity.y = gyroY
                    imu_msg.IMU.angular_velocity.z = gyroZ
                    imu_msg.MagField.magnetic_field.x = magX
                    imu_msg.MagField.magnetic_field.y = magY
                    imu_msg.MagField.magnetic_field.z = magZ

                    imu_msg.Header.seq+=1
                    pub.publish(imu_msg)

                    
                except Exception as e:
                    print(e)
        except rospy.ROSInterruptException:
                port.close()

if __name__ == '__main__':
    try:
        driver()
    except rospy.ROSInterruptException:
        pass
