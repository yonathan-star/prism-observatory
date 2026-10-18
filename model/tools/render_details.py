"""Inspection views and part sheet, rendered from the actual component STLs."""
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,PngImagePlugin
from assembly_model import ROOT,loaded,placed
from machine_geometry import O,TIP
from render_common import render,font
BG=(18,29,39);INK=(239,226,194);MUTED=(170,193,193)
COLORS={'chassis':[100,151,149],'funnel':[80,173,158],'cascade':[153,130,180],
 'cup':[233,174,86],'selector':[233,174,86],'ballast':[204,157,99],
 'ballast-light':[194,151,105],'balance-endclip':[180,150,106],'marble':[236,224,190],
 'approach-bridge':[53,129,131],'collector-ramp':[53,129,131]}
def clipped(tri,bounds):
 lo,hi=np.array(bounds[0]),np.array(bounds[1]);low=tri.min(1);high=tri.max(1)
 possible=np.all(high>=lo,1)&np.all(low<=hi,1);tri=tri[possible]
 whole=np.all(tri>=lo,axis=(1,2))&np.all(tri<=hi,axis=(1,2));out=list(tri[whole])
 for face in tri[~whole]:
  polygon=list(face)
  for axis in range(3):
   for limit,sign in [(lo[axis],1),(hi[axis],-1)]:
    result=[]
    if not polygon:break
    a=polygon[-1];ain=sign*(a[axis]-limit)>=-1e-9
    for b in polygon:
     bin=sign*(b[axis]-limit)>=-1e-9
     if ain!=bin:
      t=(limit-a[axis])/(b[axis]-a[axis]);result.append(a+t*(b-a))
     if bin:result.append(b)
     a=b;ain=bin
    polygon=result
  for j in range(1,len(polygon)-1):out.append(np.array([polygon[0],polygon[j],polygon[j+1]]))
 return np.array(out).reshape(-1,3,3)
def mesh_view(scene,size=(850,580),bounds=None,cut=False,direction=(1,-1.5,1.5),historic=False):
 tt=[];cc=[]
 for n,t in scene.items():
  box=None if bounds is None else np.array(bounds,float).copy()
  if cut and n=='funnel':
   if box is None:box=np.array([t.min((0,1)),t.max((0,1))])
   box[0,1]=max(box[0,1],104)
  tr=t if box is None else clipped(t,box)
  if len(tr):
   color=np.tile(COLORS.get(n,[110,124,130]),(len(tr),1))
   if historic and n=='chassis':
    color[:]=[191,185,166];ct=tr.mean(1)
    gold=((ct[:,0]>134)&(ct[:,1]>87)&(ct[:,1]<101)&(ct[:,2]<74))|((ct[:,1]>136)&(ct[:,2]>128))
    color[gold]=[210,157,80]
   tt.append(tr);cc.append(color)
 return render(np.concatenate(tt),np.concatenate(cc),size=size,direction=direction,margin=38)[0]
