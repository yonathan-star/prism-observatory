// THE LAST OBSERVATORY / PRISM MACHINE — original AI-assisted review CAD.
// Official nominal 8 mm PRINTED marble. No physical function claim.
part="assembly-A";
cup_angle=-5;balance_position=9.7;selector_angle=225;
include <route-data.scad>
include <drop-cascade.scad>
include <light-tipper.scad>
$fn=40;
rail_ri=5.2;rail_ro=7.6;rail_guard=12;

function loft_faces(n,m)=concat([[for(j=[0:m-1])j]],
 [for(i=[0:n-2])for(j=[0:m-1])each [[i*m+j,(i+1)*m+j,(i+1)*m+(j+1)%m],
 [i*m+j,(i+1)*m+(j+1)%m,i*m+(j+1)%m]]],[[for(j=[m-1:-1:0])(n-1)*m+j]]);
module loft(points,tangents,profile){
 polyhedron(points=[for(i=[0:len(points)-1])for(q=profile)
  [points[i][0]-tangents[i][1]*q[0],points[i][1]+tangents[i][0]*q[0],points[i][2]+q[1]]],
 faces=loft_faces(len(points),len(profile)),convexity=30);
}
module route_outer(i,extra=0,deep=2.4,height=rail_guard){
 points=[for(j=[0:len(routes[i])-1])routes[i][j]+(extra>0?(j==0?-extra:j==len(routes[i])-1?extra:0):0)*[route_tangents[i][j][0],route_tangents[i][j][1],0]];
 loft(points,route_tangents[i],[[-rail_ro-extra,-deep],[rail_ro+extra,-deep],[rail_ro+extra,height],[-rail_ro-extra,height]]);
}
module route_air(i){
 points=[for(j=[0:len(routes[i])-1])routes[i][j]+(j==0?-.8:j==len(routes[i])-1?.8:0)*[route_tangents[i][j][0],route_tangents[i][j][1],0]];
 loft(points,route_tangents[i],[[-rail_ri,-.03],[rail_ri,-.03],[rail_ri,25],[-rail_ri,25]]);
}
module route_spine(i){loft(routes[i],route_tangents[i],[[-4.7,-8],[4.7,-8],[4.7,-1.3],[-4.7,-1.3]]);}
module cylinder_air(x,y,z,r,slope,axis="x",h=40){
 intersection(){
  translate([x,y,z-4])cylinder(r=r,h=h+8,$fn=64);
  translate([x,y,z])rotate(axis=="x"?[0,atan(slope),0]:[-atan(slope),0,0])
   translate([-2*r,-2*r,0])cube([4*r,4*r,h+2*r]);
 }
}
module catch_outer(x,y,z,r,h){
 translate([x,y,3])cylinder(r1=r*.68,r2=r*.88,h=z-5.3,$fn=12);
 translate([x,y,z-3.9])cylinder(r=r,h=h+3.9,$fn=64);
 for(zz=[z-2,z+5,h>20?z+16:z+10])translate([x,y,zz])difference(){cylinder(r=r+.8,h=1.4,$fn=64);cylinder(r=r-.5,h=1.5,$fn=64);}
 for(a=[0:45:315])translate([x,y,3])rotate([0,0,a])translate([r-1.1,-1,0])cube([2.1,2,z+h-3]);
}
module catch_exit_air(x,y,z,r,axis,dir){
 translate([x,y,z])rotate(axis=="x"?[0,atan(.08*dir),0]:[-atan(.08*dir),0,0])
  if(axis=="x")translate([dir>0?-1:-r-2,-rail_ri,-.08])cube([r+3,2*rail_ri,35]);
  else translate([-rail_ri,dir>0?-1:-r-2,-.08])cube([2*rail_ri,r+3,35]);
}
module receiver_airs(){
 cylinder_air(38,104,86,13,.08,"x");catch_exit_air(38,104,86,15.4,"x",1);
 cylinder_air(tipper_xyz[0],90,84,16,-.08,"y");catch_exit_air(tipper_xyz[0],90,84,18.4,"y",-1);
 // The branch-B receiver has narrow viewing windows, below its guard crown.
 for(a=[-150:30:150])translate([tipper_xyz[0],90,0])rotate([0,0,a])
  translate([15,-2.2,92])cube([7,4.4,14]);
}
module fixed_receivers(){
 difference(){catch_outer(38,104,86,15.4,16);
  cylinder_air(38,104,86,13,.08,"x");catch_exit_air(38,104,86,15.4,"x",1);}
 difference(){catch_outer(tipper_xyz[0],90,84,18.4,28);
  cylinder_air(tipper_xyz[0],90,84,16,-.08,"y");catch_exit_air(tipper_xyz[0],90,84,18.4,"y",-1);
  for(a=[-150:30:150])translate([tipper_xyz[0],90,0])rotate([0,0,a])translate([15,-2.2,92])cube([7,4.4,14]);
 }
}
module merge_outer(){
 translate([82,68,3])linear_extrude(height=93,convexity=10)offset(r=3)square([30,23.6],center=true);
 for(x=[64,100])for(y=[53.2,82.8])translate([x,y,3])cube([2.5,2.5,91]);
}
module merge_air(){
 profile=concat([[-12.4,35]],[for(j=[0:32])let(q=-12.4+24.8*j/32)[q,.005*q*q]],[[12.4,35]]);
 loft([[66.4,68,78+.08*(66.4-72)],[97.6,68,78+.08*(97.6-72)]],[[1,0],[1,0]],profile);
}
module foundation(){
 difference(){linear_extrude(3)translate([5,5])offset(r=5)square([134,134]);
  for(y=[10:24:135])translate([7,y,2.65])cube([130,.5,.5]);
  for(x=[10:24:135])translate([x,7,2.65])cube([.5,130,.5]);
 }
 for(p=concat(funnel_pegs,cascade_pegs))translate(p)cylinder(d=3,h=2,$fn=24);
}
module pier(x,y,h,w=8){
 translate([x,y,3])linear_extrude(height=h-3,scale=.85)offset(r=.6)square([w-1.2,w-1.2],center=true);
 translate([x-w/2-1,y-w/2-1,2.9])cube([w+2,w+2,3.1]);
 translate([x-w/2-.6,y-w/2-.6,h-1.1])cube([w+1.2,w+1.2,2.1]);
 for(z=[14:15:h-5])translate([x-w/2-.2,y-w/2-.2,z])cube([w+.4,w+.4,.9]);
}
module route_supports(){
 for(spec=[[0,.10],[1,.20],[1,.50],[1,.76],[2,.30],[2,.60]])
  let(i=spec[0],j=round((len(routes[i])-1)*spec[1]),p=routes[i][j])pier(p[0],p[1],p[2]-6.5,8);
}
service4=[.20,.45,.72];
function service5_point(k)=let(p=routes[5][k==0?45:105])p+[k==0?3.2:0,0,0];
module service_mounts(){
 for(f=service4)let(p=routes[4][round((len(routes[4])-1)*f)]){
  pier(p[0],p[1],p[2]-8.2,8);
  translate([p[0],p[1],p[2]-7.2])cylinder(d=3,h=2,$fn=24);
 }
 for(k=[0:1])let(p=service5_point(k)){
  translate([p[0],p[1],3])cylinder(r=2.2,h=p[2]-10.6,$fn=32);
  translate([p[0],p[1],p[2]-7.6])cylinder(d=2,h=2,$fn=24);
 }
}
module service_track(i){difference(){union(){
 route_outer(i);route_spine(i);
 if(i==5)for(k=[0:1])let(p=service5_point(k))translate([p[0],p[1],p[2]-8])cylinder(r=2.8,h=3,$fn=32);
 }
 route_air(i);
 if(i==4)for(f=service4)let(p=routes[4][round((len(routes[4])-1)*f)]){
  translate([p[0]-4.85,p[1]-4.85,p[2]-15])cube([9.7,9.7,7.8]);
  translate([p[0],p[1],p[2]-7.3])cylinder(d=3.4,h=2.7,$fn=24);
 }
 if(i==5)for(k=[0:1])let(p=service5_point(k)){
  translate([p[0],p[1],p[2]-15])cylinder(r=2.65,h=7.4,$fn=32);
  translate([p[0],p[1],p[2]-7.7])cylinder(d=2.4,h=2.7,$fn=24);
 }
}}
module selector_mount(){
 translate([selector_xy[0],selector_xy[1],3])difference(){cylinder(r=7.2,h=selector_floor-11.3,$fn=12);
  translate([0,0,7])cylinder(r=4.4,h=selector_floor-25,$fn=12);}
 // The stem seats manually in this open bearing cup.
 translate([selector_xy[0],selector_xy[1],selector_floor-8.5])difference(){
  cylinder(r=4.8,h=5.2,$fn=48);translate([0,0,-.1])cylinder(d=5,h=5.5,$fn=32);
 }
 for(spec=[[225,-1],[315,1]])let(a=spec[0],t=[-sin(a),cos(a)],p=selector_xy+7*[cos(a),sin(a)]+spec[1]*2.7*t)
  translate([p[0],p[1],selector_floor-6.1])rotate([0,0,a+90])cube([2,6,5.2],center=true);
}
module selector_socket_air(){translate([selector_xy[0],selector_xy[1],selector_floor-8.4])cylinder(d=5,h=5.2,$fn=48);}
module tipper_mount(){
 for(sign=[-1,1])let(x=tipper_xyz[0]+sign*4.4){
  translate([x-2,102,3])cube([4,4,tipper_xyz[2]-3]);
  translate([x,104,tipper_xyz[2]])rotate([0,90,0])cylinder(r=3.5,h=4,center=true,$fn=40);
 }
 // Precisely posed pads contact the lever only at the intended end positions.
 translate(tipper_xyz)rotate([-5,0,0])translate([-2.8,3,-3.8])cube([5.6,2,3]);
 translate([tipper_xyz[0]-2.8,106.5,84])cube([5.6,4,27.5]);
 translate(tipper_xyz)rotate([55,0,0])translate([-2.8,-9,-3.8])cube([5.6,2,3]);
 translate([tipper_xyz[0]-2.8,98.7,84])cube([5.6,2.6,21.2]);
}
module tipper_bore_air(){translate(tipper_xyz)rotate([0,90,0])cylinder(d=1.95,h=16,center=true,$fn=40);}
module feed_hopper_outer(){translate([tipper_xyz[0],88,122.5])cylinder(r=8,h=14,$fn=56);}
module feed_hopper_air(){translate([tipper_xyz[0],88,116])cylinder(r=5.6,h=25,$fn=64);}
module funnel_island_air(){translate([funnel_xy[0],funnel_xy[1],115])cylinder(r=26,h=40,$fn=100);}
module cup_sweep_air(){
 for(a=[-5:5:50])hull()for(b=[a,a+5])translate(tipper_xyz)rotate([b,0,0])
  translate([0,-17,-1.4])cylinder(r=9.2,h=7,$fn=40);
}
module annulus(r,inner,h){difference(){cylinder(r=r,h=h);translate([0,0,-.1])cylinder(r=inner,h=h+.2);}}
module torus(r,tube){rotate_extrude($fn=72)translate([r,0])circle(r=tube,$fn=12);}
module conduit(a,b,r=1.4){hull(){translate(a)sphere(r=r,$fn=16);translate(b)sphere(r=r,$fn=16);}}
module fixed_gauge(){
 translate([138,94,49.5])rotate([0,90,0]){
  torus(4.5,1.05);cylinder(d=4,h=2.2,center=true,$fn=24);
  for(a=[0:90:270])rotate([0,0,a])translate([0,-.7,-.7])cube([4.5,1.4,1.4]);
  rotate([0,0,35])translate([0,-.6,.5])cube([3.7,1.2,1.4]);
 }
}
module ruin_reliefs(){intersection(){
 union(){
 // Shallow arch niches on the exterior of the central machine-hall plinth.
 for(y=[64,74.5])translate([98.3,y,54])rotate([0,90,0])linear_extrude(5)
  union(){translate([0,-3.3])square([32,6.6]);circle(r=3.3,$fn=32);}
 // Recessed dressed-stone courses: never reach the marble floor above Z77.
 for(z=[14:12:62])translate([99.4,57,z])cube([4,22,.8]);
 for(spec=[[64.5,26],[71.5,38],[64.5,50]])translate([99.4,spec[0],spec[1]])cube([4,.8,11.2]);
 // A shallow lancet on the surviving front survey pillar.
 translate([28.8,18.7,40])rotate([90,0,0])linear_extrude(1.6,center=true)
  union(){translate([-1.5,-12])square([3,12]);circle(r=1.5,$fn=24);}
 }
 // Keep these shallow carvings on the hall/pillar, clear of the receiver ribs.
 translate([-10,-10,0])cube([110.6,170,151]);
}}
module architecture(){
 // Functional islands remain open; decoration is outside feed and moving space.
 for(x=[61,90]){
  translate([x-3,137,3])cube([6,6,124]);
  for(z=[12:13:121])translate([x-3.5,136.7,z])cube([7,6.3,.9]);
  translate([x-4,136.7,124])cube([8,6.3,3]);
 }
 translate([59,137,125])cube([33,6,3]);
 translate([75.5,140,137])rotate([90,0,0]){
  torus(10.5,1.5);
  torus(7.3,.95);
  for(a=[0:30:330])rotate([0,0,a])translate([10,-.8,-1.1])cube([2.8,1.6,2.2]);
  cylinder(r=3.4,h=2.6,center=true,$fn=8);
  for(a=[0:60:300])rotate([0,0,a])translate([0,-.65,-.65])cube([10,1.3,1.3]);
  // Inner meridian, attached to the radial spokes; fixed celestial sculpture.
  rotate([0,35,0])torus(4.4,.9);
 }
 for(x=[28.8]){
  translate([x-2.7,18.8,3])cube([5.4,5.4,61]);
  for(z=[10:12:60])translate([x-3.2,18.3,z])cube([6.4,6.4,1]);
  translate([x-3.2,18.3,63.5])cube([6.4,6.4,2]);
  for(spec=[[-2.5,0,4.2],[.1,.5,2.7]])translate([x+spec[0],19+spec[1],65.2])cube([2.4,3.8,spec[2]]);
 }
 // Fixed service conduits frame the hall without covering either action.
 conduit([137,94,3],[137,94,68]);conduit([137,94,68],[129,94,68]);fixed_gauge();
 conduit([8,100,3],[8,100,65]);conduit([8,100,65],[27,100,65]);
 for(z=[12:13:64])translate([137,94,z])cylinder(r=2.05,h=1.3,$fn=24);
 for(z=[12:13:64])translate([8,100,z])cylinder(r=2.05,h=1.3,$fn=24);
 // Stepped stone quoins on the visible hall face are supported by its core.
 for(z=[9:12:61])for(y=[56.6,79.6])translate([99.5,y,z])cube([2.3,3.6,2.5]);
 // Celestial survey markers stay clear of the removable module feet.
 for(p=[[11,13],[133,133]])translate([p[0],p[1],3])cylinder(r=3,h=3,$fn=6);
}
module collector_outer(){catch_outer(72,16,11.8,14.4,15);}
module collector_air(){
 translate([72,16,11.8])cylinder(r=12,h=25,$fn=64);
 translate([72,16-rail_ri,11.75])cube([18,2*rail_ri,30]);
}
module chassis(){union(){
 difference(){union(){
  foundation();for(i=[0:3]){route_outer(i);route_spine(i);}route_supports();
  fixed_receivers();
  merge_outer();selector_mount();tipper_mount();feed_hopper_outer();collector_outer();architecture();
 }
  for(i=[0:5])route_air(i);
  merge_air();selector_socket_air();tipper_bore_air();feed_hopper_air();collector_air();cup_sweep_air();funnel_island_air();
  // Rear counterweight corner clearance, below the branch-B track floor.
  translate([tipper_xyz[0]-7.5,114.5,120])cube([15,5,5.1]);
  ruin_reliefs();
  for(i=[4:5])route_outer(i,.3,8.3,25);
  for(z=[12,108])translate([selector_xy[0]-2,selector_xy[1]-8,z])cube([4,6,8]);
 }
 service_mounts();
}}
module funnel_inner(){
 rotate_extrude($fn=100)polygon([[0,95.9],[5.25,95.9],[5.25,116],[8,116.4],[20,119.8],[27,122],[27,140],[0,140]]);
}
module funnel_world(){
 difference(){union(){
  translate([funnel_xy[0],funnel_xy[1],113.6])cylinder(r1=7.65,r2=30.5,h=8.4,$fn=100);
  translate([funnel_xy[0],funnel_xy[1],96])cylinder(r=7.65,h=20,$fn=64);
  translate([funnel_xy[0],funnel_xy[1],121]){$fn=100;annulus(30.65,27,13);}
  for(p=funnel_pegs){
   translate(p)cylinder(r=4.8,h=3,$fn=12);
   translate([p[0]-2.4,p[1]-2.4,5])cube([4.8,4.8,116]);
   for(z=[14:15:113])translate([p[0]-2.8,p[1]-2.8,z])cube([5.6,5.6,.8]);
  }
 }
  translate([funnel_xy[0],funnel_xy[1],0])funnel_inner();
  for(p=funnel_pegs)translate([p[0],p[1],2.9])cylinder(d=3.4,h=2.6,$fn=24);
  // Clearance pocket receives the fixed tangential feed tongue.
  difference(){route_outer(0,.5,20,30);translate([funnel_xy[0],funnel_xy[1],110])cylinder(r=25.7,h=50,$fn=100);}
  // Conservative full rotor disk clearance above the remaining retaining rim.
  translate([selector_xy[0],selector_xy[1],selector_floor-9.2])cylinder(r=16.6,h=35,$fn=100);
  // Lower stop-support clearance stays outside the R27 bowl interior.
  translate([selector_xy[0],selector_xy[1],118])cylinder(r=11.2,h=8,$fn=80);
  // Celestial runes are recessed only into the outside of the retaining rim.
  for(a=[155:35:330])translate([funnel_xy[0],funnel_xy[1],0])rotate([0,0,a]){
   translate([29.95,-.55,124.2])cube([2.2,1.1,6.2]);
   translate([29.95,0,128.4])rotate([45,0,0])translate([0,-1.7,-1.7])cube([2.2,3.4,3.4]);
  }
  // Front-facing, shallow lancets leave the support-leg cores intact.
  for(p=funnel_pegs)translate([p[0],p[1]-1.95,62])rotate([90,0,0])linear_extrude(1.4,center=true)
   union(){translate([-1.1,-26])square([2.2,26]);circle(r=1.1,$fn=24);}
 }
}
module cascade_local(){difference(){drop_module();translate(-cascade_xyz)route_outer(4,.3,8.3,24);
 translate(-cascade_xyz)translate([63.7,52.9,0])cube([39.1,34,100]);
 translate(-cascade_xyz)translate([56,0,0])cube([34,31.5,12]);}}
