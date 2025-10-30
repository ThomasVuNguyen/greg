// Background color: 0x87CEEB (sky blue)

// Main house body
// Material: 0xF5DEB3 (wheat)
cube([2, 1.5, 2], center = true);
translate([0, 0.75, 0]) cube([2, 1.5, 2], center = true);

// Roof
// Material: 0x8B4513 (saddle brown)
translate([0, 2.0, 0]) rotate([0, 45, 0]) cylinder(h = 1, r1 = 1.7, r2 = 0, $fn = 4);

// Door
// Material: 0x8B4513 (saddle brown)
translate([0, 0.4, 1.01]) cube([0.4, 0.8, 0.05], center = true);

// Windows
// Material: 0xADD8E6 (light blue) with emissive: 0x222222
translate([-0.6, 0.8, 1.01]) cube([0.4, 0.4, 0.05], center = true);
translate([0.6, 0.8, 1.01]) cube([0.4, 0.4, 0.05], center = true);

// Ground
// Material: 0x90EE90 (light green)
translate([0, -0.01, 0]) rotate([-90, 0, 0]) cube([10, 10, 0.02], center = true);