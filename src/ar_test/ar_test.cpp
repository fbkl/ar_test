#include <ar_test/adjustable_tf.h>
void ordinary_callback(const ar_test::CompleteTFConfig& config)
{
	ROS_INFO("this works just fine");

}

void descriptionCallback(const dynamic_reconfigure::ConfigDescription& description) {
	ROS_INFO("Received description");
}

AdjustableTransform::AdjustableTransform(const geometry_msgs::TransformStamped& t,
		tf2_ros::StaticTransformBroadcaster& tb_,
		ros::NodeHandle& nh,
		std::shared_ptr<interactive_markers::InteractiveMarkerServer> ms,
		std::string markerDescription
		): 
	tb{tb_},
	markerServer(ms),
	ownMarkerDescription(markerDescription)
{
	my_own_transform =t ;
	//create namespace with the child_frame_id
	private_nh = ros::NodeHandle(nh, t.child_frame_id);
	// we want to override the initial params that this tf may have received from the parameter server or the config defaults
	override_params();

	//now i can create the server

	s = std::make_shared<dynamic_reconfigure::Server<ar_test::CompleteTFConfig>>(private_nh);
	//add the callback
	dynamic_reconfigure::Server<ar_test::CompleteTFConfig>::CallbackType cb;
	cb = boost::bind(&AdjustableTransform::reconfigure_tf_callback, this, _1,_2);

	s->setCallback(cb);

	build_6d_marker();
	// We also want to create the marker client
	auto clc = boost::bind(&AdjustableTransform::client_callback, this, _1);

	std::string server_handle_string = private_nh.resolveName("/");
	ROS_DEBUG_STREAM("server_handle_string" << server_handle_string);

	auto even_more_private_nh = ros::NodeHandle(private_nh, t.child_frame_id);
	cl = std::make_shared<dynamic_reconfigure::Client<ar_test::CompleteTFConfig>>(server_handle_string);
	cl->setConfigurationCallback(clc);
	//cl->setConfigurationCallback(&ordinary_callback);
	cl->setDescriptionCallback(&descriptionCallback);
	ROS_DEBUG("Finished setting up AdjustableTransform");
}


void AdjustableTransform::sendme(bool applyChangesNow)
{
	ROS_DEBUG_STREAM("sendme called");
	ROS_DEBUG_STREAM("sendme got transform");
	my_own_transform.header.stamp = ros::Time::now();
	ROS_DEBUG_STREAM("sendme set header stamp");
	//t.child_frame_id = "test2";
	tb.sendTransform(my_own_transform);
	ROS_DEBUG_STREAM("sendme sent transform");
	if (applyChangesNow)
		markerServer->applyChanges();
	ROS_DEBUG_STREAM("sendme finished");
}
void AdjustableTransform::update_marker()
{
	//idk if it works, but definitely no longer a stub
	ROS_WARN_THROTTLE(20,"update markr is a stub!!");
	visualization_msgs::InteractiveMarkerPose pose;
	pose.pose.position.x = my_own_transform.transform.translation.x;
	pose.pose.position.y = my_own_transform.transform.translation.y;
	pose.pose.position.z = my_own_transform.transform.translation.z;
	if (do_update_marker)
	{	markerServer->applyChanges();
	do_update_marker = false;}
}

