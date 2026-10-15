#!/usr/bin/env python3
#http://wiki.ros.org/tf/Tutorials/Writing%20a%20tf%20listener%20%28Python%29

import rospy
import tf
import std_msgs.msg

class Thing:

    def __init__(self):
        pass
    def publisher(self):
        rospy.init_node('pose_publisher', anonymous=True)
        listener = tf.TransformListener()
        rate = rospy.Rate(10) # Hz
        br = tf.TransformBroadcaster()
        q_rot = [0.5,0.5,0.5,0.5]

        while not rospy.is_shutdown():
            
            try:
                (trans,rot) = listener.lookupTransform("map", "ximu3", rospy.Time(0))
            except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                
                continue

            q_new = tf.transformations.quaternion_multiply(rot,q_rot)
            br.sendTransform((0.5, 0.5, 0), (0,0,0,1), rospy.Time.now(), "d_transl", "map")
            br.sendTransform((0, 0, 0), q_new, rospy.Time.now(), "d", "d_transl")

            rate.sleep()

if __name__ == '__main__':
    try:
        a = Thing()
        a.publisher()
    except rospy:
        pass

