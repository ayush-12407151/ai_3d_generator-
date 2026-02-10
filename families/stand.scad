// ---------- Universal parameters ----------
height = 0;     // back support height
width  = 0;     // stand width
depth  = 0;     // base depth
angle  = 0;     // viewing angle
wall   = 0;     // thickness

$fn = 64;

// ---------- Derived dimensions ----------
base_thickness = wall * 1.2;
lip_height = wall * 2;
lip_depth  = wall * 2;

// ---------- Base ----------
cube([width, depth, base_thickness]);

// ---------- Back support ----------
rotate([angle,0,0])
translate([0, base_thickness, base_thickness])
cube([width, wall, height]);

// ---------- Front lip (anti-slip) ----------
translate([0, depth - lip_depth, base_thickness])
cube([width, lip_depth, lip_height]);

// ---------- Gusset / reinforcement ----------
translate([0, base_thickness, base_thickness])
linear_extrude(height=width)
polygon(points=[
    [0,0],
    [wall*3,0],
    [0,wall*3]
]);
