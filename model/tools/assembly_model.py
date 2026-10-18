"""Place the separately exported printable components in their CAD assembly poses."""
import struct,hashlib,json
import numpy as np
from machine_geometry import ROOT,O,TIP,F,CASCADE,ROTOR_Z
from mesh_math import load_stl
PARTS=['chassis','funnel','cascade','cup','ballast','ballast-light','balance-endclip','selector','axle','retainer','coupon','marble','approach-bridge','collector-ramp']
def rx(a):
 a=np.deg2rad(a);return np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
def ry(a):
 a=np.deg2rad(a);return np.array([[np.cos(a),0,np.sin(a)],[0,1,0],[-np.sin(a),0,np.cos(a)]])
def rz(a):
 a=np.deg2rad(a);return np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]])
def loaded():return {n:load_stl(ROOT/'exports'/f'{n}.stl') for n in PARTS}
def placed(parts,selector_angle=225,cup_angle=-5,balance_position=9.7,include_hardware=True):
 out={'chassis':parts['chassis'],'funnel':parts['funnel']+[F[0],F[1],3],
      'approach-bridge':parts['approach-bridge']+[7.4,34.4,59.03],
      'collector-ramp':parts['collector-ramp']+[82,8.4,4],
      'cascade':parts['cascade']+CASCADE,
      'cup':(parts['cup']-[0,0,2.2])@rx(cup_angle).T+TIP,
      'ballast':(parts['ballast']-[0,0,1.8]+[0,balance_position,0])@rx(cup_angle).T+TIP,
      'balance-endclip':(parts['balance-endclip']-[0,0,1.4]+[0,15.7,0])@rx(cup_angle).T+TIP,
      'selector':(parts['selector']-[0,0,6.4])@rz(selector_angle).T+[O[0],O[1],ROTOR_Z]}
 if include_hardware:
  out['axle']=parts['axle']@ry(90).T+TIP-[9.4,0,0]
  for sign in [-1,1]:out['retainer'+str(sign)]=parts['retainer']@ry(sign*90).T+TIP+[sign*6.6,0,0]
 return out
def write_stl(path,tri):
 dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')]);data=np.zeros(len(tri),dtype=dtype)
 n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-20)
 data['normal']=n;data['vertices']=tri
 path.write_bytes(b'Yonathan - Prism Observatory assembly; view only'.ljust(80,b' ')+struct.pack('<I',len(data))+data.tobytes())
def main():
 p=loaded();d=placed(p);write_stl(ROOT/'verification/assembly-A-view-only.stl',np.concatenate(list(d.values())))
 manifest={'status':'Assembly meshes are for inspection, not a single printable part. Print the separate component files.',
 'sources':{name:hashlib.sha256((ROOT/'exports'/f'{name}.stl').read_bytes()).hexdigest() for name in PARTS},
 'default_pose':{'selector_degrees':225,'cup_degrees':-5,'balance_position_mm':9.7},
 'component_instances':list(d)}
 (ROOT/'verification/assembly-sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
