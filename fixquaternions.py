#!/usr/bin/env python3
#http://wiki.ros.org/tf/Tutorials/Writing%20a%20tf%20listener%20%28Python%29

import rospy
import tf
import std_msgs.msg
#import tf_transformations

from dynamic_reconfigure.client import Client
from ar_test.cfg import TutorialsConfig


class Thing:

    def __init__(self):
        self.r = 0 
        self.p = 0
        self.y = 0
        self.qx = 0
        self.qy = 0
        self.qz = 0
        self.qw = 1
        self.ix = False
        self.iy = False
        self.iz = False
        self.child_frame_id = "ximu3"
        self.new_frame_id = "frame_1"
        self.parent_frame_id = "map"
        self.use_quaternions = False
    def callback(self, config):
        rospy.loginfo("""Reconfigure Request: {int_param}, {double_paramr},\ 
              {child_frame_id},{parent_frame_id},{new_frame_id}, {bool_paramx}, {size}""".format(**config))
        
        self.r = config["double_paramr"]
        self.p = config["double_paramp"]
        self.y = config["double_paramy"]
       
        self.qx = config["double_paramqx"]
        self.qy = config["double_paramqy"]
        self.qz = config["double_paramqz"]
        self.qw = config["double_paramqw"]
       
        self.parent_frame_id = config["parent_frame_id"]
        self.child_frame_id = config["child_frame_id"]
        self.new_frame_id = config["new_frame_id"]

        if self.child_frame_id == self.new_frame_id:
                rospy.logerr_throttle(3,"New frame id cannot be the same as old frame_id. Tfs will collide!!")
        self.ix = config["bool_paramx"]
        self.iy = config["bool_paramy"]
        self.iz = config["bool_paramz"]
       
        self.use_quaternions = config["use_q"]
        return config

    def publisher(self):

        
        #pub = rospy.Publisher('pose', PoseStamped, queue_size=1)
        rospy.init_node('pose_publisher', anonymous=True)
        listener = tf.TransformListener()
        rate = rospy.Rate(10) # Hz
        h = std_msgs.msg.Header()
        h.frame_id = self.parent_frame_id
        br = tf.TransformBroadcaster()

        cl = Client("pose_publisher_updater", 30, self.callback)

        while not rospy.is_shutdown():
            if self.use_quaternions:
                q_rot = [self.qx,self.qy,self.qz,self.qw]
            else:
                q_rot = tf.transformations.quaternion_from_euler(self.r, self.p, self.y);
            
            try:
            #if (True):
                #(trans,rot) = listener.lookupTransform(self.child_frame_id, self.parent_frame_id, rospy.Time(0))
                (trans,rot) = listener.lookupTransform(self.parent_frame_id, self.child_frame_id, rospy.Time(0))
            except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                
                continue

            #print(self.r,self.p,self.y)
            #print(rot)
                         #tf.transformations.quaternion_from_euler(0, 0, msg.theta),
            #newrot = tf.transformations.quaternion_inverse(rot)
            newrot = rot
            q_roti = tf.transformations.quaternion_inverse(q_rot)
            newrot[0] = -rot[0] if self.ix else rot[0]
            newrot[1] = -rot[1] if self.iy else rot[1]
            newrot[2] = -rot[2] if self.iz else rot[2]

            q_new = tf.transformations.quaternion_multiply(rot,q_rot)
            #q_new = rot
            #q_new = [-rot[0],-rot[1],-rot[2],rot[3], ]
            #print(q_new)
            #br.sendTransform((0.5, 0.5, 0), q_new, rospy.Time.now(), self.parent_frame_id, self.new_frame_id)
            br.sendTransform((0.5, 0.5, 0), (0,0,0,1), rospy.Time.now(), self.new_frame_id+"_transl", self.parent_frame_id)
            br.sendTransform((0, 0, 0), q_new, rospy.Time.now(), self.new_frame_id, self.new_frame_id+"_transl")

            rate.sleep()

if __name__ == '__main__':
    try:
        a = Thing()
        a.publisher()
    except rospy:
        pass

