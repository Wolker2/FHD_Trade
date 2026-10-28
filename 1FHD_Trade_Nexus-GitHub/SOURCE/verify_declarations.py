from pathlib import Path
from collections import Counter
import re,sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'SOURCE'))
from compile_srhd_dat import parse_bp_raw,unpack_dat_bytes
b=parse_bp_raw(unpack_dat_bytes((root/'CFG'/(sys.argv[2] if len(sys.argv)>2 else 'Rus')/'Lang.dat').read_bytes(),0xB1E8C689))
def flatten(b):return '\n'.join(e.value if e.child is None else '{\n'+flatten(e.child)+'\n}' for e in b.elems)
errors=[];count=0
# RScript variables share one scope across nested blocks, unlike JavaScript let.
def walk(b,path=''):
 global count
 for e in b.elems:
  p=path+'.'+e.name if path else e.name
  if e.child is not None:
   if p.startswith('Script.MarketGoodsFinder.') and all(v.child is None or v.name.isdigit() for v in e.child.elems):
    count+=1;code=flatten(e.child);code=re.sub(r"'(?:[^']|'')*'",'STR',code)
    names=[m.group(1).casefold() for m in re.finditer(r'\b(?:int|float|str|dword|unknown)\s+([A-Za-z_]\w*)\s*(?=[=;])',code)]
    duplicates=[n for n,c in Counter(names).items() if c>1]
    if duplicates:errors.append((p,duplicates))
   walk(e.child,p)
walk(b)
assert not errors,'Repeated declarations in RScript function scope: '+repr(errors)
print('PASS:',count,'compiled-block scripts contain no repeated variable declarations across nested blocks')
