#!/usr/bin/env python3
#http://wiki.ros.org/tf/Tutorials/Writing%20a%20tf%20listener%20%28Python%29

import rospy
#import math
from numpy.linalg import norm
from dynamic_reconfigure.server import Server
from ar_test.cfg import TutorialsConfig
import tf

def callback(config, level):
    rospy.loginfo("""Reconfigure Request: {int_param}, {double_paramr},\ 
          {child_frame_id},{parent_frame_id},{new_frame_id}, {bool_paramx}, {size}""".format(**config))
    # normalize quaternion
    q = [config["double_paramqx"],config["double_paramqy"],config["double_paramqz"],config["double_paramqw"]]
    noo = float(norm(q))
    print(noo)
    #raise()
    config["double_paramqx"] = config["double_paramqx"]/noo 
    config["double_paramqy"] = config["double_paramqy"]/noo 
    config["double_paramqz"] = config["double_paramqz"]/noo 
    config["double_paramqw"] = config["double_paramqw"]/noo 
    
    return config

if __name__ == '__main__':
    try:
        rospy.init_node('pose_publisher_updater')
        srv = Server(TutorialsConfig, callback)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

