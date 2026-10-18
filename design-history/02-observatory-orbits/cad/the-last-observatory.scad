// THE LAST OBSERVATORY — designed and modeled by Yonathan.
// A fallen star follows the broken orbital conduit to the energy chamber.
// Designed and modeled by Yonathan.
// No copied figure, traced artwork, or copied reference track layout.
// Units mm. No print, rolling test, submission or program eligibility claimed.

part = "complete"; // [complete,marble,assembly,track]
base_size = 144;
base_thickness = 3;
center_x = 72;
center_y = 72;
marble_diameter = 8;
channel_diameter = 9.6;
wall = 2.4;
guard_height = 13;
inner_guard_height = 9.2;
orbit_radius = 57;
orbit_wobble = 3;
orbit_turns = 2;
start_angle = -55;
floor_start = 96;
floor_end = 18.4;
basin_floor = 16.8;
orbit_segments = 480;
bridge_segments = 90;
bridge_reach = 23;
bridge_control_x = 120;
profile_facets = 24;
$fn = 40;

ri = channel_diameter/2;
ro = ri+wall;
function unit(v) = v/norm(v);
function orbit_r(u) = orbit_radius+orbit_wobble*sin(720*orbit_turns*u);
function orbit_xy(u) = let(a=start_angle+360*orbit_turns*u,r=orbit_r(u))
    [center_x+r*cos(a),center_y+r*sin(a)];
function orbit_tangent(u) =
    let(a=start_angle+360*orbit_turns*u,r=orbit_r(u),dr=2*orbit_wobble*cos(720*orbit_turns*u))
        unit([dr*cos(a)-r*sin(a),dr*sin(a)+r*cos(a)]);
b0=orbit_xy(1);
b1=b0+bridge_reach*orbit_tangent(1);
b2=[bridge_control_x,72];
b3=[84,72];
function bridge_xy(t) = pow(1-t,3)*b0+3*pow(1-t,2)*t*b1+3*(1-t)*t*t*b2+t*t*t*b3;
function bridge_tangent(t) = unit(3*pow(1-t,2)*(b1-b0)+6*(1-t)*t*(b2-b1)+3*t*t*(b3-b2));
xy_path = concat([for(i=[0:orbit_segments]) orbit_xy(i/orbit_segments)],
                 [for(i=[1:bridge_segments]) bridge_xy(i/bridge_segments)]);
tangents = concat([for(i=[0:orbit_segments]) orbit_tangent(i/orbit_segments)],
                  [for(i=[1:bridge_segments]) bridge_tangent(i/bridge_segments)]);
function accumulated(p,i=1,out=[0]) = i>=len(p) ? out :
    accumulated(p,i+1,concat(out,[out[len(out)-1]+norm(p[i]-p[i-1])]));
stations = accumulated(xy_path);
path_length = stations[len(stations)-1];
function floor_z(s) = floor_start-(floor_start-floor_end)*s/path_length;
function station_at_orbit(u) =
    let(v=u*orbit_segments,i=min(floor(v),orbit_segments-1),f=v-i)
        stations[i]*(1-f)+stations[i+1]*f;
function orbit_floor(u) = floor_z(station_at_orbit(u));

profile = concat([[-ri,guard_height]],
    [for(i=[0:profile_facets]) let(a=180+i*180/profile_facets)
        i==0?[-ri,ri]:i==profile_facets?[ri,ri]:[ri*cos(a),ri+ri*sin(a)]],
    [[ri,inner_guard_height],[ro,inner_guard_height]],
    [for(i=[0:profile_facets]) let(a=360-i*180/profile_facets)
        i==0?[ro,ri]:i==profile_facets?[-ro,ri]:[ro*cos(a),ri+ro*sin(a)]],
    [[-ro,guard_height]]);
np=len(profile);
ns=len(xy_path);
sweep_points=[for(i=[0:ns-1]) let(p=xy_path[i],t=tangents[i],z=floor_z(stations[i]))
    for(q=profile) [p[0]-t[1]*q[0],p[1]+t[0]*q[0],z+q[1]]];
// Triangulated caps avoid ambiguous concave end polygons.
cap_faces=concat([[0,1,np-2],[0,np-2,np-1]],
    [[profile_facets+1,profile_facets+2,profile_facets+3],
     [profile_facets+1,profile_facets+3,profile_facets+4]],
    [for(i=[0:profile_facets-1])each
      [[1+i,2+i,2*profile_facets+3-i],
       [1+i,2*profile_facets+3-i,2*profile_facets+4-i]]]);
