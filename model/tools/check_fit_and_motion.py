"""Assembly surface crossing and sampled moving-envelope checks.

Does not model forces, friction, printed tolerances or continuous-time dynamics.
"""
import hashlib,json,numpy as np
from assembly_model import loaded,placed,rx,rz,ROOT
from machine_geometry import TIP,O,ROTOR_Z,routes
from mesh_queries import SurfaceGrid,Queries
def main():
 rr=routes();seats=[rr[4]['points'][int(np.floor((len(rr[4]['points'])-1)*f+.5))]-[0,0,7.2] for f in [.20,.45,.72]]
 def hits(grid,tr,allow_seat=False):
  raw=grid.collisions(tr,max_hits=len(tr) if allow_seat else 16);bad=[];contacts=[]
  for h in raw:
   p=np.array(h['point_mm'])
   if allow_seat and any(abs(p[2]-q[2])<.0002 and np.all(abs(p[:2]-q[:2])<4.61) for q in seats):contacts.append(h)
   else:bad.append(h)
  return bad,contacts
 parts=loaded();scene=placed(parts);body=scene['chassis'];names=['chassis','funnel','cascade','approach-bridge','collector-ramp','axle','retainer-1','retainer1']
 fixed=np.concatenate([scene[n] for n in names]);bodygrid=SurfaceGrid(body);fit={}
 fixed_modules=['chassis','funnel','cascade','approach-bridge','collector-ramp']
 for i,name in enumerate(fixed_modules):
  g=SurfaceGrid(scene[name])
  for other in fixed_modules[i+1:]:
   hit,contact=hits(g,scene[other],name=='chassis' and other=='approach-bridge');fit[name+'_vs_'+other]={'surface_crossings':hit,'seat_precision_contacts':contact,'passed':not hit}
 lifts=[]
 # Assembly and removal use the same reversible geometric paths, sampled in
 # both directions by reversing the listed poses. Service rails come off first.
 for name,excluded in [('funnel',{'funnel','selector'}),('cascade',{'cascade','approach-bridge','collector-ramp'}),('approach-bridge',{'approach-bridge','funnel','selector'})]:
  g=SurfaceGrid(np.concatenate([t for n,t in scene.items() if n not in excluded]))
  if name=='cascade':
   offsets=[[0,0,float(z)] for z in np.r_[np.linspace(0,32,33),np.arange(34,70,2)]]
   offsets += [[0,-float(y),68] for y in np.arange(1,36,1)]
   offsets += [[0,-35,float(z)] for z in np.arange(70,162,2)]
  else:offsets=[[0,0,float(z)] for z in np.r_[np.linspace(0,32,33),np.arange(34,162,2)]]
  for off in offsets:
   hit,contact=hits(g,scene[name]+off,name=='approach-bridge')
   lifts.append({'component':name,'offset_mm':off,'surface_crossings':hit,'seat_precision_contacts':contact,'passed':not hit})
 g=SurfaceGrid(np.concatenate([t for n,t in scene.items() if n!='collector-ramp']))
 offsets=[[float(x),0,6.0] for x in np.linspace(20,0,21)]+[[0,0,float(z)] for z in np.linspace(6.,0,25)[1:]]
 offsets += [[20,0,float(z)] for z in np.arange(8,168,2)]
 for off in offsets:
  hit=g.collisions(scene['collector-ramp']+off,max_hits=3)
  lifts.append({'component':'collector-ramp','offset_mm':off,'surface_crossings':hit,'passed':not hit})
 print('Stationary fit checks complete',flush=True)
 grid=SurfaceGrid(fixed);cup_checks=[];ballast_checks=[]
 cup_local=parts['cup']-[0,0,2.2];clip_local=parts['balance-endclip']-[0,0,1.4]+[0,15.7,0]
 for angle in np.arange(-4.5,55,1):
  tr=np.concatenate([cup_local,clip_local])@rx(angle).T+TIP;hit=grid.collisions(tr,max_hits=3)
  cup_checks.append({'angle_degrees':float(angle),'surface_crossings':hit,'passed':not hit})
  for pos in [9.5,9.7,10.5]:
   tr=(parts['ballast']-[0,0,1.8]+[0,pos,0])@rx(angle).T+TIP;bh=grid.collisions(tr,max_hits=2)
   ballast_checks.append({'angle_degrees':float(angle),'position_mm':pos,'surface_crossings':bh,'passed':not bh})
 print('Cup and carrier pose checks complete',flush=True)
 selector_fixed=np.concatenate([scene[n] for n in ['chassis','funnel','cascade','approach-bridge','collector-ramp']]);sg=SurfaceGrid(selector_fixed)
 selector=[];sl=parts['selector']-[0,0,6.4]
 for angle in np.arange(135.5,225,1):
  tr=sl@rz(angle).T+[O[0],O[1],ROTOR_Z];hit=sg.collisions(tr,max_hits=3)
  selector.append({'angle_degrees':float(angle),'surface_crossings':hit,'passed':not hit})
 report={'source_sha256':{p.stem:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'exports').glob('*.stl'))},'stationary_fit':fit,'module_lift_poses':lifts,'cup_poses':cup_checks,'ballast_poses':ballast_checks,'selector_poses':selector,
 'passed':all(v['passed'] for v in fit.values()) and all(v['passed'] for v in cup_checks+ballast_checks+selector+lifts),
 'limits':['Noncoplanar triangle surface crossings at sampled 1 degree poses; not a force or wear test.',
 'Intentional bearing-seat, base-foot and press-fit retainer contacts are not certified by this crossing screen.',
 'At the three named bridge seats only, crossings within 0.0002 mm of the shared seating plane are retained as export-precision contact records, not obstructions. Separate mesh seat/peg probes verify alignment and clearances.',
 'End-stop contact at -5/55 and 135/225 degrees is intentional. Interior poses are sampled half a degree away.',
 'Assembly/removal paths are reversible sampled rigid motions: funnel (selector removed); cascade (both service tracks removed, lift 68 mm then slide 35 mm forward before lifting clear); approach bridge vertically with funnel and selector removed; collector ramp raised 6 mm and slid 20 mm to the right. Installation reverses these steps.',
 'Vertical paths sampled every 1 mm through 32 mm, then every 2 mm through 160 mm to clear the whole assembly; ramp slide every 1 mm and lowering at 0.25 mm steps. At 20 mm right the ramp is also lifted clear. Not a continuous-time collision proof or certification of support/tool access.',
 'Physical clearances, smooth movement, rotor indexing, carrier retention and automatic tipping/reset still require testing.']}
 (ROOT/'verification/fit-and-motion-report.json').write_text(json.dumps(report,indent=2)+'\n')
 bad=[v for v in cup_checks+ballast_checks+selector+lifts if not v['passed']]
 print(json.dumps({'passed':report['passed'],'stationary_fit':fit,'cup_pose_count':len(cup_checks),'carrier_pose_count':len(ballast_checks),'selector_pose_count':len(selector),'failed_poses':bad[:12],'failed_pose_count':len(bad)},indent=2),flush=True)
if __name__=='__main__':main()
