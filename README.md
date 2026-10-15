# ar_test

## TODO / description:

This package is a mess. It was never intended to be used in the first place, but here we are. What started as the AR cube from the Ishijima Electronics, now evolved to be a demo for bundles of the AR testing with the upperarm model mobl2016 from ros-opensimrt. 

The bundles are in bundles/ and the only description which is actually using multi markers is the thorax. It may be wrong because to use multimarkers we need rigid surfaces and in my lab everyone kept using the 3d printer so I couldnt print the brackets to show things that are a bit more resilient to occlusion. Without the physical bracket, fixing the bundle is very hard (for me), so I didn't write anything because it would likely not work. Either way, this is the most current state of this package. 

Only the acer camera is tip-top and everything else is maybe broken. If I had made better abstractions, then this wouldnt be a problem, but I am strapped for time and I don't usually have energy to make things polished. Only getting the bare minimum working already takes most of my time. 

I set this up to be exactly like the imus (instead maybe i should have gone for the actual model's angles, like without that pesky fixed-(90,0,0)-with-z-leading-axis transformation, but I just wanted to make this work. I never felt confident enough with this to set it up nicely. I relly strugle to find correct transformations. If you dont and want to fix my gar-baa-ge, please submit a pull request :) .  

## Making your own bundles. A partial guide

You can create the png for each of the markers using the ar_track_alvar tool createMarker (or something to that effect). Then print it and cut it out and glue it to some hard surface. That's it. 

Wait, no. THat's not it. You still need to create the xml definition of the bundle. 

If it is just one it is easier. I recommend opening rviz, adding the marker visualizer that ar_track_alvar thing publishes and looking at that. With a ton of trial and error you may be able to fix the axis of the markers. There is maybe a tool somewhere to actually show what each marker looks like and position the pngs so that you know what ros is seeing and what you created irl match. To add a bunch, do this many times over, print attach to the surface (maybe in a way that you can remove if you figure out that you attached one marker in the wrong orientation), rinse, repeat until exaustion. If the marker doesnt jump when you change from visualizing one side to the other, it means it is probably working.  

Things to know. The order of the corners in each marker actually matter a lot. They will tell ar_track_alvar how each surface is oriented. THis was not obvious to me. But think about like an oriented square with some coordinate system attached to it. If you change the order, the attachment angles of the coordinate system will change. If you rotate the square the other way around you will flip it's normal, etc, that's basically the idea. Then changing the axis is easy, like, if you want to change what's is x to become y, just change the labels, inverting axis is the same as putting a negative sign on one of the coordinates and so on. If you have good visualization and 3d rotation skills, this shouldn't be too hard, but to me, this was hard- still, it only took like a couple of days to fix. And with this disclaimer (and hopefully a working example), it should be easier to create your own. 

What else... The faces may be rotated, everything rotates, everything spins, your head spins, good luck. Oh, get coloured markers (red, green and blue) and make a ton of drawings. They may be wrong, but eventually you will get it right. 


# Old:

## Usage:

Catkin_make and source the catkin workspace with `ar_track_alvar`, `usb_cam` and this package at least. 

Then launch

    roslaunch ar_test usb_cal.launch

and

    roslaunch ar_test test.launch

You will need the cube with the fiducials as well, printed and assembled. The file is ar_cube.png, courtesy of [Ishijima Electronics](http://ishi.main.jp/ros/ros_ar_bundle.html).

## Fix quaternions TF republisher:

To use run 

    ./fixquaternions.py

## Use dyn reconfigure:

First call the node `fixquaternions.py`. It is an executable, so you can just run it.

Then you have to use rqt like:

    rosrun rqt_gui rqt_gui -s reconfigure



## Calibrate:

If you are using an uncalibrated camera, such as new webcam, then you need to run the opencv calibration. You can print a calibration checkerboard pattern from [here](https://markhedleyjones.com/projects/calibration-checkerboard-collection). I got the 11x8 squares (which camera calibrator calls 10x7 because it refers to the number of vertices). If you print a different one, you will need to change the options below.

This will take a while as the algorithm needs to take a bunch of different pictures of the checkerboard pattern in different distances and orientations.

You can read more about camera calibration [here](https://learnopencv.com/camera-calibration-using-opencv/):

Then run:

If you are using a new webcam, then you need to run the opencv calibration:

    rosrun camera_calibration cameracalibrator.py --size 10x7 --square 0.025 image:=/usb_cam/image_raw camera:=/usb_cam

save the file and then load it into the launch file. you can copy how it was done in `usb_cal.launch` 

## fixquaternions2.py

use this to republish the exact same quaternion, because we fixed it in the SimpleServer when we are stacking the quaternion components

- z -> +y
- x -> +z
- y -> +x

this was a simple transformation to fix. now the paper cube, if you turn the algorithm on while it is pointed towards the screen like:

- Z pointing towards screen (x)
- Y pointing towards right ->
- X pointing up A

Then it aligns when used with OpenSimRT branch ros\_fixing\_cube v0.02.1

# TODO:

- fixquaternions should be parametrized
- create launch files for fixquaternions*
- 
