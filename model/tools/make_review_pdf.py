"""Seven-page review with actual assembly renders, instructions and measured checks."""
import json
from PIL import Image,ImageDraw
from assembly_model import ROOT
from render_common import font
W,H=1600,2263;BG=(18,29,39);INK=(239,226,194);MUTED=(170,193,193)
def paragraph(d,text,x,y,width=1440,size=26,color=INK):
 f=font(size);line=''
 for word in text.split():
  s=(line+' '+word).strip()
  if line and d.textlength(s,font=f)>width:d.text((x,y),line,font=f,fill=color);y+=size+12;line=word
  else:line=s
 if line:d.text((x,y),line,font=f,fill=color);y+=size+12
 return y
def foot(d,n):
 d.line((70,2168,1530,2168),fill=(62,84,91),width=2)
 d.text((70,2200),'PRISM OBSERVATORY · Designed and modeled by Yonathan · 18 October 2026',font=font(21),fill=MUTED)
 d.text((1480,2200),str(n),font=font(22),fill=MUTED)
def pic(page,name,box):
 im=Image.open(ROOT/'renders'/name);im.thumbnail((box[2],box[3]),Image.Resampling.LANCZOS)
 page.paste(im,(box[0]+(box[2]-im.width)//2,box[1]+(box[3]-im.height)//2))
def new(title):
 p=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(p);d.text((70,50),title,font=font(40,True),fill=INK);return p,d
def main():
 mesh=json.loads((ROOT/'verification/topology-report.json').read_text());motion=json.loads((ROOT/'verification/fit-and-motion-report.json').read_text())
 ball=json.loads((ROOT/'verification/marble-space-report.json').read_text());mechanics=json.loads((ROOT/'verification/mechanical-estimates.json').read_text())
 pages=[];p=Image.new('RGB',(W,H),BG);pic(p,'full-assembly.png',(0,0,1600,1760));d=ImageDraw.Draw(p)
 y=paragraph(d,'A STAR CHOOSES ITS DESCENT',70,1790,size=33)
 y=paragraph(d,'Set the manual selector. One branch spirals through a funnel; the other loads a tipping cup. Both return to the shared hall, descend through three staggered trays and two guarded drops, then arrive at the front collector.',70,y+10,size=26)
 paragraph(d,'Carved hall niches, broken stonework, celestial runes, prominent conduits and an armillary crest tell the Observatory story. Designed and modeled by Yonathan; nominal 8 mm PRINTED marble and 144 mm square base.',70,y+15,size=24,color=MUTED)
 foot(d,1);pages.append(p)
 p=Image.new('RGB',(W,H),BG);pic(p,'observatory-character.png',(0,30,1600,1730));d=ImageDraw.Draw(p)
 d.text((70,1790),'A RUINED INSTRUMENT HOUSE',font=font(34,True),fill=INK)
 y=paragraph(d,'The machinery is held inside dressed-stone towers and a carved machine hall. Recessed celestial runes mark the bowl; lancets and a broken survey pillar suggest the remaining ruins. Raised conduits and a fixed service gauge connect the lower architecture. The richer armillary crest remains above the manual selector.',70,1850,size=25)
 paragraph(d,'These details are modeled in CAD. The mechanisms and route retain their approved layout. Fixed sculpture has no powered effects. Mesh, sampled motion and marble-space checks were repeated after the additions.',70,y+15,size=24,color=MUTED)
 foot(d,2);pages.append(p)
 p=Image.new('RGB',(W,H),BG);pic(p,'mechanism-details.png',(20,10,1560,2070));d=ImageDraw.Draw(p)
 paragraph(d,'Inspection crops hide some fixed context. Shown poses explain the mechanism; rolling, tipping and empty reset remain physically untested.',70,2070,size=23,color=MUTED)
 foot(d,3);pages.append(p)
 p=Image.new('RGB',(W,H),BG);pic(p,'print-parts.png',(30,0,1540,2110));d=ImageDraw.Draw(p)
 paragraph(d,'Use the separate part meshes. The assembled STL is for viewing only. Parts have individual scales in this sheet.',70,2105,size=22,color=MUTED)
 foot(d,4);pages.append(p)
 p,d=new('ASSEMBLY / DRY-FIT BEFORE PRINT COMMITMENT');y=145
 steps=[
 ('1  Coupon and surface finish','Print the fit coupon first. The notched front-left corner identifies its rows: Y=9 gives 1.8/1.95/2.1/2.25/2.4 mm holes; Y=21 gives 3.2/3.4/3.6/5.0/5.2/5.4 mm holes, increasing left to right. Test your actual axle and pegs.'),
 ('2  Cascade and service rails first','Leave funnel and selector off. Hold cascade 35 mm forward and 68 mm above its seat; slide rearward 35 mm, then lower onto four pegs at X72,Y42,Z3. Hold collector ramp 6 mm high and 20 mm right, slide left, then lower. Lower the approach bridge onto its three pier keys. The marble course retains its approved layout.'),
 ('3  Funnel and manual selector','Lower the funnel at X38,Y104,Z3, aligned with branch A. Then place the selector stem at X75.5,Y116. Its 4.6 mm stem fits a nominal 5.0 mm bearing. Align 225 degrees for A or 135 degrees for B; position before feeding. For removal: selector, funnel, bridge, ramp, then cascade; reverse the installation motions.'),
 ('4  Capture the cup axle','Cup bowl faces forward; counterweight fork faces rearward. Axle centre: X115.411,Y104,Z114. Thread a nominal 1.75 x 18.8 mm axle through posts and cup. Fit two retainers outside the posts. Never force a brittle retainer. Verify free motion and positive retention.'),
 ('5  Fit and tune the counterweight','Slide the regular carrier into the rear fork, with its neck and underside flange straddling the lever. Fit the endclip. Begin with the carrier centre 9.7 mm behind the axle; reviewed range 9.5–10.5 mm. Secure a loose clip/slider with a small removable tape tab outside contact surfaces.'),
 ('6  Feed one solid printed marble','Use a nominal 8 mm PLA printed marble, initially 100% infill. Weigh and measure it. The ideal solid ball is about 0.33 g. A lighter ball may need the optional light carrier or manual reset. Do not install both weights together. No glass/steel substitution is assumed.')]
 for title,text in steps:
  d.text((70,y),title,font=font(28,True),fill=INK);y+=48;y=paragraph(d,text,70,y,size=25);y+=28
 paragraph(d,'Full instructions, dimensions and reproduction commands are in START-HERE.txt. Dry-fit all seats; tune with measured masses and your actual print tolerances.',70,y+10,size=25,color=MUTED)
 foot(d,5);pages.append(p)
 p,d=new('MEASURED DIGITAL CHECKS');y=145
 rows=[('Printable meshes',f'{len(mesh["parts"])} / {len(mesh["parts"])} topology checks: '+('PASS' if mesh['passed'] else 'REVIEW REQUIRED')),
 ('Mesh conditions','One closed connected solid each; oriented edges; no degenerate faces'),
 ('Envelope','144 x 144 x 149.8 mm chassis; 3 mm foundation'),
 ('Stationary assembly','Funnel/chassis, cascade/chassis and module/module surface crossings: '+('PASS' if all(v['passed'] for v in motion['stationary_fit'].values()) else 'REVIEW REQUIRED')),
 ('Sampled motion',f'{len(motion["cup_poses"])} cup + {len(motion["ballast_poses"])} carrier + {len(motion["selector_poses"])} selector interior poses: '+('PASS' if motion['passed'] else 'REVIEW REQUIRED')),
 ('Assembly / removal',f'{len(motion["module_lift_poses"])} reversible path poses; keyed seats and ten fixed-part pairs'),
 ('Marble envelopes',f'{ball["samples"]:,} static 8 mm sphere probes: '+('PASS' if ball['passed'] else 'REVIEW REQUIRED')),
 ('Gravity estimate','Ideal solid-PLA loading/restoring signs: '+('PASS' if mechanics['passed_idealized_gravity_signs'] else 'REVIEW REQUIRED'))]
 for k,v in rows:
  d.text((70,y),k,font=font(25,True),fill=INK);y=paragraph(d,v,420,y,width=1100,size=24)+22
 y=paragraph(d,'The marble screen covers both selector interfaces, all six fixed tracks with +/-0.6 mm lateral offsets, bowl/throat, cup loading and release construction, both merge approaches, cascade inlet, two guarded drops, final outlet and collector. Sphere contact heights are solved against exported triangles.',70,y+5,size=25)
 y=paragraph(d,'A 0.04 mm contact offset is an analysis construction, not manufacturing clearance. Spiral and falling paths are geometric possibilities, not predicted trajectories. Motion uses noncoplanar surface crossings at 1-degree samples. Five keyed seats were measured from actual meshes; shared-plane contacts within 0.0002 mm are recorded as export precision. Continuous-time forces, printer fit and wear are not certified.',70,y+15,size=24,color=MUTED)
 pic(p,'full-assembly-clay.png',(400,y+15,800,2140-y-25));foot(d,6);pages.append(p)
 p,d=new('PRINT REVIEW / PHYSICAL TESTS STILL REQUIRED');y=145
 blocks=[('Slicing and supports','Print at 100% scale. Check thin 0.8 mm cup walls survive slicing. Keep all channels open upward. Elevated chassis rails, tall funnel legs, the cup hub and selector stem need a deliberate support/adhesion strategy. Inspect every layer and removal access. No sliced profile, G-code, print-time estimate or completed print is supplied.'),
 ('Mechanism validation','Nominal cup stops: -5 degrees rest, +55 degrees dump. The low, broad carrier gives the intended gravity signs in the ideal calculation, including empty return. It ignores axle friction, actual infill/density, impacts and wear. Weigh parts, tune balance and test triggering, release, retention and reset. Automatic operation is not proven.'),
 ('Test in stages','On a level surface, feed one ball slowly. Check each selector exit, funnel circulation and throat, cup loading/release, both merge approaches, each guarded drop, final feed and collector. Stop after any stall or escape. Record actual observations and revise the CAD/finish as necessary. Static clearance does not prove rolling speed, bounce or retention.'),
 ('Authorship and programme status','Designed and modeled by Yonathan. Earlier revisions are preserved. Physical printing and rolling tests remain pending. Programme acceptance is not claimed.'),
 ('Included evidence','Editable OpenSCAD, generated route data, 14 separate STL designs, 8 mm ball, fit coupon, raw chassis export and precision-cleanup report, assembly placement manifest, exact probe CSV/JSON, motion/topology and assembly-path reports, source rendering tools and this PDF. The repository is public. No physical print or rolling test has been completed; final programme submission remains pending.')]
 for title,text in blocks:
  d.text((70,y),title,font=font(29,True),fill=INK);y+=48;y=paragraph(d,text,70,y,size=25);y+=27
 paragraph(d,'Guide: github.com/karnxx/merbl/blob/main/guide.md#marble. Mechanism references: Woodgears marble elements/flip-flop and Out Of Marbles funnel/bucket descriptions; no commercial CAD geometry copied.',70,y+5,size=22,color=MUTED)
 foot(d,7);pages.append(p)
 dest=ROOT/'Prism-Observatory-Review.pdf';pages[0].save(dest,save_all=True,append_images=pages[1:],resolution=193.5,
  title='The Last Observatory / Prism Machine — CAD by Yonathan',author='Yonathan',subject='Separate-part CAD, manual split, funnel, tipping cup, guarded cascade, assembly and digital checks')
 print(dest,flush=True)
if __name__=='__main__':main()
