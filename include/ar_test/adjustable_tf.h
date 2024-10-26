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
#include "visualization_msgs/Marker.h"
#include "ar_test/CompleteTFConfig.h"
#include <memory>
#include <unordered_map>


class AdjustableTransform: geometry_msgs::TransformStamped
{
	public:
		AdjustableTransform(const geometry_msgs::TransformStamped& t,
				tf2_ros::StaticTransformBroadcaster& tb_,
				ros::NodeHandle& nh,
				std::shared_ptr<interactive_markers::InteractiveMarkerServer> ms
				): geometry_msgs::TransformStamped{t},
			tb{tb_},
			markerServer(ms)
			{
				//create namespace with the child_frame_id
				private_nh = ros::NodeHandle(nh, t.child_frame_id);
				s = std::make_shared<dynamic_reconfigure::Server<ar_test::CompleteTFConfig>>(private_nh);
				//add the callback
				dynamic_reconfigure::Server<ar_test::CompleteTFConfig>::CallbackType cb;
				cb = boost::bind(&AdjustableTransform::reconfigure_tf_callback, this, _1,_2);

				s->setCallback(cb);
				// we want to override the initial params that this tf may have received from the parameter server or the config defaults
				override_params();

				build_6d_marker();
				// We also want to create the marker client
				auto clc = boost::bind(&AdjustableTransform::client_callback, this, _1);
				cl = std::make_shared<dynamic_reconfigure::Client<ar_test::CompleteTFConfig>>(t.child_frame_id, private_nh, clc);
			}

		void sendme()
		{
			geometry_msgs::TransformStamped t = *this;
			t.header.stamp = ros::Time::now();
			//t.child_frame_id = "test2";
			tb.sendTransform(t);
			markerServer->applyChanges();
		}

	private:
		ros::NodeHandle private_nh;
		tf2_ros::StaticTransformBroadcaster& tb;
		std::shared_ptr<dynamic_reconfigure::Server<ar_test::CompleteTFConfig>> s;
		std::shared_ptr<interactive_markers::InteractiveMarkerServer> markerServer;
		std::shared_ptr<dynamic_reconfigure::Client<ar_test::CompleteTFConfig>> cl;
		visualization_msgs::InteractiveMarker int_marker;

		void client_callback(const ar_test::CompleteTFConfig& config)
		{
			reconfigure_tf_callback(config,1);
		}
		void override_params()
		{
			private_nh.setParam("double_paramqw",this->transform.rotation.w);
			private_nh.setParam("double_paramqx",this->transform.rotation.x);
			private_nh.setParam("double_paramqy",this->transform.rotation.y);
			private_nh.setParam("double_paramqz",this->transform.rotation.z);
			private_nh.setParam("x",this->transform.translation.x);
			private_nh.setParam("y",this->transform.translation.y);
			private_nh.setParam("z",this->transform.translation.z);
			private_nh.setParam("parent_frame_id",this->header.frame_id);
			private_nh.setParam("child_frame_id",this->child_frame_id);

		}
		void build_6d_marker()
		{
			int_marker.header.frame_id = this->header.frame_id;
			int_marker.pose.position.x = this->transform.translation.x;
			int_marker.pose.position.y = this->transform.translation.y;
			int_marker.pose.position.z = this->transform.translation.z;
			int_marker.scale = 0.3;
			int_marker.name = "simple_6dof";
			int_marker.description = "Simple 6-DOF Control";

			makeBoxControl(int_marker);
			int_marker.controls[0].interaction_mode = visualization_msgs::InteractiveMarkerControl::MOVE_ROTATE_3D;

			visualization_msgs::InteractiveMarkerControl control;
			control.orientation.w = 1;
			control.orientation.x = 1;
			control.orientation.y = 0;
			control.orientation.z = 0;
			//control.orientation = normalizeGeoQ(control.orientation)
			control.name = "rotate_x";
			control.interaction_mode = visualization_msgs::InteractiveMarkerControl::ROTATE_AXIS;
			int_marker.controls.push_back(control);

			control.orientation.w = 1;
			control.orientation.x = 1;
			control.orientation.y = 0;
			control.orientation.z = 0;
			//control.orientation = normalizeGeoQ(control.orientation)
			control.name = "move_x";
			control.interaction_mode = visualization_msgs::InteractiveMarkerControl::MOVE_AXIS;
			int_marker.controls.push_back(control);

			control.orientation.w = 1;
			control.orientation.x = 0;
			control.orientation.y = 1;
			control.orientation.z = 0;
			//control.orientation = normalizeGeoQ(control.orientation)
			control.name = "rotate_z";
			control.interaction_mode = visualization_msgs::InteractiveMarkerControl::ROTATE_AXIS;
			int_marker.controls.push_back(control);

			control.orientation.w = 1;
			control.orientation.x = 0;
			control.orientation.y = 1;
			control.orientation.z = 0;
			//control.orientation = normalizeGeoQ(control.orientation)
			control.name = "move_z";
			control.interaction_mode = visualization_msgs::InteractiveMarkerControl::MOVE_AXIS;
			int_marker.controls.push_back(control);

			control.orientation.w = 1;
			control.orientation.x = 0;
			control.orientation.y = 0;
			control.orientation.z = 1;
			//control.orientation = normalizeGeoQ(control.orientation)
			control.name = "rotate_y";
			control.interaction_mode = visualization_msgs::InteractiveMarkerControl::ROTATE_AXIS;
			int_marker.controls.push_back(control);

			control.orientation.w = 1;
			control.orientation.x = 0;
			control.orientation.y = 0;
			control.orientation.z = 1;
			//control.orientation = normalizeGeoQ(control.orientation)
			control.name = "move_y";
			control.interaction_mode = visualization_msgs::InteractiveMarkerControl::MOVE_AXIS;
			int_marker.controls.push_back(control);

			auto fbf = boost::bind(&AdjustableTransform::processFeedback, this, _1);

			markerServer->insert(int_marker, fbf);
			//self.menu_handler.apply( self.server, int_marker.name )

		}
		void processFeedback(const visualization_msgs::InteractiveMarkerFeedbackConstPtr& feedback)

