"""Constructed STATIC 8 mm sphere envelopes through every assembled transition.

These are geometric probes, not predictions of travel, bounce, friction or tipping.
Contact heights are solved against the actual exported upward-facing triangles.
"""
import csv,hashlib,json,math
import numpy as np
from assembly_model import loaded,placed,ROOT,rx
from machine_geometry import routes,O,ROTOR_Z,TIP,F,CASCADE
from mesh_queries import Queries

def main():
 parts=loaded();scenes={n:placed(parts,s,a) for n,s,a in [('A',225,-5),('B',135,-5),('dump',135,55)]}
 query={n:Queries(np.concatenate(list(sc.values()))) for n,sc in scenes.items()}
 probes=[];support_gaps=[]
 def put(group,p,pose='A',note='constructed static envelope'):
  p=np.array(p,float);q=query[pose];d=q.distance(p);inside=q.inside(p)
  probes.append({'group':group,'pose':pose,'x':p[0],'y':p[1],'z':p[2],
   'clearance_mm':d-4,'inside':inside,'note':note})
 def floor(group,xy,z,pose='A'):
  h,ok=query[pose].floor_height(np.array(xy),z)
  if not ok:support_gaps.append({'group':group,'xy':list(map(float,xy)),'nominal_floor':float(z)})
  put(group,[*xy,h],pose,'sphere height solved against nearby exported upward faces' if ok else 'over open hole/edge; constructed height')
  return h
 # Both selector positions and the 0.3 mm radial branch interface.
 for label,ang in [('A',225),('B',135)]:
  a=math.radians(ang);t=np.array([math.sin(a),-math.cos(a)])
  for u in np.linspace(4,16.3,42):floor('selector-'+label+'-to-feed',O+t*u,ROTOR_Z-.1*u,label)
 # All fixed tracks, including both merge approaches and the final feed.
 for ri,r in enumerate(routes()):
  take=list(range(0,len(r['points']),max(1,int(len(r['points'])/(r['stations'][-1]/1.2)))))
  if take[-1]!=len(r['points'])-1:take.append(len(r['points'])-1)
  pose='B' if ri in [1,3] else 'A'
  for j in take:
   p=r['points'][j];t=r['tangents'][j];normal=np.array([-t[1],t[0]])
   for lateral in [-.6,0,.6]:floor(r['name'],p[:2]+lateral*normal,p[2]-.03,pose)
 # A: tangential handoff, bowl descent and central vertical throat.
 profile_r=np.array([0,5.25,8,20,27]);profile_z=np.array([116,116,116.4,119.8,122])
 for r in np.linspace(22,1.1,135):
  a=math.radians(120)+(22-r)/(22-1.1)*4*math.pi
  floor('funnel-spiral-envelope',F+r*np.array([math.cos(a),math.sin(a)]),np.interp(r,profile_r,profile_z))
 for x in np.linspace(1.1,0,10):put('funnel-throat-entry',[F[0]+x,F[1],120.04])
 for z in np.linspace(120.04,90.06,62):put('funnel-throat-drop',[*F,z])
 for x in np.linspace(38,47,22):floor('funnel-receiver-to-return',[x,104],86-.08*(x-38))
 # B: vertical hopper to a cup at rest; explicit pose-dependent ball location.
 R=29/3;C=1+R;effective=R-4
 def cup_center(angle):
  a=math.radians(angle)
  return TIP+np.array([0,-17*math.cos(a)-C*math.sin(a),-17*math.sin(a)+C*math.cos(a)-effective+.04])
 rest=cup_center(-5)
 for z in np.linspace(128,rest[2],25):put('hopper-to-cup',[TIP[0],88,z],'B')
 for angle in np.linspace(-5,37,43):
  sc=placed(parts,135,float(angle));q=Queries(np.concatenate(list(sc.values())));p=cup_center(angle)
  d=q.distance(p);inside=q.inside(p)
  probes.append({'group':'cup-loaded-poses','pose':float(angle),'x':p[0],'y':p[1],'z':p[2],
    'clearance_mm':d-4,'inside':inside,'note':'gravity contact construction; no force or release simulation'})
 release=cup_center(37);catch_z=84+.08*(release[1]-90)+4.06
 for z in np.linspace(release[2],catch_z,46):put('cup-release-to-deep-receiver',[TIP[0],release[1]-min(1.,(release[2]-z)*.12),z],'dump')
 for y in np.linspace(release[1]-1,79,24):floor('tipper-receiver-to-return',[TIP[0],y],84+.08*(y-90),'dump')
 # Common port into first catch. Same floor grade on both sides of the gap.
 for x in np.linspace(41,43,13):floor('common-feed-to-cascade',[x,42],67-.1*(x-42))
 # Three trays and two guarded drop edges, sampled around a sphere at each lip.
 for row in range(3):
  direction=1 if row%2==0 else -1;start=67-row*22
  for x in np.linspace(-direction*30,direction*30,81):
   floor('cascade-tray-'+str(row+1),[72+x,42],start-6*(direction*x+30)/60)
  if row<2:
   end=direction*30;upper=start-6;lower=start-22
   for a in np.linspace(0,math.pi/2,25)[1:]:put('cascade-edge-'+str(row+1),[72+end+direction*4.08*math.sin(a),42,upper+4.08*math.cos(a)])
   low_center=lower+.408+4.08*math.sqrt(1.01)
   for z in np.linspace(upper,low_center,41)[1:]:put('cascade-drop-'+str(row+1),[72+end+direction*4.08,42,z])
   for dx in np.linspace(4.08,0,21):put('cascade-catch-exit-'+str(row+1),[72+end+direction*dx,42,lower+dx*.1+4.08*math.sqrt(1.01)])
 for x in np.linspace(101.5,103,13):floor('cascade-to-final-feed',[x,42],17-.1*(x-102))
 for x in np.linspace(82,72,26):floor('final-feed-to-collector',[x,16],11.8)
 groups={}
 for p in probes:
  key=p['group'];g=groups.setdefault(key,{'samples':0,'minimum_clearance_mm':1e9,'inside_centers':0,'obstructions':[]})
  g['samples']+=1;g['minimum_clearance_mm']=min(g['minimum_clearance_mm'],p['clearance_mm']);g['inside_centers']+=int(p['inside'])
  if p['clearance_mm']<-.002 or p['inside']:g['obstructions'].append(p)
 for g in groups.values():g['passed']=not g['obstructions']
 report={'source_sha256':{p.stem:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'exports').glob('*.stl'))},'nominal_marble_diameter_mm':8,'sphere_contact_target_mm':4.04,'samples':len(probes),
  'passed':all(g['passed'] for g in groups.values()),'groups':groups,'open_edge_or_hole_probes':support_gaps,
  'limits':['Constructed static sphere envelopes through every listed interface, not a complete dynamics or retention test.',
   'A nominal 8 mm sphere and 0.04 mm geometric contact offset are analysis choices, not a print tolerance guarantee.',
   'Funnel spiral, vertical falls and cup-release paths are clearance constructions, not predicted trajectories.',
   'Surface distance and ray parity checked against the actual assembled STL triangles; routes also tested at lateral offsets +/-0.6 mm.',
   'Cup triggering, empty reset, rolling speed, bounce, friction, print fit and marble roundness require physical testing.']}
 (ROOT/'verification/marble-space-report.json').write_text(json.dumps(report,indent=2)+'\n')
 with (ROOT/'verification/marble-space-probes.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(probes[0]));w.writeheader();w.writerows(probes)
 print(json.dumps({'passed':report['passed'],'samples':len(probes),'groups':{k:{a:b for a,b in v.items() if a!='obstructions'} for k,v in groups.items()},'first_obstructions':[p for g in groups.values() for p in g['obstructions']][:20]},indent=2),flush=True)
if __name__=='__main__':main()
