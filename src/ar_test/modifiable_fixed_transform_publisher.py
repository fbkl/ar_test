#!/usr/bin/env python3
#http://wiki.ros.org/tf/Tutorials/Writing%20a%20tf%20listener%20%28Python%29

### from https://raw.githubusercontent.com/ros-visualization/visualization_tutorials/refs/heads/indigo-devel/interactive_marker_tutorials/scripts/basic_controls.py

import rospy
import tf
import std_msgs.msg
#import tf_transformations
import sys

from dynamic_reconfigure.client import Client
from dynamic_reconfigure.server import Server
from ar_test.cfg import CompleteTFConfig

from interactive_markers.interactive_marker_server import *
from interactive_markers.menu_handler import *
from visualization_msgs.msg import *
from geometry_msgs.msg import Point
from random import random

def getPoseAsTuples(pose):
    orientation = [0,0,0,0]
    position = [0,0,0]
    orientation[0] = pose.orientation.x
    orientation[1] = pose.orientation.y
    orientation[2] = pose.orientation.z
    orientation[3] = pose.orientation.w

    position[0] = pose.position.x
    position[1] = pose.position.y
    position[2] = pose.position.z
    return position, orientation


def makeBox( msg ):
    marker = Marker()

    marker.type = Marker.CUBE
    marker.scale.x = msg.scale * 0.45
    marker.scale.y = msg.scale * 0.45
    marker.scale.z = msg.scale * 0.45
    marker.color.r = random()
    marker.color.g = random()
    marker.color.b = random()
    marker.color.a = 1.0

    return marker


def makeBoxControl( msg ):
    control =  InteractiveMarkerControl()
    control.always_visible = True
    control.markers.append( makeBox(msg) )
    msg.controls.append( control )
    return control
import math

def normalizeTuple(t):
    norm = math.sqrt(t[0]*t[0]+ t[1]*t[1]+ t[2]*t[2]+ t[3]*t[3])
    return t[0]/norm, t[1]/norm, t[2]/norm, t[3]/norm,

def normalizeGeoQ(q):
    qq = geometry_msgs.msg.Quaternion()
    qq.x,qq.y,qq.z,qq.w = normalizeTuple((q.x,q.y,q.z,q.w))
    return qq

