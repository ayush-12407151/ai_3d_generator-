height = 0;
width = 0;
depth = 0;
wall = 0;
slots = 0;
drain = 0;

difference() {
    cube([width, depth, height]);
    translate([wall, wall, wall])
        cube([width-2*wall, depth-2*wall, height]);

    if (drain == 1)
        translate([width/2, depth/2, -1])
            cylinder(h=wall+2, r=wall*1.2);
}

if (slots > 1) {
    slot_gap = (width - 2*wall) / slots;
    for (i=[1:slots-1])
        translate([wall + i*slot_gap - wall/2, wall, wall])
            cube([wall, depth-2*wall, height-wall]);
}
