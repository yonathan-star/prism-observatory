// THE LAST OBSERVATORY / CASCADE — original AI-assisted review draft.
// New route. No inherited circular course. mm. Not printed or physically tested.
part="complete"; // complete,track,marble,architecture
$fn=32;
include <route-data.scad>
ri=5.2; wall=2.4; ro=ri+wall; ns=len(route_points); np=8;
function profile(i)=let(b=route_banks[i],l=13+8*max(0,-b)/24,r=13+8*max(0,b)/24)
 [[-ri,l],[-ri,ri*tan(b)],[ri,-ri*tan(b)],[ri,r],[ro,r],
  [ro,-ro*tan(b)-wall],[-ro,ro*tan(b)-wall],[-ro,l]];
function world(i,q)=let(p=route_points[i],t=route_tangents[i])
 [p[0]-t[1]*q[0],p[1]+t[0]*q[0],p[2]+q[1]];
caps=[[0,1,6],[0,6,7],[1,2,5],[1,5,6],[2,3,4],[2,4,5]];
faces=concat(caps,[for(i=[0:ns-2])for(j=[0:np-1])each
 [[i*np+j,(i+1)*np+j,(i+1)*np+(j+1)%np],
 [i*np+j,(i+1)*np+(j+1)%np,i*np+(j+1)%np]]],
 [for(f=caps)[for(k=[2:-1:0])(ns-1)*np+f[k]]]);
