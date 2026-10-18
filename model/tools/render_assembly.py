"""Actual full-assembly triangle renders, before packaging or physical validation."""
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,PngImagePlugin
from assembly_model import loaded,placed,ROOT
from machine_geometry import routes,F,O,TIP
from render_common import render,font,arrow
import render_common
BG=(18,29,39);INK=(239,226,194);MUTED=(170,193,193)
parts=loaded();scene=placed(parts);rr=routes()
def colors(name,tr):
 c=tr.mean(1);out=np.tile([191.,185.,166.],(len(c),1))
 if name=='chassis':
  out[c[:,2]<3.05]=[79,97,104]
  pp=np.concatenate([r['points'] for r in rr]);near=np.empty(len(c),int)
  for i in range(0,len(c),1000):
   delta=c[i:i+1000,None]-pp[None];delta[:,:,2]-=4
   near[i:i+1000]=np.argmin((delta*delta).sum(2),axis=1)
  q=pp[near];lat=np.linalg.norm(c[:,:2]-q[:,:2],axis=1);dz=c[:,2]-q[:,2]
  out[(lat<8)&(dz>-2.8)&(dz<16)]=[53,129,131]
  out[(np.linalg.norm(c[:,:2]-[TIP[0],90],axis=1)<20)&(c[:,2]>81)&(c[:,2]<113)]=[163,132,88]
  out[(np.linalg.norm(c[:,:2]-[38,104],axis=1)<17)&(c[:,2]>81)&(c[:,2]<103)]=[57,128,126]
  out[(c[:,1]>136)&(c[:,2]>128)]=[209,159,82]
  out[(c[:,0]>134)&(c[:,1]>87)&(c[:,1]<101)&(c[:,2]<74)&(c[:,2]>3.05)]=[198,143,77]
  out[(c[:,0]>127)&(c[:,1]>91)&(c[:,1]<97)&(abs(c[:,2]-68)<2.1)]=[198,143,77]
  out[(c[:,0]<11)&(c[:,1]>97)&(c[:,1]<103)&(c[:,2]<68)&(c[:,2]>3.05)]=[198,143,77]
  out[(c[:,0]<29)&(c[:,1]>97)&(c[:,1]<103)&(abs(c[:,2]-65)<2.1)]=[198,143,77]
 elif name=='funnel':out[c[:,2]>113]=[63,154,145]
 elif name=='cascade':
  out[:]=[90,125,139];out[(c[:,2]>13)&(c[:,1]>25)]=[128,112,159]
 elif name in ['approach-bridge','collector-ramp']:out[:]=[53,129,131]
 elif name in ['cup','ballast','selector']:out[:]=[220,164,83]
 else:out[:]=[92,106,111]
 return out
tri=np.concatenate(list(scene.values()));cc=np.concatenate([colors(n,tr) for n,tr in scene.items()])
meta=PngImagePlugin.PngInfo()
meta.add_text('Assembly-Source-Hashes',json.dumps({n:hashlib.sha256((ROOT/'exports'/f'{n}.stl').read_bytes()).hexdigest() for n in parts}))
meta.add_text('Status','Actual CAD assembly. Review in progress; no physical operation claim.')
def overview(name,gray=False,direction=(1,-1.5,1.6),sel=225,ca=-5):
 sc=placed(parts,sel,ca);tr=np.concatenate(list(sc.values()))
 co=np.concatenate([colors(n,t) for n,t in sc.items()])
 old=render_common.BG
 if gray:render_common.BG=(225,225,221);co=np.tile([188,189,184],(len(tr),1))
 raw,_=render(tr,co,size=(1850,1680),direction=direction,margin=75)
 page=Image.new('RGB',(1850,1960),render_common.BG);page.paste(raw,(0,170));d=ImageDraw.Draw(page)
 ink=(41,49,49) if gray else INK;muted=(79,91,90) if gray else MUTED
 d.text((65,30),'THE LAST OBSERVATORY / PRISM MACHINE',font=font(44,True),fill=ink)
 d.text((68,106),'Manual selector · funnel · tipping cup · shared guarded cascade · front collector',font=font(25),fill=muted)
 d.text((65,1857),'Actual separate-part CAD assembly · 144 mm base · nominal 8 mm printed marble',font=font(25),fill=ink)
 d.text((65,1904),'Review geometry. Physical rolling, tipping, reset, supports and print fit remain untested.',font=font(23),fill=muted)
 page.save(ROOT/'renders'/name,pnginfo=meta);render_common.BG=old
overview('full-assembly.png');print('Full assembly render ready',flush=True)
overview('full-assembly-clay.png',True)
overview('rear-assembly.png',False,(-1,1.3,1.7))
overview('branch-B-dump-pose.png',False,(1,-1.5,1.6),135,55)
im,proj=render(tri,cc,size=(1700,1650),direction=(0,0,1),margin=90)
page=Image.new('RGB',(1700,1880),BG);page.paste(im,(0,155));d=ImageDraw.Draw(page)
d.text((60,35),'FULL ASSEMBLY / TOP PLAN',font=font(45,True),fill=INK)
d.text((62,105),'Both branches merge before the common cascade. The three cascade levels overlap in plan.',font=font(23),fill=MUTED)
for r in rr:
 p=r['points'];i=len(p)//2;a,b=proj(p[i-3]),proj(p[i+3]);arrow(d,(a[0],a[1]+155),(b[0],b[1]+155),fill=(247,209,132),width=4)
d.text((60,1815),'Direction arrows are illustrative; see separate mechanism and transition inspections.',font=font(23),fill=MUTED)
page.save(ROOT/'renders/top-plan.png',pnginfo=meta)