void AdjustableTransform::client_callback(const ar_test::CompleteTFConfig& config)
{
	ROS_DEBUG("Called client_callback");
	reconfigure_tf(config);
	do_update_marker = false;
	sendme();
}
void AdjustableTransform::override_params()
{
	ROS_DEBUG("Overriding params");
	private_nh.setParam("double_paramqw", my_own_transform.transform.rotation.w);
	private_nh.setParam("double_paramqx", my_own_transform.transform.rotation.x);
	private_nh.setParam("double_paramqy", my_own_transform.transform.rotation.y);
	private_nh.setParam("double_paramqz", my_own_transform.transform.rotation.z);
	private_nh.setParam("x",	      my_own_transform.transform.translation.x);
	private_nh.setParam("y",	      my_own_transform.transform.translation.y);
	private_nh.setParam("z",	      my_own_transform.transform.translation.z);
	private_nh.setParam("parent_frame_id",my_own_transform.header.frame_id);
	private_nh.setParam("child_frame_id", my_own_transform.child_frame_id);

}
void AdjustableTransform::build_6d_marker()
{
	ROS_DEBUG("build_6d_marker");
	int_marker.header.frame_id =my_own_transform.header.frame_id;
	int_marker.pose.position.x =my_own_transform.transform.translation.x;
	int_marker.pose.position.y =my_own_transform.transform.translation.y;
	int_marker.pose.position.z =my_own_transform.transform.translation.z;
	int_marker.scale = 0.3;
	int_marker.name = "simple_6dof";
	int_marker.description = ownMarkerDescription;

	visualization_msgs::InteractiveMarkerControl control;

	static auto control2 = makeBoxControl(int_marker);
	int_marker.controls[0].interaction_mode = visualization_msgs::InteractiveMarkerControl::MOVE_ROTATE_3D;

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
void AdjustableTransform::processFeedback(const visualization_msgs::InteractiveMarkerFeedbackConstPtr& feedback)

{
	ROS_DEBUG("called processFeedback");
	//to standardize here, we created a client that connects to the server, so here we should create a dynamic reconfigure call....
	ar_test::CompleteTFConfig config;

	config.double_paramqw = feedback->pose.orientation.w;
	config.double_paramqx = feedback->pose.orientation.x;
	config.double_paramqy = feedback->pose.orientation.y;
	config.double_paramqz = feedback->pose.orientation.z;

	config.x = feedback->pose.position.x;
	config.y = feedback->pose.position.y;
	config.z = feedback->pose.position.z;

	config.child_frame_id =   my_own_transform.child_frame_id;
	config.parent_frame_id =  my_own_transform.header.frame_id;

	//ROS_DEBUG("Calling client setConfiguration");
	cl->setConfiguration(config);
	update_marker();
	//ROS_DEBUG("Trying to applyChanges in markerServer");
	//markerServer->applyChanges();
	ROS_DEBUG("exited processFeedback");
}

void AdjustableTransform::reconfigure_tf_callback(const ar_test::CompleteTFConfig &config, uint32_t level)
{
	ROS_DEBUG("Reconfigure request:\nparent_frame_id:%s,\nchild_frame_id:%s\nrpy %f,%f,%f\n q x:%f,y:%f,z:%f,w:%f\nx:%f,y:%f,z:%f"
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

	reconfigure_tf(config);
	sendme();
	//update_marker();
	ROS_DEBUG("finished reconfigure request");

}
void AdjustableTransform::reconfigure_tf(const ar_test::CompleteTFConfig &config)
{
	ROS_DEBUG("started reconfigure_tf");
	my_own_transform.transform.translation.x = config.x;
	my_own_transform.transform.translation.y = config.y;
	my_own_transform.transform.translation.z = config.z;
	my_own_transform.transform.rotation.w = config.double_paramqw;
	my_own_transform.transform.rotation.x = config.double_paramqx;
	my_own_transform.transform.rotation.y = config.double_paramqy;
	my_own_transform.transform.rotation.z = config.double_paramqz;
	my_own_transform.header.frame_id = config.parent_frame_id;
	my_own_transform.child_frame_id = config.child_frame_id;
	ROS_DEBUG("finished reconfigure_tf");

}
visualization_msgs::Marker AdjustableTransform::makeBox(const visualization_msgs::InteractiveMarker& msg)
{
	visualization_msgs::Marker marker;
	marker.type = visualization_msgs::Marker::CUBE;
	marker.scale.x = msg.scale * 0.45;
	marker.scale.y = msg.scale * 0.45;
	marker.scale.z = msg.scale * 0.45;
	marker.color.r = 1.0;
	marker.color.g = 1.0;
	marker.color.b = 1.0;
	marker.color.a = 0.1;
	return marker;
}
visualization_msgs::InteractiveMarkerControl AdjustableTransform::makeBoxControl(visualization_msgs::InteractiveMarker& msg)
{
	visualization_msgs::InteractiveMarkerControl control;
	control.always_visible = true;
	control.markers.push_back(makeBox(msg));
	msg.controls.push_back(control);
	return control;
}
