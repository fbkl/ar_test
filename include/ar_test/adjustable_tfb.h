#ifndef ADJUSTABLE_TFB_FBK_HH
#define ADJUSTABLE_TFB_FBK_HH

#include "geometry_msgs/Transform.h"
#include "geometry_msgs/TransformStamped.h"
#include "ros/node_handle.h"
#include "ros/time.h"
#include "tf2_ros/buffer.h"
#include "tf2_ros/static_transform_broadcaster.h"
#include "tf2_ros/transform_listener.h"
#include "tf/transform_broadcaster.h"
#include "dynamic_reconfigure/client.h"
#include "dynamic_reconfigure/server.h"
#include "interactive_markers/interactive_marker_server.h"
#include "visualization_msgs/InteractiveMarker.h"
#include "visualization_msgs/InteractiveMarkerControl.h"
#include "visualization_msgs/InteractiveMarkerFeedback.h"
#include "visualization_msgs/InteractiveMarkerPose.h"
#include "visualization_msgs/Marker.h"
#include "ar_test/CompleteTFConfig.h"
#include <memory>
#include <unordered_map>
#include <ar_test/adjustable_tf.h>


class AdjustableTransformBroadcaster
{
	public:
		AdjustableTransformBroadcaster();
		AdjustableTransformBroadcaster(std::string ns);
		void sendTf(geometry_msgs::TransformStamped t);
		ros::NodeHandle nh;
	private:
		std::string my_namespace{"AdjTransf"}; 
		std::unordered_map<std::string,std::shared_ptr<AdjustableTransform>> my_atf_list;
		tf2_ros::StaticTransformBroadcaster tb;
		std::shared_ptr<interactive_markers::InteractiveMarkerServer> ms;
};
#endif