sweep_faces=concat(cap_faces,
    [for(i=[0:ns-2]) for(j=[0:np-1]) each
       [[i*np+j,(i+1)*np+j,(i+1)*np+(j+1)%np],
        [i*np+j,(i+1)*np+(j+1)%np,i*np+(j+1)%np]]],
    [for(f=cap_faces)[for(j=[2:-1:0])(ns-1)*np+f[j]]]);

module xy_at(p,t) { translate([p[0],p[1],0]) rotate([0,0,atan2(t[1],t[0])]) children(); }
module torus(r,tube,angle=360) { rotate_extrude(angle=angle,$fn=96) translate([r,0]) circle(r=tube,$fn=12); }
module annulus(r1,r2,h) { difference(){cylinder(r=r1,h=h);translate([0,0,-0.1])cylinder(r=r2,h=h+0.2);} }

module foundation() {
    difference() {
        linear_extrude(height=base_thickness)
            translate([6,6])offset(r=6)square([base_size-12,base_size-12]);
        // Observatory survey rings and floor joints, engraved into real geometry.
        for(r=[28,33,66]) translate([center_x,center_y,base_thickness-0.4])annulus(r+0.45,r-0.45,0.6);
        for(a=[0:30:330]) translate([center_x,center_y,base_thickness-0.4])
            rotate([0,0,a])translate([35,-0.4,0])cube([28,0.8,0.6]);
        for(p=[[11,11],[133,11],[11,133],[133,133]])
            translate([p[0],p[1],base_thickness-0.45])linear_extrude(height=0.6)
                polygon([[-3,0],[0,-5],[3,0],[0,5]]);
    }
}

module trough() {polyhedron(points=sweep_points,faces=sweep_faces,convexity=20);}

module masonry_pier(height,width=8) {
    // Continuous core holds separated masonry courses together.
    cylinder(r=width*0.34,h=height,$fn=8);
    cube([width+3,width+3,3],center=true);
    for(z=[1:8:height-3]) translate([0,0,z])
        linear_extrude(height=min(7.5,height-z))
            offset(r=0.6)square([width-1.2,width-1.2],center=true);
    // Offset both cap faces from the radial beam faces to avoid coplanar seams.
    translate([0,0,height-1.7])cube([width+2.5,width+2.5,4.8],center=true);
}

module orbital_arcade() {
    // Seven inner piers leave the bridge approach open. Radial arms stay below
    // the trough floor; the piers stay inside its entire rolling envelope.
    for(a=[22.5:45:292.5]) let(u=((a-start_angle+360)%360)/(360*orbit_turns),
                               p=orbit_xy(u),z=orbit_floor(u)) {
        translate([center_x+39*cos(a),center_y+39*sin(a),base_thickness-0.15])
            masonry_pier(z-1-base_thickness+0.15,7.4);
        for(v=[u,u+1/orbit_turns]) let(q=orbit_xy(v),fz=orbit_floor(v),r=orbit_r(v))
            translate([center_x,center_y,0])rotate([0,0,a])
                translate([38,-2.5,fz-5])cube([r-38+0.8,5,4]);
    }
    // A buttress at the broken beacon supports both corresponding orbital levels.
    a=start_angle;
    translate([center_x+40*cos(a),center_y+40*sin(a),base_thickness-0.15])
        masonry_pier(floor_start-1-base_thickness+0.15,8.5);
    for(u=[0,0.5]) let(fz=orbit_floor(u),r=orbit_r(u))
        translate([center_x,center_y,0])rotate([0,0,a])
            translate([39,-3,fz-5])cube([r-39+0.8,6,4]);
}

module beacon() {
    xy_at(xy_path[0],tangents[0]) {
        translate([-wall,-ro-0.25,floor_start-wall])cube([wall+0.45,2*ro+0.5,guard_height+wall]);
        for(q=[-12,12]) let(h=floor_start+(q<0?18:12))
            translate([0,q,base_thickness-0.15]) {
                cylinder(r=2.9,h=h-base_thickness+0.15,$fn=8);
                translate([0,0,h-base_thickness-3])cylinder(r1=4,r2=2,h=4,$fn=8);
            }
    }
}

