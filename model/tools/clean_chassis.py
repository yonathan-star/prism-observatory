"""Reproducible export cleanup; preserves the raw CAD export for review.

Welds float-resolution slivers at 0.0001 mm; removes tiny detached chips only.
Does not add geometry, bridge holes, or change the route design.
"""
import hashlib,json,struct,sys
import numpy as np
from mesh_math import ROOT,load_stl,measure_mesh
name=sys.argv[1] if len(sys.argv)>1 else 'chassis'
assert name in ['chassis','approach-bridge','collector-ramp']
source=ROOT/'verification'/f'raw-openscad-{name}.stl'
source.write_bytes((ROOT/'exports'/f'{name}.stl').read_bytes())
raw=load_stl(source);rounded=np.round(raw,4)
v,inv=np.unique(rounded.reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3)
areas=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)
f=f[areas>1e-9]
parent=np.arange(len(v))
def find(a):
 while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
 return a
for a,b,c in f:
 x,y,z=find(a),find(b),find(c);parent[y]=x;parent[z]=x
roots=np.array([find(a) for a in f[:,0]]);ids,counts=np.unique(roots,return_counts=True)
largest=ids[counts.argmax()];removed=[]
for key in ids:
 if key==largest:continue
 tr=v[f[roots==key]]
 volume=abs(np.einsum('ij,ij->i',tr[:,0],np.cross(tr[:,1],tr[:,2])).sum()/6)
 low=tr.reshape(-1,3).min(0);high=tr.reshape(-1,3).max(0)
 assert volume<.0001 and min(high-low)<.0002,('Detached geometry beyond a precision sliver must be fixed in CAD',volume,low,high)
 removed.append({'triangles':len(tr),'volume_mm3':float(volume),'bounds_mm':[low.tolist(),high.tolist()]})
assert sum(r['volume_mm3'] for r in removed)<.001
f=f[roots==largest]
# CGAL can represent a subdivided straight edge with a zero-area triangle.
# Replace each such collinear three-edge boundary by splitting its adjacent
# nondegenerate face. This preserves the exact surface, adding no hole cap.
edge_splits=0
for iteration in range(250):
 edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]])
 _,ei,ec=np.unique(np.sort(edges,axis=1),axis=0,return_inverse=True,return_counts=True)
 boundary=edges[ec[ei]==1]
 if not len(boundary):break
 link={int(a):int(b) for a,b in boundary}
 a=int(boundary[0,0]);loop=[a];current=link[a]
 while current!=a and len(loop)<100:loop.append(current);current=link[current]
 assert current==a,('Unclosed boundary needs CAD correction',loop)
 xyz=v[loop];edge_len=np.linalg.norm(np.roll(xyz,-1,axis=0)-xyz,axis=1);idx=int(edge_len.argmax())
 left,right=loop[idx],loop[(idx+1)%len(loop)];others=[k for k in loop if k not in [left,right]]
 delta=v[right]-v[left];length=np.linalg.norm(delta)
 distances=[np.linalg.norm(np.cross(v[k]-v[left],delta))/length for k in others]
 assert max(distances)<.00015,('Noncollinear hole must not be patched',distances,xyz)
 sequence=[left]+sorted(others,key=lambda k:float((v[k]-v[left])@delta))+[right]
 found=False
 for fi,face in enumerate(f):
  for j in range(3):
   if face[j]==left and face[(j+1)%3]==right:
    third=face[(j+2)%3];new=[[sequence[k],sequence[k+1],third] for k in range(len(sequence)-1)]
    f[fi]=new[0];f=np.vstack([f,new[1:]]);found=True;break
  if found:break
 assert found
 edge_splits+=1
assert not len(boundary),'Unresolved mesh boundary'
# An edge split can expose a coincident opposite-facing internal pair.
# Cancel both zero-thickness faces, preserving their surrounding surface.
_,di,dc=np.unique(np.sort(f,axis=1),axis=0,return_inverse=True,return_counts=True)
duplicate_removed=0
for key in np.flatnonzero(dc>1):
 ids=np.flatnonzero(di==key);assert len(ids)==2
 tr=v[f[ids]];normals=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0])
 assert np.linalg.norm(normals.sum(0))<1e-9
 duplicate_removed+=2
f=f[dc[di]==1]
tri=v[f]
dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')])
data=np.zeros(len(tri),dtype=dtype);data['vertices']=tri
n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n/=np.linalg.norm(n,axis=1,keepdims=True);data['normal']=n
output=ROOT/'exports'/f'{name}.stl'
output.write_bytes(b'Yonathan - Observatory Cascade; cleaned export; see report'.ljust(80,b' ')+struct.pack('<I',len(data))+data.tobytes())
_,metrics=measure_mesh(output)
report={'raw_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':metrics['sha256'],
 'coordinate_rounding_mm':.0001,'maximum_vertex_displacement_mm':float(np.linalg.norm(rounded-raw,axis=2).max()),
 'collapsed_zero_area_triangles':int((areas<=1e-9).sum()),'collinear_edge_retriangulations':edge_splits,'maximum_collinearity_deviation_allowed_mm':.00015,'coincident_opposite_internal_faces_removed':duplicate_removed,'removed_detached_chips':removed,'final_mesh':metrics,
 'limits':'Export cleanup only. Raw export and editable CAD are retained. No print or dynamics validation.'}
(ROOT/'verification'/f'{name}-export-cleanup.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert metrics['passed'],'Cleanup left topology issues; do not release.'
