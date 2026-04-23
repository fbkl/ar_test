#!/usr/bin/env python3

import rospy
import tf2_ros
import tf
import std_msgs.msg
#import tf_transformations
import sys
from std_srvs.srv import Empty, EmptyResponse

import tf.transformations as tft

if __name__ == '__main__':

        rospy.init_node('calibration_frame_publisher', anonymous=True)

        """
        map -> fixed_room_marker : there is a fixed transform

        then each camera will have their "map" defined as a {camera_name}_localmap 

        the tf from the camera to this localmap

        
        


        ar_track alvar with publish the tf from the camera frame to the fixed_room_marker


        i need to calculate then the tf from camera to map

        then publish the inverse transform from map to {camera_name}_localmap

        and the set the ar_track_alvar node to sleep until another calibration is required


        easy peasy :(

        """


        br = tf2_ros.StaticTransformBroadcaster()
        buffer = tf2_ros.Buffer()
        listener = tf2_ros.TransformListener(buffer)
        #listener = tf.TransformListener()
        rospy.sleep(1.0)


        camera = rospy.get_param('~camera', "camera") 
        #parent_frame_id = f"{camera}_parent"
        parent_frame_id = f"{camera}_localmap"
        #parent_frame_id = f"{camera}_infra1_optical_frame"
        #child_frame_id = "fixed_room_marker"
        #child_frame_id = "radius_localmap"
        child_frame_id = "room"

        rospy.logwarn(buffer.all_frames_as_string())

        ## this transform will be available via alvar
        #trans = buffer.lookup_transform(parent_frame_id, child_frame_id, rospy.Time(0),rospy.Duration(5))
        trans = buffer.lookup_transform(child_frame_id, parent_frame_id, rospy.Time(0),rospy.Duration(5))
        #(origin_translation,orientation) = listener.lookupTransform(parent_frame_id, child_frame_id, rospy.Time(0))
        
        inverted= False
        origin_translation = trans.transform.translation
        orientation = trans.transform.rotation
        
        if inverted:
            origin_translation.x *=-1
            origin_translation.y *=-1
            origin_translation.z *=-1
       
        rev_ori=True
        if rev_ori:
            q = [orientation.x, orientation.y, orientation.z, orientation.w]
            roll, pitch, yaw = tft.euler_from_quaternion(q)

            # rebuild quaternion with yaw only
            #q_yaw_only = tft.quaternion_from_euler(0, 0, -yaw)
            #q_yaw_only = tft.quaternion_from_euler(0, 0, -2*yaw)
            #q_yaw_only = tft.quaternion_from_euler(0, 0, 2*yaw)
            q_yaw_only = tft.quaternion_from_euler(0, 0, yaw)
            orientation.x = q_yaw_only[0]
            orientation.y = q_yaw_only[1]
            orientation.z = q_yaw_only[2]
            orientation.w = q_yaw_only[3]
        
        calibrated_transform = tf2_ros.TransformStamped()
        calibrated_transform.child_frame_id = f"{camera}_localmap"
        calibrated_transform.header.stamp = rospy.Time.now()
        calibrated_transform.header.frame_id = "map"
        
        calibrated_transform.transform.translation = origin_translation
        
        no_orientation=False
        if no_orientation:
            calibrated_transform.transform.rotation.w = 1
        else:
            calibrated_transform.transform.rotation = orientation
        
        
        br.sendTransform(calibrated_transform) ## or the other way around
        