class ModifiableFixedTransformPublisher:
    """
    This is the fixquaternions node, but modified to what I think it is its true purpose:
    To add a transform that you can tweak and check in rviz if it looks correct or not before you create a static transform publisher for it.
    """
    def __init__(self):
        self.ar = 0 
        self.ap = 0
        self.ay = 0
        self.qx = 0
        self.qy = 0
        self.qz = 0
        self.qw = 1
        self.x = 0
        self.y = 0
        self.z = 0
        self.child_frame_id = "a_new_coordinate_frame"
        self.parent_frame_id = "map"
        self.use_quaternions = False
        self.rate = 10
        self.br =  tf.TransformBroadcaster()

        self.marker=None

        ## we arent really using this, but for future
        self.menu_handler = MenuHandler() 
        self.menu_handler.insert( "First Entry", callback=self.processFeedback )
        self.menu_handler.insert( "Second Entry", callback=self.processFeedback )
        sub_menu_handle = self.menu_handler.insert( "Submenu" )
        self.menu_handler.insert( "First Entry", parent=sub_menu_handle, callback=self.processFeedback )
        self.menu_handler.insert( "Second Entry", parent=sub_menu_handle, callback=self.processFeedback )

    def processFeedback(self, feedback ):
        rospy.logdebug("processFeedback:" +self.child_frame_id)

        config = CompleteTFConfig.defaults

        ##update the config from my internal state:
        config["parent_frame_id"] = self.parent_frame_id
        config["child_frame_id"] = self.child_frame_id
        self.use_quaternions = True
        config["use_q"] = self.use_quaternions

        #rospy.logwarn(config)
        config["x"] =  feedback.pose.position.x
        config["y"] =  feedback.pose.position.y
        config["z"] =  feedback.pose.position.z
        config["double_paramqx"] = feedback.pose.orientation.x
        config["double_paramqy"] = feedback.pose.orientation.y
        config["double_paramqz"] = feedback.pose.orientation.z
        config["double_paramqw"] = feedback.pose.orientation.w
        
        ##euler angles idk
        #rospy.logwarn("I don't exactly know what to do with RPY angles, so maybe I will mess it up")
 
        config["double_paramr"],config["double_paramp"],config["double_paramy"]  = tf.transformations.euler_from_quaternion(
                [feedback.pose.orientation.w,
feedback.pose.orientation.x,
feedback.pose.orientation.y,
feedback.pose.orientation.z, ])

        self.cl.update_configuration(config)

        #(self.x,self.y,self.z), (self.qx,self.qy,self.qz,self.qw,) = *getPoseAsTuples(feedback.pose)
        #self.br.sendTransform( *getPoseAsTuples(feedback.pose), rospy.Time.now(), "moving_frame", "base_link" )
        self.server.applyChanges()
  
    def make6DofMarker(self, interaction_mode, position, show_6dof = False):
        int_marker = InteractiveMarker()
        int_marker.header.frame_id = self.parent_frame_id
        int_marker.pose.position = position
        int_marker.scale = 0.3

        int_marker.name = "simple_6dof"
        int_marker.description = "Simple 6-DOF Control"

        # insert a box
        makeBoxControl(int_marker)
        int_marker.controls[0].interaction_mode = interaction_mode

        if interaction_mode != InteractiveMarkerControl.NONE:
            control_modes_dict = { 
                              InteractiveMarkerControl.MOVE_3D : "MOVE_3D",
                              InteractiveMarkerControl.ROTATE_3D : "ROTATE_3D",
                              InteractiveMarkerControl.MOVE_ROTATE_3D : "MOVE_ROTATE_3D" }
            int_marker.name += "_" + control_modes_dict[interaction_mode]
            int_marker.description = "3D Control"
            int_marker.description += " + 6-DOF controls"
            int_marker.description += "\n" + control_modes_dict[interaction_mode]
        

        int_marker.description = rospy.get_param("~marker_description", int_marker.description)

        control = InteractiveMarkerControl()
        control.orientation.w = 1
        control.orientation.x = 1
        control.orientation.y = 0
        control.orientation.z = 0
        #control.orientation = normalizeGeoQ(control.orientation)
        control.name = "rotate_x"
        control.interaction_mode = InteractiveMarkerControl.ROTATE_AXIS
        int_marker.controls.append(control)

        control = InteractiveMarkerControl()
        control.orientation.w = 1
        control.orientation.x = 1
        control.orientation.y = 0
        control.orientation.z = 0
        #control.orientation = normalizeGeoQ(control.orientation)
        control.name = "move_x"
        control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        int_marker.controls.append(control)

        control = InteractiveMarkerControl()
        control.orientation.w = 1
        control.orientation.x = 0
        control.orientation.y = 1
        control.orientation.z = 0
        #control.orientation = normalizeGeoQ(control.orientation)
        control.name = "rotate_z"
        control.interaction_mode = InteractiveMarkerControl.ROTATE_AXIS
        int_marker.controls.append(control)

        control = InteractiveMarkerControl()
        control.orientation.w = 1
        control.orientation.x = 0
        control.orientation.y = 1
        control.orientation.z = 0
        #control.orientation = normalizeGeoQ(control.orientation)
        control.name = "move_z"
        control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        int_marker.controls.append(control)

        control = InteractiveMarkerControl()
        control.orientation.w = 1
        control.orientation.x = 0
        control.orientation.y = 0
        control.orientation.z = 1
        #control.orientation = normalizeGeoQ(control.orientation)
        control.name = "rotate_y"
        control.interaction_mode = InteractiveMarkerControl.ROTATE_AXIS
        int_marker.controls.append(control)

        control = InteractiveMarkerControl()
        control.orientation.w = 1
        control.orientation.x = 0
        control.orientation.y = 0
        control.orientation.z = 1
        #control.orientation = normalizeGeoQ(control.orientation)
        control.name = "move_y"
        control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        int_marker.controls.append(control)

        self.server.insert(int_marker, self.processFeedback)
        self.menu_handler.apply( self.server, int_marker.name )

        return int_marker.name

    def client_callback(self,config):
        return self.callback(config, 1)
         
    def callback(self, config, level):
        rospy.loginfo("""Reconfigure Request: 
              {child_frame_id},{parent_frame_id},
        {double_paramr},\ 
        {double_paramp},\ 
        {double_paramy},\ 
        {use_q},\
        {double_paramqx},\ 
        {double_paramqy},\ 
        {double_paramqz},\ 
        {double_paramqw},\ 
        {x},\ 
        {y},\ 
        {z},\ 
""".format(**config))
        
        rospy.logdebug("server_callback" +self.child_frame_id)

        self.ar = config["double_paramr"]
        self.ap = config["double_paramp"]
        self.ay = config["double_paramy"]
       
        self.qx = config["double_paramqx"]
        self.qy = config["double_paramqy"]
        self.qz = config["double_paramqz"]
        self.qw = config["double_paramqw"]
       
        self.parent_frame_id = config["parent_frame_id"]
        self.child_frame_id = config["child_frame_id"]

        if self.child_frame_id == self.parent_frame_id:
                rospy.logerr_throttle(3,"New frame id cannot be the same as old frame_id. Tfs will collide!!")
       
        self.use_quaternions = config["use_q"]
        
        self.x = config["x"]
        self.y = config["y"]
        self.z = config["z"]
        if self.use_quaternions:
            q_rot = [self.qx,self.qy,self.qz,self.qw]
            q_rot = normalizeTuple(q_rot)
        else:
            q_rot = tf.transformations.quaternion_from_euler(self.ar, self.ap, self.ay);
        ##update the parameter server
        config["double_paramqx"] = float(q_rot[0])
        config["double_paramqy"] = float(q_rot[1])
        config["double_paramqz"] = float(q_rot[2])
        config["double_paramqw"] = float(q_rot[3])

        #update the tf 
        #self.br.sendTransform((self.x, self.y, self.z), q_rot, rospy.Time.now(), self.child_frame_id, self.parent_frame_id)

        #update the marker position
        if self.marker:
            h = std_msgs.msg.Header()
            h.stamp = rospy.Time.now()
            pose = geometry_msgs.msg.Pose()
            h.frame_id = self.parent_frame_id
            pose.position.x = self.x
            pose.position.y = self.y
            pose.position.z = self.z
            
            pose.orientation.x = q_rot[0]
            pose.orientation.y = q_rot[1]
            pose.orientation.z = q_rot[2]
            pose.orientation.w = q_rot[3]
            self.server.doSetPose(None, self.marker, pose, h )

        #update the internal state
        self.qx = q_rot[0]
        self.qy = q_rot[1]
        self.qz = q_rot[2]
        self.qw = q_rot[3]

        rospy.loginfo("running")
        return config

    def publisher(self):

        listener = tf.TransformListener()
        rate = rospy.Rate(self.rate) # Hz

        sv = Server(CompleteTFConfig, self.callback)
        self.cl = Client(rospy.get_name(), 30, self.client_callback)
        self.server = InteractiveMarkerServer(rospy.get_name())
        position = Point( self.x, self.y, self.z)
        self.marker = self.make6DofMarker( InteractiveMarkerControl.MOVE_ROTATE_3D, position, True )
        #rospy.spin()
        while not rospy.is_shutdown():
            if self.use_quaternions:
                q_rot = [self.qx,self.qy,self.qz,self.qw]
                q_rot = normalizeTuple(q_rot)
            else:
                q_rot = tf.transformations.quaternion_from_euler(self.ar, self.ap, self.ay);

            self.br.sendTransform((self.x, self.y, self.z), q_rot, rospy.Time.now(), self.child_frame_id, self.parent_frame_id)
            rospy.logdebug("loop:"+self.child_frame_id)

            #rospy.logwarn("running")
            self.server.applyChanges()
    
            rate.sleep()