module bridge_gate() {
    t=0.60;
    p=bridge_xy(t);
    // Height interpolated from the real tessellated stations.
    i=orbit_segments+round(t*bridge_segments);
    fz=floor_z(stations[i]);
    xy_at(p,bridge_tangent(t)) {
        // The opening is 20 mm wide and reaches 23 mm above the rolling floor.
        for(q=[-11.5,11.5])
            translate([-2.8,q-1.5,base_thickness-0.1])cube([5.6,3,fz+13-base_thickness+0.2]);
        multmatrix([[0,0,1,0],[1,0,0,0],[0,1,0,fz+13],[0,0,0,1]])
            linear_extrude(height=5.6,center=true)
                intersection(){difference(){circle(r=13);circle(r=10);}translate([-14,0])square([28,14]);}
        for(q=[-11.5,11.5])translate([-3.7,q-2.4,fz+10.5])cube([7.4,4.8,2.5]);
    }
}

module energy_chamber() {
    translate([center_x,center_y,base_thickness-0.15])cylinder(r=9,h=basin_floor-wall-base_thickness+0.45);
    difference() {
        translate([center_x,center_y,basin_floor-wall])cylinder(r=15.4,h=13.4);
        translate([center_x,center_y,basin_floor])cylinder(r=13,h=15);
        translate([center_x+10,center_y-ri,basin_floor])cube([12,2*ri,16]);
    }
    // Four low radial fins read as an inert energy receiver, without electronics.
    for(a=[45:90:315])translate([center_x,center_y,0])rotate([0,0,a])
        translate([15,-1.2,base_thickness-0.1])cube([7,2.4,basin_floor+7-base_thickness]);
}

module central_observatory() {
    // An open four-pier instrument tower: the chamber is accessible below.
    translate([center_x,center_y,base_thickness-0.1])cylinder(r=27,h=2.1,$fn=12);
    for(dx=[-18,18])for(dy=[-18,18])
        translate([center_x+dx,center_y+dy,base_thickness])masonry_pier(71,7);
    // Fractured crown; its gaps reveal the open observatory, not a copied facade.
    translate([center_x,center_y,69])difference(){
        annulus(25.5,20.5,9);
        rotate([0,0,18])translate([-3,18,4])cube([11,15,8]);
        rotate([0,0,196])translate([-4,19,6])cube([12,15,6]);
    }
    translate([center_x,center_y,78]) {
        for(a=[45,135,225,315])rotate([0,0,a])translate([23,-1.5,-1])cube([3,3,5]);
    }
    // Retained gimbal cradle physically joins the low point of the instrument
    // to both sides of the stone crown; the celestial rings do not float.
    translate([center_x-24,center_y-3,75])cube([48,6,4]);
    // Original damaged armillary: two intersecting celestial rings and a fixed
    // stellar core on a real axle. The core is scenery, not the rolling marble.
    translate([center_x,center_y,99]) {
        rotate([90,0,0])rotate([0,0,15])torus(23,2.1,300);
        rotate([47,0,0])torus(20,1.8);
        rotate([0,90,0])cylinder(r=1.8,h=48,center=true,$fn=16);
        sphere(r=5.6,$fn=24);
        for(a=[[0,0,0],[180,0,0],[0,90,0],[0,-90,0],[90,0,0],[-90,0,0]])
            rotate(a)translate([0,0,3.5])cylinder(r1=3.4,r2=1.1,h=6.3,$fn=8);
    }
}

module bridge_supports() {
    // Short supports for the interior bridge, separate from the orbit piers.
    for(t=[0.27,0.52,0.80])let(p=bridge_xy(t),i=orbit_segments+round(t*bridge_segments),z=floor_z(stations[i]))
        translate([p[0],p[1],base_thickness-0.1])cylinder(r=3.2,h=z-1-base_thickness+0.1,$fn=12);
}

module complete() {
    assert(base_size<150 && base_thickness<4);
    assert(marble_diameter<channel_diameter);
    union(){foundation();trough();orbital_arcade();beacon();bridge_gate();
        bridge_supports();energy_chamber();central_observatory();}
}

if(part=="marble")translate([0,0,marble_diameter/2])sphere(d=marble_diameter,$fn=96);
else if(part=="track")trough();
else if(part=="assembly") {
    complete();
    p=xy_path[5];translate([p[0],p[1],floor_z(stations[5])+4.05])sphere(d=8,$fn=64);
} else complete();
