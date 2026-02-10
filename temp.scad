// Universal parameters
width = 80;   // overall size
wall = 4;    // thickness

$fn = 64;

// --- Mounting base ---
base_width = width * 0.6;
base_height = wall * 4;

cube([base_width, wall * 3, base_height]);

// --- Cantilever arm ---
arm_length = width * 0.7;
arm_height = wall * 2;

translate([base_width/2 - wall/2, wall * 3, base_height])
cube([wall, arm_length, arm_height]);

// --- Retention curve (prevents slip) ---
translate([base_width/2, wall * 3 + arm_length, base_height + arm_height/2])
rotate([90,0,0])
difference() {
    cylinder(h=wall, r=wall*2);
    translate([0,0,-1])
        cylinder(h=wall+2, r=wall);
}
