from pathlib import Path
import json,re,subprocess,sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent;sys.path[:0]=[str(root/'SOURCE')]
from compile_srhd_dat import parse_bp_raw,unpack_dat_bytes
b=parse_bp_raw(unpack_dat_bytes((root/'CFG'/(sys.argv[2] if len(sys.argv)>2 else 'Rus')/'Lang.dat').read_bytes(),0xB1E8C689));scripts={}
def flatten(b):return '\n'.join(e.value if e.child is None else '{\n'+flatten(e.child)+'\n}' for e in b.elems)
def walk(b,path=''):
 for e in b.elems:
  p=path+'.'+e.name if path else e.name
  if e.child is not None:
   if p.startswith('Script.MarketGoodsFinder.') and all(v.child is None or v.name.isdigit() for v in e.child.elems):scripts[p]=flatten(e.child)
   walk(e.child,p)
walk(b)
main=parse_bp_raw(unpack_dat_bytes((root/'CFG/Main.dat').read_bytes(),0xB1E8C689))
for segment in ['ML','FHDTradeShopTable','CodeBeforeRun']:
 main=next(e.child for e in main.elems if e.name==segment and e.child is not None)
scripts['Script.MarketGoodsFinder.Tests.LayoutBefore']=flatten(main)
for p,s in scripts.items():
 s=re.sub(r'\b(int|float|str|dword|unknown)\s+(\w+)\s*=',r'var \2=',s)
 s=re.sub(r'\bunknown\s+(\w+)\s*;',r'var \1;',s).replace('exit;','return;')
 pattern=r'0\+(?:substr|InterfaceText|CustomInterfaceText|ExecuteCodeFromString)\('
 offset=0
 while m:=re.search(pattern,s[offset:]):
  start=offset+m.start();opening=offset+m.end()-1;end=opening+1;depth=1;quoted=False
  while depth:
   ch=s[end]
   if ch=="'":quoted=not quoted
   if not quoted:
    if ch=='(':depth+=1
    if ch==')':depth-=1
   end+=1
  s=s[:start]+'Number('+s[start+2:end]+')'+s[end:];offset=end+6
 s=re.sub(r'\b0\+([A-Za-z_]\w*)\b(?!\s*\()',r'Number(\1)',s)
 s=s.replace('(rowCount-1)/cards','Math.trunc((rowCount-1)/cards)')
 scripts[p]=s
js=Path(__file__).with_name('goods_fixture.js').read_text().replace('SCRIPTS',json.dumps(scripts,ensure_ascii=False))
r=subprocess.run(['node','-e',js],text=True,capture_output=True);print(r.stdout,end='')
if r.returncode:print(r.stderr[:3000],file=sys.stderr)
raise SystemExit(r.returncode)
