"""Exercise BlockPar occurrence-based overlay merging against vanilla forms."""
from pathlib import Path
from collections import defaultdict
from copy import deepcopy
import sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent;sys.path.insert(0,str(root/'SOURCE'))
from compile_srhd_dat import parse_bp_raw,unpack_dat_bytes,parse_blockpar
vanilla=Path(sys.argv[2]) if len(sys.argv)>2 else Path(__file__).resolve().parent/'fixtures/vanilla_trade_forms.txt'
def merge(base,overlay):
 out=deepcopy(base);seen=defaultdict(int)
 for e in overlay.elems:
  if e.child:
   i=seen[e.name];seen[e.name]+=1;slots=[j for j,x in enumerate(out.elems) if x.name==e.name and x.child]
   if i<len(slots):out.elems[slots[i]].child=merge(out.elems[slots[i]].child,e.child)
   else:out.elems.append(deepcopy(e))
  else:
   out.elems=[x for x in out.elems if not(x.name==e.name and x.child is None)];out.elems.append(deepcopy(e))
 return out
def d(b,*names):
 for n in names:b=next(e.child for e in b.elems if e.name==n and e.child)
 return b
def named(b,name):
 if any(e.name=='Name' and e.value==name for e in b.elems):return b
 for e in b.elems:
  if e.child:
   found=named(e.child,name)
   if found:return found
 return None
base=parse_blockpar(vanilla);mod=parse_bp_raw(unpack_dat_bytes((root/'CFG/Main.dat').read_bytes(),0xB1E8C689));combined=merge(base,mod)
for form in ['GoodsShop','StarMap']:
 original=d(base,'ML',form);merged=d(combined,'ML',form)
 nativeNames=[v.value for e in d(original,'Panel').elems if e.child and e.name in ['Panel','Window'] for v in e.child.elems if v.name=='Name' and v.child is None]
 assert nativeNames,form+' has no native panel fixtures'
 for name in nativeNames:
  old=named(original,name)
  if old is None:continue
  new=named(merged,name);assert new is not None,f'{form}: missing native {name} after overlay merge'
  assert old==new,f'{form}: native {name} was modified by the new UI panel'
 print('PASS:',form,nativeNames,'retain names, contents and coordinates after overlay merge')
 assert named(merged,'MGFGoodsTabsPanel') is not None
 assert all(named(merged,'MGFGoodsTab'+str(i)) is not None for i in range(3))
print('PASS: merged forms contain all three commodity tabs without replacing native panels')
