$fn = 32;

// color: 0xff0000, shininess: 100
// ambientLight: 0x404040, 0.5
// directionalLight: 0xffffff, 0.8, position (1, 1, 1)

difference() {
    sphere(r = 1);
    
    // Simulate lighting effects through boolean operations
    intersection() {
        sphere(r = 1.01);
        rotate([45, 45, 0])
        cylinder(h = 2, r = 0.8, center = true);
    }
}