module trough(){polyhedron(points=[for(i=[0:ns-1])for(q=profile(i))world(i,q)],faces=[for(f=faces)[for(j=[2:-1:0])f[j]]],convexity=30);}
module route_air(){
 p=[for(i=[0:ns-1])for(q=[[-6.4,6.4*tan(route_banks[i])-.06],[6.4,-6.4*tan(route_banks[i])-.06],[6.4,23],[-6.4,23]])world(i,q)];
 f=concat([[0,1,2],[0,2,3]],[for(i=[0:ns-2])for(j=[0:3])each
 [[4*i+j,4*(i+1)+j,4*(i+1)+(j+1)%4],[4*i+j,4*(i+1)+(j+1)%4,4*i+(j+1)%4]]],
 [[4*(ns-1)+2,4*(ns-1)+1,4*(ns-1)],[4*(ns-1)+3,4*(ns-1)+2,4*(ns-1)]]);
 polyhedron(points=p,faces=f,convexity=30);
}
module at_route(i){p=route_points[i];t=route_tangents[i];translate([p[0],p[1],p[2]])rotate([0,0,atan2(t[1],t[0])])children();}
module annulus(r,inner,h){difference(){cylinder(r=r,h=h);translate([0,0,-0.1])cylinder(r=inner,h=h+0.2);}}
module torus(r,tube){rotate_extrude($fn=80)translate([r,0])circle(r=tube,$fn=12);}
module foundation(){difference(){linear_extrude(3)translate([5,5])offset(r=5)square([134,134]);
 for(y=[10:23:134])translate([8,y,2.65])cube([128,.55,.7]);
 for(x=[18:23:132])translate([x,8,2.65])cube([.55,128,.7]);
 translate([75,97,2.6])annulus(21,20.35,.7);
}}
module pier(h,w=10){
 translate([0,0,3])linear_extrude(height=max(1,h-3),scale=.86)
  polygon([[-w/2+1,-w/2],[w/2-1,-w/2],[w/2,-w/2+1],[w/2,w/2-1],[w/2-1,w/2],[-w/2+1,w/2],[-w/2,w/2-1],[-w/2,-w/2+1]]);
 translate([-w/2-2,-w/2-2,2.9])cube([w+4,w+4,3.1]);
 translate([-w/2-.8,-w/2-.8,h-1.4])cube([w+1.6,w+1.6,2.4]);
 for(z=[14:13:h-5])translate([-w/2-.2,-w/2-.2,z])cube([w+.4,w+.4,.85]);
}
module fenestration(w,d,h){ // Arched aperture along local Y.
 translate([-w/2,-d/2,0])cube([w,d,max(.1,h-w/2)]);
 translate([0,0,h-w/2])rotate([90,0,0])cylinder(r=w/2,h=d,center=true);
}
module keep(x,y,w,d,h){
 translate([x,y,0])difference(){union(){
  translate([-w/2,-d/2,2.9])cube([w,d,h-2.9]);
  for(z=[14:12:h-3])translate([-w/2-.6,-d/2-.6,z])cube([w+1.2,d+1.2,1]);
  translate([-w/2-1,-d/2-1,h-3])cube([w+2,d+2,3]);
 }
  for(z=[14:30:h-22])translate([0,0,z])fenestration(w*.44,d+4,17);
  for(z=[27:25:h-15])for(a=[-1,1])translate([a*w/2,0,z])rotate([0,0,90])fenestration(d*.34,5,13);
 }
}
module launch_keep(){
 keep(31,120,27,25,100.8);
 for(x=[20,43])for(y=[109,131])translate([x,y,0])pier(107+(x==20?7:0),6.5);
 // Start backstop only behind the continuous route entrance.
 at_route(0)translate([-2.6,-ro, -2.5])cube([2.7,2*ro,17]);
 // Broken beacon shelves, solid integral sculpture.
 translate([18,108,111])cube([8,25,3]);
 translate([20,111,113])cylinder(r1=4,r2=1.7,h=9,$fn=6);
}
module drum(x,y,r,h){
 translate([x,y,0])difference(){union(){
  translate([0,0,3])cylinder(r=r,h=h-3,$fn=12);
  for(z=[8:15:h-2])translate([0,0,z])cylinder(r=r+1,h=1.6,$fn=12);
  for(a=[0:60:300])rotate([0,0,a])translate([r-1.4,-1.5,3])cube([3,3,h-3]);
  translate([0,0,3])cylinder(r=r+3,h=4,$fn=12);
 }
 for(a=[0:90:270])rotate([0,0,a])translate([0,0,14])fenestration(8,2*r+6,min(h-20,24));
 }
}
module large_masses(){
 drum(92,92,16,98);
 // Three thick buttresses make the crescent tower read as a real abutment.
 for(a=[0,100,210])translate([92,92,3])rotate([0,0,a])
  linear_extrude(48,scale=.5)translate([13,-3])square([9,6]);
 drum(40,71,10.5,72);
 drum(108,33,9.2,48);
 drum(48,36,10.5,31);
}
module radial_arms(){
 for(spec=[[1,92,92,14,30],[3,40,71,9,20],[5,108,33,8,18],[7,48,36,9,21]])
 for(v=[.12,.40,.68,.88])let(i=round(stage_bounds[spec[0]][0]*(1-v)+stage_bounds[spec[0]][1]*v),
  p=route_points[i],a=atan2(p[1]-spec[2],p[0]-spec[1]))
  translate([spec[1],spec[2],p[2]-7])rotate([0,0,a])translate([spec[3],-2.4,0])
   cube([spec[4]-spec[3]+1,4.8,5.8]);
}
module arcade_wall(x,y,length,z0,z1,thick,holes){
 difference(){
  translate([x,y,0])multmatrix([[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]])
   linear_extrude(thick,center=true)polygon([[0,3],[length,3],[length,z1-2.2],[0,z0-2.2]]);
  for(q=holes)translate([x+q[0],y,7])fenestration(q[1],thick+2,q[2]);
 }
}
module aqueducts(){
 arcade_wall(43,122,49,101.74,94.37,8,[[12,16,59],[36,16,54]]);
 arcade_wall(48,15,60,33.70,42.73,8,[[13,16,20],[37,17,24]]);
}
module machine_hall(){
 // Bulk is concentrated in paired walls and four structural pylons.
 difference(){union(){
  translate([53,39,3])cube([39,42,83]);
  for(x=[53,86])for(y=[39,75])translate([x,y,0])pier(94,8);
  translate([51,37,80])cube([43,46,5]);
  translate([55,43,85])cube([35,34,6]);
 }
 // Upper gallery: wide continuous passage; its crown remains visible.
 translate([73,51,56])rotate([0,0,90])fenestration(24,50,27);
 // Lower gallery stays visible through a generous machine-hall opening.
 translate([73,63,16])rotate([0,0,90])fenestration(29,50,29);
 // Courtyard cutaway gives access from above and preserves heavy side walls.
 translate([62,56,43])cube([21,18,48]);
 }
 for(x=[54,89])for(z=[8:12:77])translate([x,38,z])cube([2.5,2,6]);
 // Side-facing mechanical rosettes are fixed, decorative geometry.
 for(x=[52.5,92.5])translate([x,70,56])rotate([0,90,0]){
  annulus(9,6.8,1.8);
  for(a=[0:30:330])rotate([0,0,a])translate([7.5,-1,0])cube([3,2,1.8]);
  cylinder(r=3,h=2.3,$fn=8);
  for(a=[0:60:300])rotate([0,0,a])translate([0,-.8,.2])cube([8,1.6,1.4]);
 }
}
module armillary(){
 // The richer earlier aesthetic: fixed teeth, reticle, cradle and two rings.
 translate([72,72,91]){
  cylinder(r1=11,r2=8,h=8,$fn=12);
  translate([0,0,6])annulus(16,11,3);
  for(a=[0:30:330])rotate([0,0,a])translate([14,-1.6,6])cube([4,3.2,3]);
 }
 for(x=[55,89])translate([x,69,88])cube([5,6,26]);
 translate([72,72,113]){
  rotate([90,0,0])torus(19,2);
  rotate([44,12,0])torus(16.5,1.7);
  rotate([0,90,0])cylinder(r=1.8,h=39,center=true,$fn=12);
  sphere(r=5.2,$fn=8);
  for(a=[0:30:330])rotate([90,0,0])rotate([0,0,a])translate([18.2,-1.2,-1.4])cube([3,2.4,2.8]);
 }
}
module receiver(){
 // Entry floor is 0.2 mm lower than the final conduit. No uphill exit lip.
 translate([118,76,3])cylinder(r1=18,r2=15.5,h=12,$fn=12);
 difference(){
  translate([118,76,14])cylinder(r=16.4,h=22,$fn=48);
  translate([118,76,17.8])cylinder(r=13.6,h=24,$fn=64);
  translate([99,70.8,17.75])cube([20,10.4,24]);
 }
 for(a=[-45,0,45,90,135,225,270])translate([118,76,3])rotate([0,0,a])
  translate([15,-1.2,0])cube([3.5,2.4,25]);
 translate([118,76,13])annulus(17.2,14,2.1);
}
// Generated support/spine arrangement keeps every abutment out of lower runs.
include <supports.scad>
module architecture(){difference(){union(){launch_keep();large_masses();machine_hall();armillary();radial_arms();aqueducts();}route_air();}}
module complete(){union(){foundation();trough();architecture();receiver();support_system();}}
if(part=="track")trough();
else if(part=="marble")translate([0,0,4])sphere(d=8,$fn=96);
else if(part=="architecture"){foundation();architecture();receiver();support_system();}
else complete();
