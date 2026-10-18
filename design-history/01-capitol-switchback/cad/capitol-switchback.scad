// Capitol Switchback — designed and modeled by Yonathan.
// Designed and modeled by Yonathan.
// No physical print/roll test or program eligibility is claimed.
// Units: millimetres. Run the course in the displayed orientation.
// Command-line STL: openscad -D 'part="course"' -o course.stl this-file.scad

part = "course";                 // [course,marble,assembly]
base_size = 140;
base_thickness = 3;
base_corner_radius = 6;
marble_diameter = 8;
channel_diameter = 9.6;          // 1.6 mm diametral clearance
wall = 2.4;
guard_height = 11;              // measured from the rolling floor
bend_radius = 21;
floor_start = 48;
floor_end = 16;
support_radius = 3.5;
support_pitch = 23;
path_step = 1.5;
arc_facets = 28;
$fn = 64;

ri = channel_diameter/2;
ro = ri + wall;
x_left = 31;
x_right = 109;
y_first = 28;
y_second = y_first + 2*bend_radius;
y_last = y_second + 2*bend_radius;
x_start = 20;
x_end = 108;
length_1 = x_right-x_start;
length_2 = PI*bend_radius;
length_3 = x_right-x_left;
length_4 = PI*bend_radius;
length_5 = x_end-x_left;
course_length = length_1+length_2+length_3+length_4+length_5;
drop = floor_start-floor_end;

// Return [x,y,floor_z,tangent_x,tangent_y]. Exact tangent joins,
// with height decreasing linearly with cumulative horizontal arc length.
function centerline(s) =
    s <= length_1 ?
        [x_start+s,y_first,floor_start-drop*s/course_length,1,0] :
    s <= length_1+length_2 ?
        let(a=-90+(s-length_1)/bend_radius*180/PI)
        [x_right+bend_radius*cos(a),y_first+bend_radius+bend_radius*sin(a),
         floor_start-drop*s/course_length,-sin(a),cos(a)] :
    s <= length_1+length_2+length_3 ?
        [x_right-(s-length_1-length_2),y_second,
         floor_start-drop*s/course_length,-1,0] :
    s <= length_1+length_2+length_3+length_4 ?
        let(a=-90-(s-length_1-length_2-length_3)/bend_radius*180/PI)
        [x_left+bend_radius*cos(a),y_second+bend_radius+bend_radius*sin(a),
         floor_start-drop*s/course_length,sin(a),-cos(a)] :
        [x_left+(s-length_1-length_2-length_3-length_4),y_last,
         floor_start-drop*s/course_length,1,0];

// An upright U with rounded floor and tall open guard walls.
// The outer arc is a true offset of the inner arc, giving 2.4 mm walls.
profile = concat(
    [[-ri,guard_height]],
    [for(i=[0:arc_facets]) let(a=180+i*180/arc_facets)
        [ri*cos(a),ri+ri*sin(a)]],
    [[ri,guard_height],[ro,guard_height]],
    [for(i=[0:arc_facets]) let(a=360-i*180/arc_facets)
        [ro*cos(a),ri+ro*sin(a)]],
    [[-ro,guard_height]]
);

// Include every exact segment boundary in the sweep, eliminating joins/gaps.
function stations_segment(offset, length) =
    let(n=ceil(length/path_step)) [for(i=[0:n-1]) offset+length*i/n];
stations = concat(stations_segment(0,length_1),
    stations_segment(length_1,length_2),
    stations_segment(length_1+length_2,length_3),
    stations_segment(length_1+length_2+length_3,length_4),
    stations_segment(length_1+length_2+length_3+length_4,length_5),
    [course_length]);
np = len(profile);
ns = len(stations);
sweep_points = [for(s=stations) let(p=centerline(s))
    for(q=profile) [p[0]-p[4]*q[0],p[1]+p[3]*q[0],p[2]+q[1]]];
sweep_faces = concat(
    [[for(j=[0:np-1]) j]],
    [for(i=[0:ns-2]) for(j=[0:np-1]) each
        [[i*np+j,(i+1)*np+j,(i+1)*np+(j+1)%np],
         [i*np+j,(i+1)*np+(j+1)%np,i*np+(j+1)%np]]],
    [[for(j=[np-1:-1:0]) (ns-1)*np+j]]
);

module rounded_base() {
    linear_extrude(height=base_thickness)
        translate([base_corner_radius,base_corner_radius])
            offset(r=base_corner_radius)
                square([base_size-2*base_corner_radius,
                        base_size-2*base_corner_radius]);
}

module trough() {
    polyhedron(points=sweep_points, faces=sweep_faces, convexity=12);
}

module columns() {
    // These are retained structural parts, connected below the rolling floor.
    n=ceil(course_length/support_pitch);
    for(i=[0:n]) let(p=centerline(course_length*i/n))
        translate([p[0],p[1],base_thickness-0.2])
            cylinder(r=support_radius,
                     h=p[2]-1-(base_thickness-0.2));
}

module entry_stop() {
    // Backstop only; the open top receives the marble by hand.
    translate([x_start-wall,y_first-ro,floor_start-wall])
        cube([wall+0.3,2*ro,guard_height+wall]);
}

module catch_tray() {
    tray_x = 116;
    tray_y = y_last;
    tray_floor = 14.6;
    tray_inner_radius = 10.5;
    tray_outer_radius = tray_inner_radius+wall;
    tray_bottom = tray_floor-wall;
    tray_top = 26.5;
    translate([tray_x,tray_y,base_thickness-0.2])
        cylinder(r=6.5,h=tray_bottom-base_thickness+0.6);
    difference() {
        translate([tray_x,tray_y,tray_bottom])
            cylinder(r=tray_outer_radius,h=tray_top-tray_bottom);
        translate([tray_x,tray_y,tray_floor])
            cylinder(r=tray_inner_radius,h=tray_top-tray_floor+1);
        // The entry slot removes the wall across the complete rolling channel.
        translate([99,tray_y-ri,tray_floor])
            cube([10,2*ri,tray_top-tray_floor+1]);
    }
}

module course() {
    assert(base_size<150 && base_thickness<4);
    assert(marble_diameter<channel_diameter);
    assert(bend_radius>12 && bend_radius>ro);
    assert(floor_start>floor_end);
    union() {
        rounded_base();
        trough();
        columns();
        entry_stop();
        catch_tray();
    }
}

if(part=="marble") translate([0,0,marble_diameter/2]) sphere(d=marble_diameter,$fn=96);
else if(part=="assembly") {
    color([0.10,0.47,0.46]) course();
    p=centerline(12);
    color([0.97,0.64,0.20])
        translate([p[0],p[1],p[2]+marble_diameter/2+0.05])
            sphere(d=marble_diameter,$fn=96);
} else course();
