side = 140;
belt_width= 58;
belt_handle_distance = 40;
belt_handle_height = 8;
belt_handle_width = 7;
belt_handle_thickness = 10;
belt_z_thickness = 5;
plate_thickness = 1;
divet_thickness = 3;
tallness = 14;
border_width= 15;

$fs = 0.15;

module roundedcube(size = [1, 1, 1], center = false, radius = 0.5, apply_to = "all") {
	// If single value, convert to [x, y, z] vector
	size = (size[0] == undef) ? [size, size, size] : size;

	translate_min = radius;
	translate_xmax = size[0] - radius;
	translate_ymax = size[1] - radius;
	translate_zmax = size[2] - radius;

	diameter = radius * 2;

	obj_translate = (center == false) ?
		[0, 0, 0] : [
		-(size[0] / 2),
		-(size[1] / 2),
		-(size[2] / 2)
		];

	translate(v = obj_translate) {
		hull() {
			for (translate_x = [translate_min, translate_xmax]) {
				x_at = (translate_x == translate_min) ? "min" : "max";
				for (translate_y = [translate_min, translate_ymax]) {
					y_at = (translate_y == translate_min) ? "min" : "max";
					for (translate_z = [translate_min, translate_zmax]) {
						z_at = (translate_z == translate_min) ? "min" : "max";

						translate(v = [translate_x, translate_y, translate_z])
							if (
									(apply_to == "all") ||
									(apply_to == "xmin" && x_at == "min") || (apply_to == "xmax" && x_at == "max") ||
									(apply_to == "ymin" && y_at == "min") || (apply_to == "ymax" && y_at == "max") ||
									(apply_to == "zmin" && z_at == "min") || (apply_to == "zmax" && z_at == "max")
							   ) {
								sphere(r = radius);
							} else {
								rotate = 
									(apply_to == "xmin" || apply_to == "xmax" || apply_to == "x") ? [0, 90, 0] : (
											(apply_to == "ymin" || apply_to == "ymax" || apply_to == "y") ? [90, 90, 0] :
											[0, 0, 0]
											);
								rotate(a = rotate)
									cylinder(h = diameter, r = radius, center = true);
							}
					}
				}
			}
		}
	}
}




module actual_handle()
{
	color("Yellow")
		roundedcube([belt_handle_width,belt_width+belt_handle_thickness,belt_handle_height], true, 01, "zmax");
	//#cube([3,belt_width,belt_handle_height], center = true);
}

module handles_solids()
{
	translate([belt_handle_distance/2,0,belt_handle_height/2+plate_thickness])
		actual_handle();

	translate([-belt_handle_distance/2,0,belt_handle_height/2+plate_thickness])
		actual_handle();
}
module pyramid_cube(side = 10, thickness = 5)
{
	module add_divets(angle, side)
	{
		rotate([0,0,angle]) translate([side/2,0,0])
			divets(remove_center=true);
	}
	module a_divet(dist,ot,angle, remove_center)
	{


		difference(){
			union(){translate([-thickness/2,dist,thickness/2+ot/2])
				cube([thickness,divet_thickness+ot,thickness+2*ot], center=true);
				translate([-thickness/2,dist,thickness/2]) 
					rotate([0,angle,0])        translate([4.5,0,4.5]) sphere(2.0);         }    

			if(remove_center)
			{
				translate([-thickness/2,dist,thickness/2+ot/2])    cube([thickness+0.2,divet_thickness/3+ot,thickness+0.2+2*ot], center=true);



			}

		}

	}
	module divets(ot = 0, distance = side/4, angle=0, remove_center=false)
	{
		a_divet(distance,ot,angle, remove_center);
		a_divet(-distance,ot,angle, remove_center);

	}
	module sidewall(angle=0)
	{
		rotate([0,0,angle]) translate([side/2,0,0]) {rotate([0,45,0]) translate([0,0,thickness/2]) cube([side,side,thickness], center=true);

			//#cube([10,10,10], center=true);
		}
	}
	module sidewall_neg(angle=0)
	{
		rotate([0,0,angle]) translate([side/2,0,0]) 
		{
			rotate([0,45,0]) 
				translate([0,0,thickness/2]) 
				cube([side,side,thickness], center=true);
			divets(0.1, angle=180);
		}    
	}
	difference(){
		translate([0,0,thickness/2])  cube([side,side,thickness], center=true);

		sidewall(0);
		sidewall(90);
		sidewall_neg(180);
		sidewall_neg(270);   
	}
	add_divets(0,side);
	add_divets(90,side);
	//#cube([side,side,thickness], center=true);
}

module hole(side = 100, thickness=2, walls =3)
{
	difference(){
		pyramid_cube(side,thickness);
		translate([0,0,thickness/2+plate_thickness]) cube([side-2*walls,side-2*walls,thickness-plate_thickness], center=true);

	}

}

module just_plate()
{
	hole(side,tallness,border_width);



}
module plate()
{
	just_plate();
	difference(){

		{
			handles_solids();
		}
		translate([0,0,plate_thickness+belt_z_thickness/2])
			cube([side,belt_width,belt_z_thickness-$fs], center= true);
	}
}

//translate([side/2,side/2,plate_thickness/2]) 


//difference(){
plate();
//translate([0,0,-10])cube(100);}


//translate([-side/2,side/2,plate_thickness/2]) plate();

module reinforcement()
{
	translate([(belt_width+belt_handle_thickness/2)/2,0,plate_thickness/2+belt_z_thickness/2]) roundedcube([belt_handle_thickness/2,belt_handle_distance+belt_handle_width ,belt_z_thickness], true, 01, "zmax");

	translate([(belt_width+belt_handle_thickness/2)/2,0,2*plate_thickness]) 
		cube([belt_handle_thickness/2,side-2*border_width,plate_thickness], center=true);


}

rotate([0,0,90]) reinforcement();
rotate([0,0,-90]) reinforcement();
