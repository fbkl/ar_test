#include "ar_test/adjustable_tf.h"
#include "ar_test/adjustable_tfb.h"
#include "geometry_msgs/TransformStamped.h"
#include "ros/spinner.h"
#include "ros/time.h"

#include <ros/ros.h>
#include <ros/console.h>

using namespace std;
int main(int argc, char** argv) {
	try {
		ros::init(argc, argv, "adjustable_tf_node_test");


		if( ros::console::set_logger_level(ROSCONSOLE_DEFAULT_NAME, ros::console::levels::Debug) ) {
			ros::console::notifyLoggerLevelsChanged();
		}
		ROS_WARN_STREAM("started the mofo!" << argc);
		ROS_WARN_STREAM("started the mofo!" << argc);

		AdjustableTransformBroadcaster atb(ros::this_node::getName());
		geometry_msgs::TransformStamped t;
		t.header.stamp = ros::Time::now();


		auto nh = ros::NodeHandle("~");
		std::string parent_frame_id;
		std::string child_frame_id;
		
		double x,y,z;
		double qx,qy,qz,qw;


    if (argc != 10) {
        //cerr << "Usage: " << argv[0] << " num1 num2 num3 num4 num5 num6 str1 str2" << endl;
		nh.getParam("parent_frame_id", parent_frame_id);
		nh.getParam("child_frame_id", child_frame_id);
		nh.getParam("x", x);
		nh.getParam("y", y);
		nh.getParam("z", z);
		nh.getParam("qx", qx);
		nh.getParam("qy", qy);
		nh.getParam("qz", qz);
		nh.getParam("qw", qw);
        //return 1;
	ROS_WARN_STREAM("CHUMBUNDO" << argc);
    }
    else{

    // Read 6 integers
   
int NUM_NUMBER_ARGS=7;	    
    float nums[NUM_NUMBER_ARGS];
    for (int i = 0; i < NUM_NUMBER_ARGS; ++i) {
        nums[i] = atof(argv[i + 1]);
    }

    // Read 2 strings
    string str1 = argv[NUM_NUMBER_ARGS+1];
    string str2 = argv[NUM_NUMBER_ARGS+2];

    // Print to confirm
    std::string a =  "Numbers: ";
    for (int i = 0; i < NUM_NUMBER_ARGS; ++i) {
        a+= to_string(nums[i]) + " ";
    }
    ROS_WARN_STREAM(a + "\nStrings: " + str1 + ", " << str2);

    x = nums[0];
    y = nums[1];
    z = nums[2];
    
    qx = nums[3];
    qy = nums[4];
    qz = nums[5];
    qw = nums[6];
    
    parent_frame_id = str1;
    child_frame_id = str2;
    }





		t.child_frame_id = child_frame_id;
		t.header.frame_id = parent_frame_id;
		t.transform.rotation.x = qx;
		t.transform.rotation.y = qy;
		t.transform.rotation.z = qz;
		t.transform.rotation.w = qw;
		t.transform.translation.x = x;
		t.transform.translation.y = y;
		t.transform.translation.z = z;

		atb.sendTf(t);

		ros::AsyncSpinner spinner(2);
		spinner.start();
		ros::waitForShutdown();
	} catch (std::exception& e) {
		std::cout << "Program crashed while running. Reason: " << e.what() << std::endl;
		return -1;
	}
	return 0;
}

