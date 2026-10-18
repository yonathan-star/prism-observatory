// Original LIGHT TIPPER PROTOTYPE for the official 8 mm printed marble.
// Separate moving scoop/lever; NOT validated operation, balance or printer fit.
ball_d=8; shell=.8; axle_bore=1.95; ballast_pin_bore=1.95;
cup_r=.875*ball_d;cup_depth=.375*ball_d;
curvature_r=(cup_r*cup_r+cup_depth*cup_depth)/(2*cup_depth);
center_z=1+curvature_r;cup_y=-17;
$fn=64;
module cup(){
 difference(){union(){
  // A shallow spherical cap, not a deep hemisphere that would need 90° tipping.
  translate([0,cup_y,center_z])difference(){
   intersection(){sphere(r=curvature_r+shell);translate([-15,-15,-center_z])cube([30,30,3.8]);}
   sphere(r=curvature_r);
  }
  translate([-2,-24,-.8])cube([4,40,1.3]);
  rotate([0,90,0])cylinder(r=2.2,h=4,center=true,$fn=32);
 }
 // Axle runs freely in a removable mount; bore options require a fit coupon.
 rotate([0,90,0])cylinder(d=axle_bore,h=6,center=true,$fn=32);
 // A front pouring notch lowers the release lip. Dump-stop angle needs testing.
 translate([-4.8,-29,3.0])cube([9.6,8,10]);
 // Rear slot for a separate adjustable printed counterweight carrier.
  // Open rear end accepts the captive slider from behind.
  translate([-1,7,-2])cube([2,11,5]);
 }
}
module ballast(){
 // Captive slider: upper block and underside flange straddle the 1.3 mm lever.
 // Low, broad mass keeps restoring torque at the dump stop.
 translate([-7,-5,.7])cube([14,10,4.4]);
 translate([-.8,-1.6,-1.1])cube([1.6,3.2,1.9]);
 translate([-2.5,-2,-1.8])cube([5,4,.7]);
}
module marble(){translate([0,0,4])sphere(d=8,$fn=96);}
