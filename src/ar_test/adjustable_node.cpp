#include "ar_test/adjustable_tf.h"
#include "geometry_msgs/TransformStamped.h"
#include "ros/time.h"

#include <ros/ros.h>


int main(int argc, char** argv) {
	try {
		ros::init(argc, argv, "adjustable_tf_node_test");

		AdjustableTransformBroadcaster atb;
		geometry_msgs::TransformStamped t;
		t.header.stamp = ros::Time::now();

		t.child_frame_id = "test";
		t.header.frame_id = "map";
		t.transform.rotation.w = 1;
		t.transform.translation.x = 0.3;

		atb.sendTf(t);

		ros::spin();
	} catch (std::exception& e) {
		std::cout << "Program crashed while running. Reason: " << e.what() << std::endl;
		return -1;
	}
	return 0;
}

