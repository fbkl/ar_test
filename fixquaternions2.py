#!/usr/bin/env python3
#http://wiki.ros.org/tf/Tutorials/Writing%20a%20tf%20listener%20%28Python%29

import rospy
import tf
import std_msgs.msg
#import tf_transformations

from dynamic_reconfigure.server import Server
from ar_test.cfg import TutorialsConfig

global r
global p
global y

r = 0
p = 0
y = 0


class Thing:

    def __init__(self):
        self.r = 0 
        self.p = 0
        self.y = 0
        self.ix = False
        self.iy = False
        self.iz = False


    def callback(self, config, level):
        rospy.loginfo("""Reconfigure Request: {int_param}, {double_paramr},\ 
              {str_param}, {bool_paramx}, {size}""".format(**config))
        
        self.r = config["double_paramr"]
        self.p = config["double_paramp"]
        self.y = config["double_paramy"]
        
        self.ix = config["bool_paramx"]
        self.iy = config["bool_paramy"]
        self.iz = config["bool_paramz"]
        
        return config

    def publisher(self):

        
        #pub = rospy.Publisher('pose', PoseStamped, queue_size=1)
        rospy.init_node('pose_publisher', anonymous=True)
        listener = tf.TransformListener()
        rate = rospy.Rate(5) # Hz
        h = std_msgs.msg.Header()
        h.frame_id = 'map'
        br = tf.TransformBroadcaster()

        
        srv = Server(TutorialsConfig, self.callback)

        while not rospy.is_shutdown():
            q_rot = tf.transformations.quaternion_from_euler(self.r, self.p, self.y);
            try:
                (trans,rot) = listener.lookupTransform('/map', '/ar_marker_10', rospy.Time(0))
            except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                continue

            #print(self.r,self.p,self.y)
            #print(rot)
                         #tf.transformations.quaternion_from_euler(0, 0, msg.theta),
            newrot = rot
            newrot[0] = -rot[0] if self.ix else rot[0]
            newrot[1] = -rot[1] if self.iy else rot[1]
            newrot[2] = -rot[2] if self.iz else rot[2]

            q_new = tf.transformations.quaternion_multiply(q_rot, newrot)
            #q_new = [-rot[0],-rot[1],-rot[2],rot[3], ]
            br.sendTransform((0.5, 0.5, 0), q_new, rospy.Time.now(), "corrected", "map")

            rate.sleep()

if __name__ == '__main__':
    try:
        a = Thing()
        a.publisher()
    except rospy:
        pass

