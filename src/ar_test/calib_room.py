#!/usr/bin/env python3

import numpy as np
import rospy
import tf2_ros
import tf
import std_msgs.msg
#import tf_transformations
import sys
from std_srvs.srv import Empty, EmptyResponse

import tf.transformations as tft


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
camera = rospy.get_param('~camera', "camera") 
        #parent_frame_id = f"{camera}_parent"
parent_frame_id = f"{camera}_localmap"
        #parent_frame_id = f"{camera}_infra1_optical_frame"
        #child_frame_id = "fixed_room_marker"
        #child_frame_id = "radius_localmap"
child_frame_id = f"{camera}_room" ## maybe this is map and i need to publish the tf from map to room

#child_frame_id = "map" # this does not work. the solution will be more complicated

## Time(0) means "the LATEST transform you have, however old". If the room marker was
## seen a minute ago and is clipped now, the old code averaged that same stale transform
## 10 times and "succeeded" silently. So: only calibrate on a marker seen just now, judged
## by LOCAL arrival of alvar's ar_pose_marker (never by stamps -- those come from the
## camera machine's clock), and take 10 DISTINCT detections, not 10 copies of one.
## diagnostics_schema/ar_visibility.py shows the same thing live under 'AR Markers'.
from ar_track_alvar_msgs.msg import AlvarMarkers
SEEN_TIMEOUT = 1.0     # s, local clock
SAMPLING_TIMEOUT = 5.0 # s, to collect all 10 distinct detections
last_seen_arrival = None

def ar_callback(msg):
    global last_seen_arrival
    if msg.markers:
        last_seen_arrival = rospy.get_time()

rospy.Subscriber("ar_pose_marker", AlvarMarkers, ar_callback, queue_size=1)

rospy.sleep(1.0)

def fail(why):
    rospy.logerr(f"[{camera}] calibration REFUSED: {why}")
    raise rospy.ServiceException(f"[{camera}] calibration refused: {why}")

def calib_callback(req):

        rospy.logwarn(buffer.all_frames_as_string())

        if last_seen_arrival is None:
            fail("room marker never detected by ar_track_alvar (clipped? out of view?)")
        if rospy.get_time() - last_seen_arrival > SEEN_TIMEOUT:
            fail(f"room marker not detected for {rospy.get_time() - last_seen_arrival:.1f} s (clipped? blurred? too far?)")

        quats = []
        vecs = []
        last_stamp = None
        deadline = rospy.get_time() + SAMPLING_TIMEOUT

        while len(quats) < 10:
            if rospy.get_time() > deadline:
                fail(f"only {len(quats)}/10 fresh detections in {SAMPLING_TIMEOUT} s -- marker flickering in and out of view")
            ## this transform will be available via alvar
            #trans = buffer.lookup_transform(parent_frame_id, child_frame_id, rospy.Time(0),rospy.Duration(5))
            try:
                trans = buffer.lookup_transform(child_frame_id, parent_frame_id, rospy.Time(0),rospy.Duration(1))
            except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
                fail(f"no transform {child_frame_id} <- {parent_frame_id}: {e}")
            if trans.header.stamp == last_stamp or rospy.get_time() - last_seen_arrival > SEEN_TIMEOUT:
                rospy.sleep(0.02) ## same detection as last time, or the marker just dropped out: wait for a new one
                continue
            last_stamp = trans.header.stamp
            #(origin_translation,orientation) = listener.lookupTransform(parent_frame_id, child_frame_id, rospy.Time(0))
            origin_translation = trans.transform.translation
            orientation = trans.transform.rotation
        
            q = [orientation.x, orientation.y, orientation.z, orientation.w]
            quats.append(q)

            v = [origin_translation.x, origin_translation.y, origin_translation.z ]
            vecs.append(v)

        ## averaging quaternions using the eigenvalue method
        Q = np.array(quats)
        M = Q.T @ Q
        eigvals, eigvecs = np.linalg.eigh(M)

        best_q = eigvecs[:, -1] ## the largest is the last one?
        orientation.x = best_q[0]
        orientation.y = best_q[1]
        orientation.z = best_q[2]
        orientation.w = best_q[3]
        #orientation = trans.transform.rotation

        ## now averaging the vecs

        V = np.array(vecs)
        best_v = V.mean(axis=0)
        assert(len(best_v) == 3) 
        origin_translation.x = best_v[0]
        origin_translation.y = best_v[1]
        origin_translation.z = best_v[2]
        #origin_translation = trans.transform.translation

        inverted= False
        
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
        calibrated_transform.header.frame_id = "room"
        
        calibrated_transform.transform.translation = origin_translation
        
        no_orientation=False
        if no_orientation:
            calibrated_transform.transform.rotation.w = 1
        else:
            calibrated_transform.transform.rotation = orientation
        
        
        br.sendTransform(calibrated_transform) ## or the other way around
        
        return EmptyResponse()


if __name__ == '__main__':
    s = rospy.Service('calib',Empty, calib_callback)
    rospy.spin()
