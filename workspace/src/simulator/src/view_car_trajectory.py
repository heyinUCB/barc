#!/usr/bin/env python

# ---------------------------------------------------------------------------
# Licensing Information: You are free to use or extend these projects for
# education or reserach purposes provided that (1) you retain this notice
# and (2) you provide clear attribution to UC Berkeley, including a link
# to http://barc-project.com
#
# Author: J. Noonan
# Email: jpnoonan@berkeley.edu
#
# This code provides a way to see the car's trajectory, orientation, and velocity profile in 
# real time with referenced to the track defined a priori.
#
# ---------------------------------------------------------------------------

import rospy
from barc.msg import ECU
from sensor_msgs.msg import Imu
from std_msgs.msg import Header
from numpy import eye, array, zeros, diag, unwrap, tan, cos, sin, vstack, linalg, append, ones, polyval, delete, size, empty, linspace
from numpy import ones, polyval, delete, size
from tf import transformations
import math
import matplotlib.pyplot as plt
import numpy as np
import pylab

global pos_info_x_vals, pos_info_y_vals
global v_vals, t_vals, psi_vals

from simulator.msg import Z_DynBkMdl 

pos_info_x_vals = []
pos_info_y_vals = []

v_vals = []
t_vals = []
psi_curr = 0.0

def measurements_callback(data):
    global pos_info_x_vals, pos_info_y_vals
    global v_vals, t_vals, psi_curr
    
    pos_info_x_vals.append(data.x)
    pos_info_y_vals.append(data.y)

    v_vals.append(data.v_x)
    t_vals.append(rospy.get_rostime().to_sec())
    psi_curr = data.psi

def show():
    plt.show()

def view_trajectory():
    global pos_info_x_vals, pos_info_y_vals
    global v_vals, t_vals, psi_curr

    rospy.init_node("car_view_trajectory_node", anonymous=True)
    rospy.on_shutdown(show)

    rospy.Subscriber('z_vhcl', Z_DynBkMdl, measurements_callback)

    fig = pylab.figure()
    pylab.ion()

    vmax_ref = 1.0

    loop_rate = 50
    rate = rospy.Rate(loop_rate)

    car_dx = 0.306
    car_dy = 0.177

    car_xs_origin = [car_dx, car_dx, -car_dx, -car_dx, car_dx]
    car_ys_origin = [car_dy, -car_dy, -car_dy, car_dy, car_dy]

    car_frame = np.vstack((np.array(car_xs_origin), np.array(car_ys_origin)))
    while not rospy.is_shutdown():
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)
        ax1.grid('on')
        ax1.axis('equal')
        
       
        if (pos_info_x_vals and pos_info_y_vals):
            ax1.plot(pos_info_x_vals[:len(pos_info_x_vals)-1], pos_info_y_vals[:len(pos_info_y_vals)-1], 'g-', label="Car path")
            
            x = pos_info_x_vals[len(pos_info_x_vals)-1]
            y = pos_info_y_vals[len(pos_info_y_vals)-1]
            # ax1.plot(x, y, 'gs', label="Car current pos")

            R = np.matrix([[np.cos(psi_curr), -np.sin(psi_curr)], [np.sin(psi_curr), np.cos(psi_curr)]])

            rotated_car_frame = R * car_frame

            car_xs = np.array(rotated_car_frame[0,:])[0]
            car_ys = np.array(rotated_car_frame[1,:])[0]

            front_car_segment_x = np.array([car_xs[0], car_xs[1]]) + x
            front_car_segment_y = np.array([car_ys[0], car_ys[1]]) + y

            ax1.plot(car_xs[1:] + x, car_ys[1:] + y, 'k-')
            ax1.plot(front_car_segment_x, front_car_segment_y, 'y-')
            #plt.plot(np.array(car_xs_origin) + x, np.array(car_ys_origin) + y, 'k-')

        if (v_vals):
            t_vals_zeroed = [t - t_vals[0] for t in t_vals]
            ax2.plot(t_vals_zeroed, v_vals, 'm-')
            ax2.set_ylim([min(0, min(v_vals)), max(vmax_ref, max(v_vals))])


        ax1.set_title("Green = Data from POS_INFO")

        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Velocity (m/s)")

        pylab.pause(0.001)
        pylab.gcf().clear()

    

if __name__ == '__main__':
    try:
        view_trajectory()
    except rospy.ROSInterruptException:
        pass
