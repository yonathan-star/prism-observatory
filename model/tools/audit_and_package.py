"""Require current passing reports and matching render sources before packaging."""
import hashlib,json,zipfile
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
from assembly_model import ROOT
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 hashes={p.stem:digest(p) for p in sorted((ROOT/'exports').glob('*.stl'))}
 read=lambda n:json.loads((ROOT/'verification'/n).read_text())
 topology=read('topology-report.json');motion=read('fit-and-motion-report.json');ball=read('marble-space-report.json');mechanics=read('mechanical-estimates.json');assembly=read('assembly-sources.json');seating=read('seating-report.json')
 assert topology['passed'] and motion['passed'] and ball['passed'],'A required geometry screen has failed.'
 assert seating['passed'],'Service-track seating/peg checks need review.'
 assert mechanics['passed_idealized_gravity_signs'],'Idealized loading/restoring signs need review.'
 assert {n:v['sha256'] for n,v in topology['parts'].items()}==hashes
 for r in [motion,ball,mechanics,seating]:assert r['source_sha256']==hashes,'Report belongs to different STL bytes.'
 assert assembly['sources']==hashes
 for p in sorted((ROOT/'renders').glob('*.png')):
  with Image.open(p) as im:assert json.loads(im.info['Assembly-Source-Hashes'])==hashes,('Stale render',p.name)
 for name in ['chassis','approach-bridge','collector-ramp']:
  cleanup=read(f'{name}-export-cleanup.json')
  assert cleanup['output_sha256']==hashes[name]
  assert cleanup['raw_sha256']==digest(ROOT/'verification'/f'raw-openscad-{name}.stl')
  assert not cleanup['removed_detached_chips'],'Do not remove substantive geometry to make the screen pass.'
 summary={'status':'All listed DIGITAL geometry screens passed on these exact STL bytes; physical validation remains pending.',
  'timestamp_utc':datetime.now(timezone.utc).isoformat(),'mesh_sha256':hashes,
  'editable_CAD_sha256':{str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'cad').glob('*.scad'))},
  'checks':{'individual_printable_meshes':len(hashes),'cup_poses':len(motion['cup_poses']),'counterweight_poses':len(motion['ballast_poses']),
   'selector_poses':len(motion['selector_poses']),'module_lift_poses':len(motion.get('module_lift_poses',[])),'marble_sphere_probes':ball['samples'],'stationary_component_pairs':len(motion['stationary_fit'])},
  'physical_tests_performed':False,'submitted_or_printed':False,
  'limits':['Static sphere constructions are not trajectories, dynamics or retention proof.',
   'Motion screen tests sampled noncoplanar surface crossings, excluding intentional seat/press-fit contacts.',
   'No printer-specific slicing, supports/access, strength, balance/friction, roundness, rolling, tipping or empty-reset validation.',
   'Designed and modeled by Yonathan. Physical tests and programme acceptance remain pending.']}
 (ROOT/'verification/final-validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 assert (ROOT/'Prism-Observatory-Review.pdf').is_file()
 files=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in ['PACKAGE-CONTENTS.json','package-console.txt']]
 manifest={str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':digest(p)} for p in files}
 (ROOT/'PACKAGE-CONTENTS.json').write_text(json.dumps(manifest,indent=2)+'\n');files.append(ROOT/'PACKAGE-CONTENTS.json')
 dest=ROOT.parent/'Prism-Observatory-CAD-Review.zip'
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for p in files:z.write(p,str(Path(ROOT.name)/p.relative_to(ROOT)))
 with zipfile.ZipFile(dest) as z:
  assert z.testzip() is None
  for name,v in manifest.items():assert hashlib.sha256(z.read(str(Path(ROOT.name)/name))).hexdigest()==v['sha256']
 print(json.dumps({'zip':str(dest),'bytes':dest.stat().st_size,'sha256':digest(dest),'files':len(files),'checks':summary['checks'],'status':summary['status']},indent=2),flush=True)
if __name__=='__main__':main()
