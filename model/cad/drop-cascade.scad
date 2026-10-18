// Original preliminary FIXED drop-cascade concept. NOT a print-ready part.
// Official baseline: print a nominal 8 mm marble. No glass or steel substitution.
actual_marble_diameter=8;
preview_marble_diameter=8;
d=actual_marble_diameter>0?actual_marble_diameter:preview_marble_diameter;
assert(d>=8 && d<=16,"Only the 8–16 mm envelope range has been considered.");
wall=2.4;channel=d+max(2.4,.15*d);half=channel/2;
catch_clear=1.7*d+4;catch_r=catch_clear/2+wall;
span=max(60,4*d+12);gap=d+8;run_drop=6;
final_floor=d+6;entry=final_floor+3*run_drop+2*gap;
guard=d+2;back_guard=d+8;
$fn=40;
function floor_at(x,dir,start)=start-run_drop*(dir>0?(x+span/2)/span:(span/2-x)/span);
module tray(dir,start){
 // Real separate open U-trays, each with a continuously sloped floor.
 pts=[for(x=[-span/2,span/2])let(z=floor_at(x,dir,start))
  for(q=[[-half,guard],[-half,0],[half,0],[half,back_guard],
          [half+wall,back_guard],[half+wall,-wall],[-half-wall,-wall],[-half-wall,guard]])
   [x,q[0],z+q[1]]];
 caps=[[0,1,6],[0,6,7],[1,2,5],[1,5,6],[2,3,4],[2,4,5]];
 faces=concat(caps,[for(j=[0:7])each [[j,8+j,8+(j+1)%8],[j,8+(j+1)%8,(j+1)%8]]],
  [for(f=caps)[for(k=[2:-1:0])8+f[k]]]);
 difference(){
  polyhedron(points=pts,faces=[for(f=faces)[for(j=[2:-1:0])f[j]]],convexity=20);
  // View the marble through retaining windows narrower than its diameter.
  for(xx=[-span/2+4:7:span/2-6])translate([xx,-half-wall-1,floor_at(xx,dir,start)+2])
   cube([.55*d,wall+2,guard-3.2]);
 }
}
module catch_well(x,z,exit_dir){
 // The catch floor has the SAME grade as the outgoing tray. No flat dead pocket.
 difference(){
  translate([x,0,z-wall-1.5])cylinder(r=catch_r,h=guard+wall+1.5);
  intersection(){
   translate([x,0,z-wall-2])cylinder(r=catch_r-wall,h=guard+wall+4);
   translate([x,0,z])rotate([0,atan(exit_dir*run_drop/span),0])
    translate([-2*catch_r,-2*catch_r,0])cube([4*catch_r,4*catch_r,guard+2*catch_r]);
  }
  translate([x,0,z])rotate([0,atan(exit_dir*run_drop/span),0])
   translate([exit_dir>0?-1:-catch_r-1.2,-half,-.1])cube([catch_r+2.2,channel,guard+2*catch_r]);
 }
}
module drop_guards(x,zlow,zhigh,dir){
 // A guarded fall rather than a projectile jump. Front slots are narrower than d.
 translate([x,0,0])scale([dir,1,1]){
  translate([-2,catch_r-wall,zlow])cube([catch_r+2,wall,zhigh-zlow+guard]);
  translate([catch_r-wall,-catch_r,zlow])cube([wall,2*catch_r,zhigh-zlow+guard]);
  difference(){
   translate([-2,-catch_r,zlow])cube([catch_r+2,wall,zhigh-zlow+guard]);
   for(xx=[1:0.9*d:catch_r-3])translate([xx,-catch_r-1,zlow+d])cube([.55*d,wall+2,max(1,zhigh-zlow-2)]);
  }
 }
}
module concept(){
 union(){
  // Open heavy frame; front remains visible. Geometry is only a layout study.
  for(x=[-span/2-catch_r+2,span/2+catch_r-2])translate([x,catch_r+.2,0])cube([4,2.8,entry+guard+2]);
  translate([-span/2-catch_r,-catch_r-5,0])cube([span+2*catch_r,2*catch_r+10,3]);
  for(i=[0:2])let(dir=i%2==0?1:-1,z=entry-i*(gap+run_drop)){
   tray(dir,z);
   // Incoming catch is behind the lower tray's open high end.
   catch_well(-dir*span/2,z,dir);
   if(i<2)drop_guards(dir*span/2,z-run_drop-gap,z-run_drop,dir);
   // Real tabs join each incoming catch to the rear frame.
   xx=-dir*span/2;
   translate([xx+(xx<0?-catch_r-2:-2),catch_r-3,z-wall-1])cube([catch_r+4,6,3.2]);
  }
 }
}
module drop_module(){
 difference(){
  concept();
  for(x=[-37,37])for(y=[-12.5,12.5])translate([x,y,-.1])cylinder(d=3.4,h=2.5,$fn=24);
  // Incoming west port in the first catch; outgoing floor grade is preserved.
  translate([-span/2,0,entry])rotate([0,atan(run_drop/span),0])
   translate([-catch_r-2,-half,-.08])cube([catch_r+3,channel,guard+8]);
 }
}
