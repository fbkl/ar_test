side = 100;
belt_width= 28;
belt_handle_distance = 40;
belt_handle_height = 5;
belt_handle_thickness = 20;
belt_handle_width = 5;
belt_z_thickness = 3;
plate_thickness = 1;

translate([0,0,0]) cube([side,side,plate_thickness], center= true);

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
	roundedcube([belt_handle_width ,belt_width+belt_handle_thickness,belt_handle_height], true, 01, "zmax");
	//#cube([3,belt_width,belt_handle_height], center = true);
}

module handles_solids()
{
	translate([belt_handle_distance/2,0,belt_handle_height/2+plate_thickness/2])
		actual_handle();

	translate([-belt_handle_distance/2,0,belt_handle_height/2+plate_thickness/2])
		actual_handle();
}
difference(){

	{
		handles_solids();
	}
	translate([0,0,plate_thickness/2+belt_z_thickness/2])
		roundedcube([side,belt_width,belt_z_thickness-$fs], true,01);
}

module reinforcement()
{
	translate([(belt_width+belt_handle_thickness/2)/2,0,plate_thickness/2+belt_z_thickness/2]) roundedcube([belt_handle_thickness/2,belt_handle_distance+belt_handle_width ,belt_z_thickness], true, 01, "zmax");

}

rotate([0,0,90]) reinforcement();
rotate([0,0,-90]) reinforcement();
