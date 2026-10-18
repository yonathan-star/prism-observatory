"""Sequential headless component exports, avoiding concurrent AppImage runtimes."""
import os,subprocess,json,shutil
from pathlib import Path
from machine_geometry import ROOT,export
PARTS=['chassis','funnel','cascade','cup','ballast','ballast-light','balance-endclip','selector','axle','retainer','coupon','marble','approach-bridge','collector-ramp']
def main():
 export();env=dict(os.environ,QT_QPA_PLATFORM='offscreen',APPIMAGE_EXTRACT_AND_RUN='1')
 binary=os.environ.get('OPENSCAD_BIN') or shutil.which('openscad')
 if not binary:raise RuntimeError('Install OpenSCAD or set OPENSCAD_BIN to its executable path.')
 for name in PARTS:
  dest=ROOT/'exports'/f'{name}.stl';log=ROOT/'verification'/f'openscad-{name}.log'
  with log.open('w') as f:
   p=subprocess.run([binary,'--export-format','binstl','-D',f'part="{name}"','-o',str(dest),str(ROOT/'cad/observatory-machine.scad')],env=env,stdout=f,stderr=subprocess.STDOUT)
  if p.returncode or not dest.exists():raise RuntimeError(f'{name} failed; read {log}')
  print(f'Exported {name}: {dest.stat().st_size:,} bytes',flush=True)
if __name__=='__main__':main()
