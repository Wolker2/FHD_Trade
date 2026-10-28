"""Resolve the commodity-button and custom-dialog drawing resources, including empty captions and dynamic Goods0N..Goods7S styles."""
from pathlib import Path
import sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent;sys.path.insert(0,str(root/'SOURCE'))
from compile_srhd_dat import parse_bp_raw,unpack_dat_bytes,parse_blockpar
from gi_codec import decode
main=parse_bp_raw(unpack_dat_bytes((root/'CFG/Main.dat').read_bytes(),0xB1E8C689));cache=parse_blockpar(root/'SOURCE/CFG/CacheData.txt')
def fields(b):return {e.name:e.value for e in b.elems if e.child is None}
def path(b,p):
 for part in p.split('.'):
  e=next((e for e in b.elems if e.name==part),None)
  assert e is not None,'Resource key not found: '+p
  if e.child:b=e.child
  else:return e.value
 return b
styles=Path(sys.argv[2]) if len(sys.argv)>2 else Path(__file__).resolve().parent/'fixtures/vanilla_goods_button_resources.txt';native=parse_blockpar(styles)
fonts=Path(sys.argv[3]) if len(sys.argv)>3 else Path(__file__).resolve().parent/'fixtures/vanilla_goods_button_resources.txt';nativeCache=parse_blockpar(fonts)
def resolve(p,kind):
 assert p,f'TDataEC.PathGetBuf: empty {kind} resource path'
 if p.startswith('Bm.FHD_Trade.'):
  f=path(cache,p);rel=Path(*f.split('\\')[3:]);fp=root/rel;assert fp.is_file(),str(rel)
  if fp.name.startswith('Goods') and fp.suffix=='.gi':
   image=decode(fp.read_bytes());left,top,right,bottom=image['bounds'];size=(right-left,bottom-top)
   assert size==(80,29),f'Expected 80x29 GI button {fp.name}, got {size}'
 else:assert path(nativeCache,p),'Empty native cache entry: '+p
checks=0
for formName in ['FHDTradeShopTable','GoodsShop','StarMap','FHDTradeServiceMenu','FHDTradeGoodsSelect']:
 form=path(main,'ML.'+formName)
 def walk(b):
  for e in b.elems:
   if e.child:
    ps=fields(e.child)
    if e.name=='GraphButton' and (formName in ['FHDTradeServiceMenu','FHDTradeGoodsSelect'] or ps.get('Name','') in ['MGFGoodsTab0','MGFGoodsTab1','MGFGoodsTab2']):yield ps
    yield from walk(e.child)
 for ps in walk(form):
  effective=fields(path(native,'ML.'+ps['Style']));effective.update(ps)
  if 'Caption' in effective:resolve(effective.get('Font',''),'font for '+formName+'/'+ps['Name'])
  for imageName in ['ImageNormal','ImageNormalA','ImageDown']:resolve(effective[imageName].split(',',1)[1],imageName)
  if ps.get('Name','') in ['MGFGoodsTab0','MGFGoodsTab1','MGFGoodsTab2']:
   for g in range(8):
    for st in ['N','S']:
     dyn=fields(path(main,f'ML.FHDTradeGoodsTabStyles.Goods{g}{st}'))
     resolve(dyn.get('Font',''),f'dynamic style Font for Goods{g}{st}')
     for imageName in ['ImageNormal','ImageNormalA','ImageDown']:resolve(dyn[imageName].split(',',1)[1],imageName)
   checks+=1
assert checks==9
print('PASS: 9 commodity tabs, all 16 Goods0N..Goods7S dynamic styles, and all FHDTradeServiceMenu/FHDTradeGoodsSelect buttons resolve fonts and GI resources')