def main():
 p=loaded();page=Image.new('RGB',(1800,2390),BG);d=ImageDraw.Draw(page)
 d.text((55,35),'PRISM MACHINE / MECHANISM INSPECTION',font=font(40,True),fill=INK)
 d.text((58,100),'Actual exported meshes. Some fixed context is hidden to expose the mechanisms.',font=font(24),fill=MUTED)
 def cup_scene(angle):
  scene=placed(p,135,angle);t=scene['chassis'];c=t.mean(1)
  # Retain the axle mount/stops; omit the hopper and receiver for visibility.
  scene['chassis']=t[(abs(c[:,0]-TIP[0])<9.8)&(c[:,1]>98)&(c[:,1]<111)&(c[:,2]>100)&(c[:,2]<120)]
  return scene
 panels=[('MANUAL SELECTOR / A',placed(p,225,-5),([54,97,122],[99,137,149]),False),
  ('MANUAL SELECTOR / B',placed(p,135,-5),([54,97,122],[99,137,149]),False),
  ('CUP REST POSE / FEED CONTEXT HIDDEN',cup_scene(-5),([99,71,83],[138,125,138]),False),
  ('CUP DUMP POSE / FEED CONTEXT HIDDEN',cup_scene(55),([99,71,83],[138,125,138]),False),
  ('FUNNEL / FRONT HALF HIDDEN',{'funnel':placed(p)['funnel']},([3,72,92],[70,136,136]),True),
  ('THREE TRAYS / TWO GUARDED DROPS',{'cascade':placed(p)['cascade']},None,False)]
 for i,(title,scene,bounds,cut) in enumerate(panels):
  x=30+(i%2)*890;y=175+(i//2)*690
  d.rounded_rectangle((x,y,x+855,y+660),radius=14,outline=(62,84,91),width=2)
  d.text((x+18,y+16),title,font=font(24,True),fill=INK)
  im=mesh_view(scene,bounds=bounds,cut=cut);page.paste(im,(x+3,y+65))
 d.text((55,2280),'The poses and crop views explain the CAD. They do not show a physical run or certify retention.',font=font(24),fill=MUTED)
 meta=PngImagePlugin.PngInfo();meta.add_text('Provenance','Actual separate-part STL meshes; fixed context selectively hidden for inspection.')
 meta.add_text('Assembly-Source-Hashes',json.dumps({n:hashlib.sha256((ROOT/'exports'/f'{n}.stl').read_bytes()).hexdigest() for n in p}))
 page.save(ROOT/'renders/mechanism-details.png',pnginfo=meta)
 report=json.loads((ROOT/'verification/topology-report.json').read_text())['parts']
 page=Image.new('RGB',(2400,2630),BG);d=ImageDraw.Draw(page)
 d.text((55,35),f'SEPARATE PRINT PARTS / {len(p)} STL DESIGNS',font=font(40,True),fill=INK)
 d.text((58,100),'Each tile has its own scale. Print one of each installed part; retainers ×2. Coupon/alternative as needed.',font=font(22),fill=MUTED)
 for i,(name,tr) in enumerate(p.items()):
  x=20+(i%4)*595;y=175+(i//4)*595
  d.rounded_rectangle((x,y,x+575,y+565),radius=14,outline=(62,84,91),width=2)
  label=name.upper()+(' ×2' if name=='retainer' else '')
  d.text((x+15,y+14),label,font=font(24,True),fill=INK)
  im=mesh_view({name:tr},size=(565,425));page.paste(im,(x+5,y+65))
  dim=report[name]['dimensions_mm'];text=' × '.join(f'{v:.1f}' for v in dim)+' mm'
  d.text((x+15,y+512),text,font=font(22),fill=MUTED)
 d.text((55,2580),'Assembly STL is view-only. STL meshes are not a sliced or physically validated print package.',font=font(23),fill=MUTED)
 page.save(ROOT/'renders/print-parts.png',pnginfo=meta)
 scene=placed(p);page=Image.new('RGB',(1800,1880),BG);d=ImageDraw.Draw(page)
 d.text((55,35),'THE OBSERVATORY / CARVED RUINS & INSTRUMENTS',font=font(36,True),fill=INK)
 d.text((58,100),'Fixed story details in the actual CAD. Inspection crops omit surrounding context.',font=font(24),fill=MUTED)
 architecture=[('ARMILLARY / MERIDIAN / SURVEY CREST',{'chassis':scene['chassis']},([54,133,121],[97,144,151]),(1,-2,1.1)),
  ('CARVED HALL / DRESSED STONE NICHES',{'chassis':scene['chassis']},([96,55,6],[101.79,85,67]),(1,-.8,.65)),
  ('CELESTIAL RUNES / RETAINING RIM',{'funnel':scene['funnel']},([4,72,114],[70,136,136]),(1,-1.5,.8)),
  ('CONDUIT / FIXED SERVICE GAUGE',{'chassis':scene['chassis']},([134,86,38],[141,102,61]),(1,-1.5,.9))]
 for i,(title,sc,bounds,view) in enumerate(architecture):
  x=30+(i%2)*890;y=175+(i//2)*760
  d.rounded_rectangle((x,y,x+855,y+730),radius=14,outline=(62,84,91),width=2)
  d.text((x+18,y+16),title,font=font(23,True),fill=INK)
  im=mesh_view(sc,size=(850,640),bounds=bounds,direction=view,historic=True);page.paste(im,(x+3,y+70))
 d.text((55,1785),'The gauge, conduits and instrument are fixed sculpture. Color is an illustrative finishing scheme.',font=font(23),fill=MUTED)
 page.save(ROOT/'renders/observatory-character.png',pnginfo=meta)
 print('Mechanism details and separate-part sheet ready',flush=True)
if __name__=='__main__':main()
