"""Actual-STL seat planes, peg-hole envelopes and blind-hole tip clearance."""
import hashlib,json,math
import numpy as np
from assembly_model import ROOT,loaded,placed
from machine_geometry import routes
from mesh_queries import Queries

def height_at(tri,xy,z,up):
 a=tri[:,0];b=tri[:,1]-a;c=tri[:,2]-a;det=b[:,0]*c[:,1]-b[:,1]*c[:,0]
 good=abs(det)>1e-10;d=xy-a[:,:2];inv=np.divide(1.,det,out=np.zeros_like(det),where=good)
 u=(d[:,0]*c[:,1]-d[:,1]*c[:,0])*inv;v=(b[:,0]*d[:,1]-b[:,1]*d[:,0])*inv
 h=a[:,2]+u*b[:,2]+v*c[:,2]
 good&=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(abs(h-z)<.4)&(det*(1 if up else -1)>0)
 assert good.any(),('No expected seating face',xy,z,up)
 return float(h[good][np.argmin(abs(h[good]-z))])

def main():
 scene=placed(loaded());rr=routes();seats=[]
 for f in [.20,.45,.72]:
  p=rr[4]['points'][int(np.floor((len(rr[4]['points'])-1)*f+.5))]
  seats.append(('approach-bridge',p-[0,0,7.2],1.5,3.0))
 for k,j in enumerate([45,105]):
  p=rr[5]['points'][j]+[3.2 if k==0 else 0,0,0]
  seats.append(('collector-ramp',p-[0,0,7.6],1.,1.7))
 report=[]
 for name,p,r,sample in seats:
  tr=scene[name];q=Queries(tr);point=p[:2]+[sample,0]
  fixed_h=height_at(scene['chassis'],point,p[2],True);moving_h=height_at(tr,point,p[2],False)
  probes=[]
  for z in [.25,.8,1.4,2.]:
   for a in np.linspace(0,2*math.pi,16,endpoint=False):
    t=p+[(r+.1)*math.cos(a),(r+.1)*math.sin(a),z]
    probes.append({'center_mm':t.tolist(),'inside_module':q.inside(t),'surface_distance_mm':q.distance(t)})
  tip=q.distance(p+[0,0,2]);gap=moving_h-fixed_h
  v={'part':name,'nominal_seat_center_mm':p.tolist(),'seat_plane_gap_mm':gap,
    'peg_radius_mm':r,'probe_radius_mm':r+.1,'hole_envelope_samples':len(probes),
    'minimum_probe_surface_distance_mm':min(x['surface_distance_mm'] for x in probes),
    'inside_module_probes':sum(x['inside_module'] for x in probes),'peg_tip_to_blind_cap_mm':tip}
  v['passed']=abs(gap)<.0002 and v['inside_module_probes']==0 and v['minimum_probe_surface_distance_mm']>.05 and tip>.5
  report.append(v)
 result={'source_sha256':{p.stem:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'exports').glob('*.stl'))},
   'passed':all(x['passed'] for x in report),'seats':report,
   'limits':['Actual triangle seat planes and geometric peg-hole envelope probes, not a manufacturing or retention test.',
    'The 0.1 mm expanded peg probes are analysis points; actual printing clearance and fit require the coupon.',
    'Shared seat-plane discrepancies below 0.0002 mm are export precision; no intentional mechanism material is removed.']}
 (ROOT/'verification/seating-report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