module selector_untrimmed(){
 p=[[0,0,0],[0,-16,-1.6]];t=[[0,-1],[0,-1]];
 difference(){union(){
  loft(p,t,[[-7.6,-2.4],[7.6,-2.4],[7.6,12],[-7.6,12]]);
  translate([-7.6,.1,-2.4])cube([15.2,2.4,14.4]);
  translate([0,0,-6.4])cylinder(d=4.6,h=5,$fn=40);
  translate([0,0,-3.3])cylinder(r=3.9,h=1.9,$fn=48);
  translate([-3,2.1,0])cube([6,9.9,2.4]);
  translate([0,7,-4.3])cylinder(r=1.6,h=4.3,$fn=24);
 }
  loft(p,t,[[-5.2,-.03],[5.2,-.03],[5.2,30],[-5.2,30]]);
 }
}
module selector_local(){intersection(){selector_untrimmed();translate([0,0,-7])cylinder(r=16,h=40,$fn=100);}}
module axle(){rotate([0,90,0])cylinder(d=1.75,h=18.8,center=true,$fn=40);}
module retainer(){difference(){cylinder(d=4.2,h=2.4,$fn=40);translate([0,0,-.1])cylinder(d=1.7,h=3,$fn=32);translate([0,-.4,-.1])cube([4,.8,3]);}}
module coupon(){difference(){
 linear_extrude(4)offset(r=2)translate([2,2])square([86,26]);
 for(i=[0:4])translate([10+15*i,9,-.1])cylinder(d=[1.8,1.95,2.1,2.25,2.4][i],h=4.2,$fn=32);
 for(i=[0:5])translate([10+15*i,21,-.1])cylinder(d=[3.2,3.4,3.6,5,5.2,5.4][i],h=4.2,$fn=40);
 translate([-1,-1,-.1])cube([5,5,4.2]);
}}
module balance_endclip(){difference(){translate([-3.2,0,-1.4])cube([6.4,3.2,3.2]);translate([-2.15,-.1,-.95])cube([4.3,2.9,1.6]);}}
module light_ballast(){difference(){ballast();translate([-4.5,-3,2.1])cube([9,6,3.1]);}}
module moving_cup(angle=cup_angle,pos=balance_position){translate(tipper_xyz)rotate([angle,0,0]){
 cup();translate([0,pos,0])ballast();translate([0,15.7,0])balance_endclip();}}
