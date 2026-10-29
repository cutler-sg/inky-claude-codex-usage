// Inky Impression 5.7 desk stands. Units: mm. Concept geometry, not fit validated.
// Set show_display=false and show_cable=false to inspect/export the stand alone.
concept = 1; // [1:Wedge, 2:Twin fins, 3:Open triangle, 4:Pebble cradle]
show_display = true;
show_cable = true;
lean = 12; // Degrees back from vertical.
slot_width = 5.2; // Provisional lower-edge envelope incl. clearance, NOT the 9mm header depth.
cable_width = 8;
support_spacing = 86;
seat_height = 9;
$fn = 48;

module panel_space() { translate([0,12,seat_height]) rotate([-lean,0,0]) children(); }
module side_extrude(width) {
    // Local profile X/Y becomes world Y/Z; extrusion becomes world X.
    multmatrix([[0,0,1,-width/2],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
        linear_extrude(width) children();
}
module rounded_base(width,depth,height,r=4) {
    linear_extrude(height) hull()
        for(x=[-width/2+r,width/2-r],y=[r,depth-r]) translate([x,y]) circle(r);
}
module slot_cut() {
    panel_space() translate([-70,-slot_width/2,0]) cube([140,slot_width,130]);
}
module ribbon_relief() {
    // Central ribbon is visible in the vendor photo; 36mm is a provisional keep-out.
    translate([-18,-2,4]) cube([36,46,40]);
}
module cable_cut(depth=78) {
    // Open underside channel; drop the cable in instead of threading its connector.
    translate([-cable_width/2,24,-1]) cube([cable_width,depth,5]);
    translate([-cable_width/2,42,-1]) cube([cable_width,14,45]);
}
module wedge() {
    difference() {
        union() {
            rounded_base(112,72,6);
            side_extrude(108) polygon([[3,5],[3,14],[23,32],[67,5]]);
        }
        slot_cut(); ribbon_relief(); cable_cut();
    }
}
module fin(width=14,open=false) {
    difference() {
        side_extrude(width) polygon([[0,0],[0,14],[22,40],[76,0]]);
        if(open) side_extrude(width+2) polygon([[26,11],[28,28],[52,11]]);
    }
}
module twins() {
    difference() {
        union() {
            for(x=[-support_spacing/2,support_spacing/2]) translate([x,0,0]) fin();
            translate([-support_spacing/2,61,0]) cube([support_spacing,10,7]);
        }
        slot_cut(); cable_cut();
    }
}
module triangle() {
    difference() {
        union() {
            for(x=[-support_spacing/2,support_spacing/2]) translate([x,0,0]) fin(8,true);
            translate([-support_spacing/2,64,0]) cube([support_spacing,9,7]);
            translate([-support_spacing/2,2,0]) cube([support_spacing,7,5]);
        }
        slot_cut(); ribbon_relief(); cable_cut();
    }
}
module cradle() {
    difference() {
        union() {
            rounded_base(116,66,7,9);
            for(x=[-support_spacing/2,support_spacing/2]) translate([x,0,0])
                side_extrude(18) polygon([[3,6],[3,14],[19,25],[40,6]]);
        }
        slot_cut(); ribbon_relief(); cable_cut();
    }
}
module stand() {
    difference() {
        union() {
            if(concept==1) wedge();
            if(concept==2) twins();
            if(concept==3) triangle();
            if(concept==4) cradle();
        }
        // Keep front lips below the active image; no tall clamp over the glass.
        panel_space() translate([-70,-50,4]) cube([140,50-slot_width/2+0.1,130]);
    }
}
module display_reference() {
    // Only outline and active-area dimensions are sourced. Thickness, Pi placement
    // and ports are illustrative envelopes; measure actual assembly before fitting.
    panel_space() {
        color("#242b2d") difference() {
            translate([-62.7,0,0]) cube([125.4,1.6,99.5]);
            translate([-13,-1,-1]) cube([26,4,13]);
        }
        color("#33393a") translate([-61,-1.6,3]) cube([122,1.6,95]);
        color("#f4f1e5") translate([-57.45,-1.8,8]) cube([114.9,0.2,85.8]);
        // Quiet graphic so the stand silhouette remains the focus.
        color("#dd5d39") translate([-47,-2,20]) cube([25,0.2,61]);
        color("#31556a") translate([-17,-2,20]) cube([31,0.2,42]);
        color("#e9b438") translate([19,-2,20]) cube([28,0.2,22]);
        for(z=[19.83,41.28,62.73,84.18])
            color("#aaaaaa") translate([-64.2,0,z-2.5]) cube([1.5,3,5]);
        color("#b77824") translate([-12,1.7,0]) cube([24,0.5,14]);
        color("#20272a") translate([-24,2,68]) cube([51,8,5]);
        color("#36775f") translate([-30,10,40]) cube([65,1.6,30]);
        color("#bfc4c6") translate([-18,11.6,39]) cube([8,3,5]);
    }
}
module segment(a,b,r=1.8) { hull() { translate(a) sphere(r); translate(b) sphere(r); } }
module cable_reference() {
    // Illustrative loose sweep from the Pi's downward-facing USB to rear channel.
    pts=[[-14,33,48],[-14,39,37],[0,40,28],[0,47,15],[0,52,2],[0,80,2],[0,94,2]];
    color("#343b40") for(i=[0:len(pts)-2]) segment(pts[i],pts[i+1]);
}

color("#b7c4c9") stand();
if(show_display) display_reference();
if(show_cable) cable_reference();
