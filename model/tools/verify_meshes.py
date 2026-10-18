"""Measure each printable part and a gravity-only cup balance screen."""
import json,math
import numpy as np
from assembly_model import ROOT,PARTS,rx
from mesh_math import measure_mesh
def main():
 report={};mass={};cg={}
 for name in PARTS:
  tri,v=measure_mesh(ROOT/'exports'/f'{name}.stl')
  vv=np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2]))/6
  c=((tri.sum(1)/4)*vv[:,None]).sum(0)/vv.sum()
  v['solid_PLA_mass_estimate_g']=float(vv.sum()*.00124);v['centroid_in_print_coordinates_mm']=c.tolist()
  mass[name]=v['solid_PLA_mass_estimate_g'];cg[name]=c;report[name]=v
 report={'passed':all(v['passed'] for v in report.values()),'parts':report,
  'limits':'Binary STL topology/size/volume checks, not a slicer, strength, support, printability or physical function test.'}
 (ROOT/'verification/topology-report.json').write_text(json.dumps(report,indent=2)+'\n')
 cup=cg['cup']-[0,0,2.2];ballast=cg['ballast']-[0,0,1.8];clip=cg['balance-endclip']-[0,0,1.4]+[0,15.7,0]
 ball_mass=4/3*math.pi*4**3*.00124;balance=[]
 for pos in [9.5,9.7,10.5]:
  rows=[]
  for angle in np.linspace(-5,55,61):
   rot=rx(angle);empty=sum(mass[n]*(p@rot.T)[1] for n,p in [('cup',cup),('ballast',ballast+[0,pos,0]),('balance-endclip',clip)])
   a=math.radians(angle);ball_y=-17*math.cos(a)-(1+29/3)*math.sin(a)
   rows.append({'angle_degrees':float(angle),'empty_rearward_moment_g_mm':float(empty),'loaded_rearward_moment_g_mm':float(empty+ball_mass*ball_y)})
  balance.append({'position_mm':pos,'minimum_empty_restoring_moment_g_mm':min(r['empty_rearward_moment_g_mm'] for r in rows),
   'loaded_rest_moment_g_mm':rows[0]['loaded_rearward_moment_g_mm'],'samples':rows})
 mechanics={'source_sha256':{n:v['sha256'] for n,v in report['parts'].items()},'PLA_density_used_g_per_mm3':.00124,'ideal_solid_8mm_ball_mass_g':ball_mass,
  'counterweight_centre_range_mm':[9.5,10.5],'default_mm':9.7,'gravity_screen':balance,
  'passed_idealized_gravity_signs':all(b['minimum_empty_restoring_moment_g_mm']>0 and b['loaded_rest_moment_g_mm']<0 for b in balance),
  'limits':['Positive empty rearward moment means a restoring tendency; negative loaded-rest moment means a tipping tendency.',
   'Solid-PLA density and ideal sphere used. No axle friction, print infill differences, impact, acceleration or measured mass.',
   'Counterweight position, retention, triggering and empty return MUST be physically tuned and tested. This is not automatic-reset validation.']}
 (ROOT/'verification/mechanical-estimates.json').write_text(json.dumps(mechanics,indent=2)+'\n')
 print(json.dumps({'topology_passed':report['passed'],'parts':{n:{k:v[k] for k in ['passed','triangles','dimensions_mm','solid_PLA_mass_estimate_g']} for n,v in report['parts'].items()},'gravity_signs_passed':mechanics['passed_idealized_gravity_signs'],'balance':[{k:v for k,v in b.items() if k!='samples'} for b in balance]},indent=2),flush=True)
if __name__=='__main__':main()