module rotor_world(angle=selector_angle){translate([selector_xy[0],selector_xy[1],selector_floor])rotate([0,0,angle])selector_local();}
module assembly(angle=selector_angle,ca=cup_angle,bp=balance_position){
 chassis();funnel_world();translate(cascade_xyz)cascade_local();
 service_track(4);service_track(5);
 moving_cup(ca,bp);rotor_world(angle);translate(tipper_xyz)axle();
 for(sign=[-1,1])translate(tipper_xyz+[sign*6.6,0,0])rotate([0,sign*90,0])retainer();
}
if(part=="chassis")chassis();
else if(part=="funnel")translate([-funnel_xy[0],-funnel_xy[1],-3])funnel_world();
else if(part=="cascade")cascade_local();
else if(part=="approach-bridge")translate([-7.4,-34.4,-59.03])service_track(4);
else if(part=="collector-ramp")translate([-82,-8.4,-4])service_track(5);
else if(part=="cup")translate([0,0,2.2])cup();
else if(part=="ballast")translate([0,0,1.8])ballast();
else if(part=="ballast-light")translate([0,0,1.8])light_ballast();
else if(part=="balance-endclip")translate([0,0,1.4])balance_endclip();
else if(part=="selector")translate([0,0,6.4])selector_local();
else if(part=="axle")rotate([0,-90,0])translate([9.4,0,0])axle();
else if(part=="retainer")retainer();
else if(part=="coupon")coupon();
else if(part=="marble")marble();
else if(part=="motion-cup")intersection(){chassis();union(){for(a=[-4.5:5:54.5])moving_cup(a,balance_position);}}
else if(part=="motion-selector")intersection(){union(){chassis();funnel_world();}union(){for(a=[135.5:5:224.5])rotor_world(a);}}
else if(part=="assembly-B")assembly(135);
else if(part=="assembly-dump")assembly(135,55);
else assembly(225);
