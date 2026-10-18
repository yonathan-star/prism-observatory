"""Local distance, ray parity and exact noncoplanar segment/triangle queries."""
import itertools,math
import numpy as np
from mesh_math import point_mesh_distance
class Queries:
 def __init__(self,tri):
  self.tri=tri;self.low=tri.min(1);self.high=tri.max(1);self.lo=tri.min((0,1));self.hi=tri.max((0,1))
  self.e1=tri[:,1]-tri[:,0];self.e2=tri[:,2]-tri[:,0]
  self.direction=np.array([.316227766,.777817459,.544331054]);self.direction/=np.linalg.norm(self.direction)
  self.h=np.cross(self.direction,self.e2);det=np.einsum('ij,ij->i',self.e1,self.h)
  self.valid=abs(det)>1e-10;self.inv=np.divide(1.,det,out=np.zeros_like(det),where=self.valid)
  self.upward=np.cross(self.e1,self.e2)[:,2]>1e-8
 def distance(self,p):
  use=np.all(self.high>=p-5.5,1)&np.all(self.low<=p+5.5,1)
  return point_mesh_distance(p,self.tri[use] if use.any() else self.tri)
 def inside(self,p):
  if np.any(p<self.lo) or np.any(p>self.hi):return False
  s=p-self.tri[:,0];u=self.inv*np.einsum('ij,ij->i',s,self.h);q=np.cross(s,self.e1)
  v=self.inv*(q@self.direction);t=self.inv*np.einsum('ij,ij->i',self.e2,q)
  hit=self.valid&(u>=0)&(v>=0)&(u+v<=1)&(t>1e-7)
  return bool(len(np.unique(np.round(t[hit],6)))%2)
 def floor_height(self,xy,z,radius=4.04):
  use=self.upward&np.all(self.high[:,:2]>=xy-4.3,1)&np.all(self.low[:,:2]<=xy+4.3,1)&(self.low[:,2]<z+4)&(self.high[:,2]>z-5)
  tri=self.tri[use]
  if not len(tri):return z+radius,False
  low,high=z+2.4,z+7
  supported=point_mesh_distance(np.r_[xy,low],tri)<radius
  for unused in range(22):
   mid=(low+high)/2
   if point_mesh_distance(np.r_[xy,mid],tri)<radius:low=mid
   else:high=mid
  return high,supported

def segment_hits(start,delta,tri):
 a=tri[:,0];e1=tri[:,1]-a;e2=tri[:,2]-a
 h=np.cross(delta,e2);det=np.einsum('ij,ij->i',e1,h)
 ok=abs(det)>1e-9;inv=np.divide(1.,det,out=np.zeros_like(det),where=ok)
 s=start-a;u=inv*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1)
 v=inv*np.einsum('ij,ij->i',np.broadcast_to(delta,q.shape),q)
 t=inv*np.einsum('ij,ij->i',e2,q)
 # Endpoint-only contact is allowed. Coplanar bearing/foot contacts are separate.
 good=ok&(u>1e-7)&(v>1e-7)&(u+v<1-1e-7)&(t>1e-7)&(t<1-1e-7)
 return good,t

class SurfaceGrid:
 def __init__(self,tri,cell=6):
  self.tri=tri;self.cell=cell;self.low=tri.min(1);self.high=tri.max(1);self.bins={}
  for i,(lo,hi) in enumerate(zip(np.floor(self.low/cell).astype(int),np.floor(self.high/cell).astype(int))):
   for key in itertools.product(*(range(lo[j],hi[j]+1) for j in range(3))):self.bins.setdefault(key,[]).append(i)
 def collisions(self,moving,max_hits=16):
  hits=[]
  for index,m in enumerate(moving):
   low=m.min(0);high=m.max(0);lo=np.floor(low/self.cell).astype(int);hi=np.floor(high/self.cell).astype(int)
   cand=set()
   for key in itertools.product(*(range(lo[j],hi[j]+1) for j in range(3))):cand.update(self.bins.get(key,[]))
   if not cand:continue
   ids=np.fromiter(cand,int);ok=np.all(self.high[ids]>=low-1e-8,1)&np.all(self.low[ids]<=high+1e-8,1);ids=ids[ok]
   if not len(ids):continue
   tr=self.tri[ids]
   for j in range(3):
    good,t=segment_hits(m[j],m[(j+1)%3]-m[j],tr)
    if good.any():
     k=np.flatnonzero(good)[0];hits.append({'moving_face':index,'fixed_face':int(ids[k]),'point_mm':(m[j]+t[k]*(m[(j+1)%3]-m[j])).tolist()});break
    # Reverse edge/triangle test catches a fixed edge crossing the moving face.
    a=tr[:,j];delta=tr[:,(j+1)%3]-a
    e1=m[1]-m[0];e2=m[2]-m[0];h=np.cross(delta,e2);det=h@e1;valid=abs(det)>1e-9
    inv=np.divide(1.,det,out=np.zeros_like(det),where=valid);s=a-m[0];u=inv*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1)
    v=inv*np.einsum('ij,ij->i',delta,q);t=inv*(q@e2)
    good=valid&(u>1e-7)&(v>1e-7)&(u+v<1-1e-7)&(t>1e-7)&(t<1-1e-7)
    if good.any():
     k=np.flatnonzero(good)[0];hits.append({'moving_face':index,'fixed_face':int(ids[k]),'point_mm':(a[k]+t[k]*delta[k]).tolist()});break
   if len(hits)>=max_hits:break
  return hits
