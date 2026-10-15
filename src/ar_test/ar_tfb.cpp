#include <ar_test/adjustable_tfb.h>
AdjustableTransformBroadcaster::AdjustableTransformBroadcaster()
{
	ROS_INFO("called the erm constructor without any parameters");
	nh = ros::NodeHandle(my_namespace);
	ms = std::make_shared<interactive_markers::InteractiveMarkerServer>(my_namespace);
}
AdjustableTransformBroadcaster::AdjustableTransformBroadcaster(std::string ns)
{
	static int i = 0;
	ROS_INFO_STREAM("called the erm constructor with namespace" << ns << " for the " << i << "th time.");
	nh = ros::NodeHandle(ns);
	ms = std::make_shared<interactive_markers::InteractiveMarkerServer>(ns);
}

void AdjustableTransformBroadcaster::sendTf(geometry_msgs::TransformStamped t)
{
	static auto at = std::make_shared<AdjustableTransform>(t,tb,nh,ms);
	//add to my map
	my_atf_list[t.child_frame_id] = at;
	at->sendme();
	at->update_marker();
}