		{
			//to standardize here, we created a client that connects to the server, so here we should create a dynamic reconfigure call....
			ar_test::CompleteTFConfig config;

			config.double_paramqw = feedback->pose.orientation.w;
			config.double_paramqx = feedback->pose.orientation.x;
			config.double_paramqy = feedback->pose.orientation.y;
			config.double_paramqz = feedback->pose.orientation.z;
			
			config.x = feedback->pose.position.x;
			config.y = feedback->pose.position.y;
			config.z = feedback->pose.position.z;

			cl->setConfiguration(config);
			markerServer->applyChanges();
		}

		void reconfigure_tf_callback(const ar_test::CompleteTFConfig &config, uint32_t level)
		{
			ROS_INFO("Reconfigure request:\nparent_frame_id:%s,\nchild_frame_id:%s\nrpy %f,%f,%f\n q x:%f,y:%f,z:%f,w:%f\nx:%f,y:%f,z:%f"
					,config.parent_frame_id.c_str()
					,config.child_frame_id.c_str()
					,config.double_paramr
					,config.double_paramp
					,config.double_paramy
					,config.double_paramqx
					,config.double_paramqy
					,config.double_paramqz
					,config.double_paramqw
					,config.x
					,config.y
					,config.z
				);

			this->transform.translation.x = config.x;
			this->transform.translation.y = config.y;
			this->transform.translation.z = config.z;
			this->transform.rotation.w = config.double_paramqw;
			this->transform.rotation.x = config.double_paramqx;
			this->transform.rotation.y = config.double_paramqy;
			this->transform.rotation.z = config.double_paramqz;
			this->header.frame_id = config.parent_frame_id;
			this->child_frame_id = config.child_frame_id;
			sendme();
			// we also want to update the marker position


		}
		visualization_msgs::Marker makeBox(const visualization_msgs::InteractiveMarker& msg)
		{
			visualization_msgs::Marker marker;
			marker.type = visualization_msgs::Marker::CUBE;
			marker.scale.x = msg.scale * 0.45;
			marker.scale.y = msg.scale * 0.45;
			marker.scale.z = msg.scale * 0.45;
			marker.color.a = 1.0;
			return marker;
		}
		visualization_msgs::InteractiveMarkerControl makeBoxControl(visualization_msgs::InteractiveMarker& msg)
		{
			visualization_msgs::InteractiveMarkerControl control;
			control.always_visible = true;
			control.markers.push_back(makeBox(msg));
			msg.controls.push_back(control);
			return control;
		}
};
class AdjustableTransformBroadcaster
{
	public:
		AdjustableTransformBroadcaster()
		{
			nh = ros::NodeHandle(my_namespace);
			ms = std::make_shared<interactive_markers::InteractiveMarkerServer>(my_namespace);
		}
		void sendTf(geometry_msgs::TransformStamped t)
		{
			auto at = std::make_shared<AdjustableTransform>(t,tb,nh,ms);
			//add to my map
			my_atf_list[t.child_frame_id] = at;
			at->sendme();
		}
		ros::NodeHandle nh;
	private:
		std::string my_namespace{"AdjTransf"}; 
		std::unordered_map<std::string,std::shared_ptr<AdjustableTransform>> my_atf_list;
		tf2_ros::StaticTransformBroadcaster tb;
		std::shared_ptr<interactive_markers::InteractiveMarkerServer> ms;
};
#endif
