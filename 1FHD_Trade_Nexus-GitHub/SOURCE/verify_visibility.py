from pathlib import Path
import sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent;sys.path.insert(0,str(root/'SOURCE'))
from compile_srhd_dat import parse_bp_raw,unpack_dat_bytes
b=parse_bp_raw(unpack_dat_bytes((root/'CFG/Main.dat').read_bytes(),0xB1E8C689))
def get(block,name):return next(e.child for e in block.elems if e.name==name and e.child)
def prop(block,name,default=None):return next((e.value for e in block.elems if e.name==name and e.child is None),default)
def nodes(block,path=()):
 for e in block.elems:
  if e.child:
   child=e.child;p=path+((e.name,child),)
   yield p
   yield from nodes(child,p)
ml=get(b,'ML')
for form in ['FHDTradeShopTable','GoodsShop','StarMap']:
 tabPaths=[p for p in nodes(get(ml,form)) if (prop(p[-1][1],'Name')or'').startswith('MGFGoodsTab') and prop(p[-1][1],'Name')[-1:] in '012']
 assert len(tabPaths)==3
 for p in tabPaths:
  child=p[-1][1];x,y,*_=map(float,prop(child,'Pos').split(','));w,h=map(float,prop(child,'Size').split(','));parent=p[-2][1];pw,ph=map(float,prop(parent,'Size').split(','))
  assert x>=0 and y>=0 and x+w<=pw and y+h<=ph,f'{form}/{prop(child,"Name")}: rect {(x,y,w,h)} is outside parent {prop(parent,"Name")} bounds {(pw,ph)}'
  assert not any(kind=='Window' for kind,node in p[:-1]),'Tabs must be outside the buffered Window work area'
 print('PASS:',form,'three tab rectangles fully inside their own parent, outside the Window client area')