def strip_argv(argv):
    """Removes ros arguments that start with __"""
    stripped = []
    for arg in argv:
        if "__" == arg[:2]:
            continue
        stripped.append(arg)
    return stripped
if __name__ == '__main__':
    #   try:
        a = ModifiableFixedTransformPublisher()

        rospy.init_node('new_coordinate_frame_publisher', anonymous=True)

        my_args = strip_argv(sys.argv)

        rospy.logwarn("This node can substitute either a tf or a tf2_ros static publisher, but they differ in the number of arguments. Please make sure which one you are using!")
        has_rate = False
        if rospy.get_param("has_rate", default=False) or type(my_args[-1]) == type(""):
            rpy_len = 9
            q_len = 10
        else:
            has_rate = True
            rpy_len = 10
            q_len = 11



        if len(my_args) <= 1:
            print("No arguments were given")
        else:
            rospy.logwarn(my_args)
            rospy.logwarn("arguments overwrite rosparams!")
            rospy.set_param("~x", float(my_args[1]))
            rospy.set_param("~y", float(my_args[2]))
            rospy.set_param("~z", float(my_args[3]))
            if len(my_args) == rpy_len: ## rpy angles
                rospy.logwarn("the order of the angles is inverted in this guy because it is also inverted in tf static_transform_publisher")
                rospy.set_param("~double_paramy", float(my_args[4]))
                rospy.set_param("~double_paramp", float(my_args[5]))
                rospy.set_param("~double_paramr", float(my_args[6]))
                rospy.set_param("~parent_frame_id", my_args[7])
                rospy.set_param("~child_frame_id", my_args[8])
                if has_rate:
                    rospy.set_param("~rate", float(my_args[9]))
                rospy.set_param("~use_q", False)

            if len(my_args) == q_len: ## quaternions
                rospy.logerr("ATTENTION, I HAVEN'T CHECKED THIS, IDK IF IT IS CORRECT!")
                rospy.set_param("~double_paramqx", float(my_args[4]))
                rospy.set_param("~double_paramqy", float(my_args[5]))
                rospy.set_param("~double_paramqz", float(my_args[6]))
                rospy.set_param("~double_paramqw", float(my_args[7]))
                rospy.set_param("~parent_frame_id", my_args[8])
                rospy.set_param("~child_frame_id", my_args[9])
                if has_rate:    
                    rospy.set_param("~rate", float(my_args[10]))
                rospy.set_param("~use_q", True)

        a.publisher()
#    except :
#        pass

