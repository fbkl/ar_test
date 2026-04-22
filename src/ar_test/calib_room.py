#!/usr/bin/env python3

import rospy
import tf2_ros
import tf
import std_msgs.msg
#import tf_transformations
import sys
from std_srvs.srv import Empty, EmptyResponse

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


        camera = "radius" ##TODO: PARAM!
        parent_frame_id = f"{camera}_parent"
        #child_frame_id = "fixed_room_marker"
        child_frame_id = "radius_localmap"

        rospy.logwarn(buffer.all_frames_as_string())

        ## this transform will be available via alvar
        #trans = buffer.lookup_transform(parent_frame_id, child_frame_id, rospy.Time(0),rospy.Duration(5))
        trans = buffer.lookup_transform(child_frame_id, parent_frame_id, rospy.Time(0),rospy.Duration(5))
        #(origin_translation,orientation) = listener.lookupTransform(parent_frame_id, child_frame_id, rospy.Time(0))
        
        origin_translation = trans.transform.translation
        orientation = trans.transform.rotation

        calibrated_transform = tf2_ros.TransformStamped()
        calibrated_transform.child_frame_id = f"{camera}_localmap"
        calibrated_transform.header.stamp = rospy.Time.now()
        calibrated_transform.header.frame_id = "map"
        
        calibrated_transform.transform.translation = origin_translation
        calibrated_transform.transform.rotation = orientation
        
        br.sendTransform(calibrated_transform) ## or the other way around
        
