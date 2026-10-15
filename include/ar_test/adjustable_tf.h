#ifndef ADJUSTABLE_TF_FBK_HH
#define ADJUSTABLE_TF_FBK_HH

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


class AdjustableTransform
{
	public:
		geometry_msgs::TransformStamped my_own_transform;
		AdjustableTransform(const geometry_msgs::TransformStamped& t,
				tf2_ros::StaticTransformBroadcaster& tb_,
				ros::NodeHandle& nh,
				std::shared_ptr<interactive_markers::InteractiveMarkerServer> ms,
				std::string markerDescription = "Simple 6-DOF Controll"
				);
		
		void sendme(bool applyChangesNow= false);
		void update_marker();

		std::string ownMarkerDescription;

	private:
		bool do_update_marker{true};
		ros::NodeHandle private_nh;
		tf2_ros::StaticTransformBroadcaster& tb;
		std::shared_ptr<dynamic_reconfigure::Server<ar_test::CompleteTFConfig>> s;
		std::shared_ptr<interactive_markers::InteractiveMarkerServer> markerServer;
		std::shared_ptr<dynamic_reconfigure::Client<ar_test::CompleteTFConfig>> cl;
		//dynamic_reconfigure::Client<ar_test::CompleteTFConfig>* cl;
		visualization_msgs::InteractiveMarker int_marker;

		void client_callback(const ar_test::CompleteTFConfig& config);
		void override_params();
		void build_6d_marker();
		void processFeedback(const visualization_msgs::InteractiveMarkerFeedbackConstPtr& feedback);

		void reconfigure_tf_callback(const ar_test::CompleteTFConfig &config, uint32_t level);
		void reconfigure_tf(const ar_test::CompleteTFConfig &config);
		visualization_msgs::Marker makeBox(const visualization_msgs::InteractiveMarker& msg);
		visualization_msgs::InteractiveMarkerControl makeBoxControl(visualization_msgs::InteractiveMarker& msg);
};
#endif
