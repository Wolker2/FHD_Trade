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
for p,s in scripts.items():
 s=re.sub(r'\b(int|float|str|dword|unknown)\s+(\w+)\s*=',r'let \2=',s)
 s=re.sub(r'\bunknown\s+(\w+)\s*;',r'let \1;',s).replace('exit;','return;')
 pattern=r'0\+(?:substr|InterfaceText|ExecuteCodeFromString)\('
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
 scripts[p]=s
js=r'''
const assert=require('node:assert/strict'),scripts=SCRIPTS,ns='Script.MarketGoodsFinder.';
const item=(id,name,buy,sell,stock,owner=0)=>({id,name,buy,sell,stock,owner});
const p1=item(101,'Планета А',10,11,30),s1=item(201,'Научная база А',8,15,100);
const p2=item(102,'Планета Б',9,12,40),s2=item(202,'Торговая база Б',7,20,2);
const under100=item(204,'Запас 99',6,0,99),loss=item(205,'Убыточная продажа',0,7,0),zeroProfit=item(206,'Равная цена',0,8,0);
const unusable=item(203,'Без торговли',0,0,100),captured=item(103,'Захвачена',1,900,50,5);
let stars=[{id:1,name:'А',planets:[p1,captured],stations:[s1,unusable,under100],visible:true},{id:2,name:'Б',planets:[p2],stations:[s2,loss,zeroProfit],visible:true},{id:3,name:'Закрыта',planets:[],stations:[item(301,'Скрытая база',1,9999,100)],visible:false}];
let home=0,choices=null;const forbidden=[];for(const [i,type]of ['PlayerMB','PlayerMB_licensed','CB','DomRuins'].entries()){const p=item(400+i,'Переименованная станция '+i,1,9000,9000);p.type=type;stars[0].stations.push(p);stars[1].stations.push({...p,id:p.id+10});forbidden.push(p.id,p.id+10);}
stars.push({id:4,name:'Доминаторы',owner:1,planets:[item(501,'Д-планета',1,9000,9999)],stations:[item(502,'Д-база',1,9000,9999)],visible:true});
stars.push({id:5,name:'Клисаны',faction:'Klissan',planets:[item(601,'К-планета',1,9000,9999)],stations:[item(602,'К-база',1,9000,9999)],visible:true});
stars.push({id:6,name:'Пираты',owner:2,planets:[],stations:[],visible:true});
let messages=0,clears=0,selected=null,ether=null;const texts=new Map(),states=new Map();
const api={newarray:n=>Array(n).fill(0),ArrayDim:a=>a.length,ArrayAdd:(a,x)=>a.push(x),ArrayDelete:(a,i)=>a.splice(i,1),free:()=>{},
ArraySort:(keys,rows)=>{const pairs=rows.map((r,i)=>[keys[i],r]).sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0);pairs.forEach((p,i)=>{keys[i]=p[0];rows[i]=p[1];});},
GetGameOptions:n=>n==='ResolutionX'?1920:1080,Player:()=>1,ShipStar:()=>stars[home],StarOwner:s=>s.owner||0,StarCustomFaction:s=>s.faction||'',ShipType:p=>{assert(![p1,p2,captured].includes(p),'ShipType called on a planet');return p.type||'SB';},lowercase:s=>s.toLowerCase(),count:s=>s.length,ord:s=>s.charCodeAt(0),ListBox:(title,list)=>{choices=[...list];return -1;},GalaxyStars:()=>stars.length,GalaxyStar:i=>stars[i],StarToCon:s=>s,SectorVisible:s=>s.visible,
StarPlanets:(s,i)=>i===undefined?s.planets.length:s.planets[i],StarRuins:(s,i)=>i===undefined?s.stations.length:s.stations[i],PlanetOwner:p=>{assert(![s1,s2,unusable].includes(p),'station passed to PlanetOwner');return p.owner;},ShipGoodsIllegalOnPlanet:(ship,g,p)=>{assert(![s1,s2,unusable].includes(p),'station passed to ShipGoodsIllegalOnPlanet');return p.illegal?1:0;},
GoodsBuyPrice:(p,g)=>p.buy,GoodsSellPrice:(p,g)=>p.sell,GoodsAdd:(p,g,n)=>{assert.equal(n,0);return p.stock;},CoordX:p=>p.id*10,CoordY:p=>p.id*5,Id:p=>p.id,Name:p=>p.name,StarName:s=>s.name,
findsubstr:(s,t)=>s.indexOf(t),substr:(s,p,n)=>n===undefined?s.slice(p):s.slice(p,p+n),MessageBox:()=>messages++,GenerateCodeStringFromBlock:p=>p,
t_Luxury:0,t_Technics:1,t_Arms:2,t_Narcotics:3,t_Alcohol:4,t_Medicine:5,t_Food:6,min:Math.min,max:Math.max,
InterfaceState:(f,n,v)=>{clears++;if(n.startsWith('MGFBuyMark')||n.startsWith('MGFSellMark'))states.set(n,v);},InterfacePos:()=>{},InterfaceImage:(f,n,v)=>{assert(v.startsWith('Style:FHDTradeGoodsTabStyles.Goods'));},InterfaceText:(f,n,v)=>{if(v!==undefined)texts.set(f+':'+n,v);return texts.get(f+':'+n)||'0';},ShipFindCustomShipInfoByType:()=>-1,
IdToPlanet:id=>stars.flatMap(s=>s.planets).find(p=>p.id===Number(id))||0,IdToShip:id=>stars.flatMap(s=>s.stations).find(p=>p.id===Number(id))||0,Ether:(t,n,description,buy,sell)=>ether=[buy,sell]};
const execute=(p,...args)=>{let result=args.length%2?args.pop():null;let params=Object.fromEntries(Array.from({length:args.length/2},(_,i)=>[args[2*i],args[2*i+1]]));let vars={...api,...params};return new Function(...Object.keys(vars),scripts[p]+(result?'\nreturn '+result+';':''))(...Object.values(vars));};
api.ExecuteCodeFromString=execute;
const local=(dest,sort=1)=>execute(ns+'Table.BuildLocalRows','goods_type',1,'sort_mode',sort,'filter_star_id',dest,'rows').map(r=>r.split('$'));
p1.stock=29;
assert(local(2).every(r=>r[9]!=='101'),'planet stock 29 must not appear in local purchase rows');
assert(execute(ns+'Table.BuildRows','goods_type',1,'sort_mode',1,'filter_star_id',0,'search_mode',1,'rows').every(r=>r.split('$')[9]!=='101'),'planet stock 29 must not appear in global purchase rows');
p1.stock=30;
assert(local(2).some(r=>r[9]==='101'),'planet stock 30 must remain');
assert(execute(ns+'Table.BuildRows','goods_type',1,'sort_mode',1,'filter_star_id',0,'search_mode',1,'rows').some(r=>r.split('$')[9]==='101'),'planet stock 30 must remain in global search');
p2.stock=0;assert(local(2).some(r=>r[12]==='102'),'sale destination stock must not be filtered');p2.stock=40;
const rows=local(2);assert.equal(rows.length,4,'local search must include all planet/station purchase-sale pairs');
assert.deepEqual(rows.map(r=>[r[9],r[12]]).sort(),[['101','102'],['101','202'],['201','102'],['201','202']]);
for(const r of rows){assert.equal(r.length,15);assert.equal(r[8],r[9]==='201'?'1':'0');assert.equal(r[11],r[12]==='202'?'1':'0');assert(!r.includes('Захвачена'));assert(!r.includes('Скрытая база'));}
assert(rows.every(r=>r[8]!=='1'||Number(r[14])>=100));assert(rows.every(r=>r[11]!=='1'||Number(r[7])>0));
assert.equal(rows[0][1],'Научная база А');assert.equal(rows[0][3],'Торговая база Б');assert.equal(Number(rows[0][7]),12);
assert.deepEqual(local(2,0).map(r=>Number(r[14])),[100,100,30,30],'quantity sort must show the largest stock first');
assert.deepEqual(local(2,0).map(r=>[r[9],r[12]]).sort(),rows.map(r=>[r[9],r[12]]).sort(),'alphabetical sort must retain stations');
s1.stock=99;assert(local(2).every(r=>r[9]!=='201'));s1.stock=100;assert(local(2).some(r=>r[9]==='201'));
const same=local(1);assert.equal(same.length,2);assert(same.every(r=>r[9]!==r[12]),'no route to the same trading place');
assert.equal(local(3).length,0,'closed sectors stay excluded');assert.equal(local(4).length,0);assert.equal(local(5).length,0);home=3;assert.equal(local(2).length,0);home=4;assert.equal(local(2).length,0);home=0;
for(const type of ['RC','PB','WB','SB','BK','MC','TC','MB','Manaan','SSB','BM']){s1.type=type;assert.equal(local(2).length,4,'ordinary station excluded: '+type);}s1.type='SB';
execute(ns+'Search','form_name','GoodsShop');assert.deepEqual(choices,['А','Б','Пираты (П)'],'system selection must exclude both hostile factions');
s1.stock=0;assert(local(2).every(r=>r[9]!=='201'),'station without goods cannot be a purchase source');s1.stock=100;
const global=execute(ns+'Table.BuildRows','goods_type',1,'sort_mode',1,'filter_star_id',0,'search_mode',1,'rows').map(r=>r.split('$'));
assert.equal(global.length,3);assert(global.every(r=>r[8]!=='1'||Number(r[14])>=100));assert(global.every(r=>r[11]!=='1'||Number(r[7])>0));assert(global.some(r=>r[8]==='1'));assert(global.some(r=>r[11]==='1'));assert(global.every(r=>r[9]!=='301'&&r[12]!=='301'));
assert(global.every(r=>![...forbidden,501,502,601,602].includes(Number(r[9]))&&![...forbidden,501,502,601,602].includes(Number(r[12]))),'global source/destination filter');
const byQty=execute(ns+'Table.BuildRows','goods_type',1,'sort_mode',0,'filter_star_id',0,'search_mode',1,'rows').map(r=>Number(r.split('$')[14]));assert.deepEqual(byQty,[...byQty].sort((a,b)=>b-a));
execute(ns+'Markers.Clear');assert.equal(messages,0,'clear marks must not open a confirmation popup');assert.equal(clears,20,'all old marks still cleared');
execute(ns+'Table.RenderFresh','form_name','GoodsShop','goods_index',1,'search_mode',0,'star_id',2);
assert.equal(texts.get('GoodsShop:MGFRow0SourcePlace'),'Научная база А');assert.equal(texts.get('GoodsShop:MGFRow0DestinationPlace'),'Торговая база Б');
for(const [name,value] of [['MGFStateGoods','1'],['MGFStateSort','1'],['MGFStatePage','0'],['MGFStateMode','0'],['MGFStateStar','2']])texts.set('GoodsShop:'+name,value);
for(let slot=0;slot<10;slot++)for(const kind of ['Buy','Sell'])states.set('MGF'+kind+'Mark'+slot,1);
execute(ns+'Table.MarkRoute','form_name','GoodsShop','row_index',0);assert.deepEqual(ether,[s1,s2]);
assert.deepEqual([...states].filter(([n,v])=>v===1).map(([n])=>n).sort(),['MGFBuyMark0','MGFSellMark0']);
execute(ns+'Markers.Clear');assert([...states.values()].every(v=>v===0));
console.log('PASS: planet 29/30 threshold in both search modes, unchanged sale destination stock, station stock 99/100 boundary, strictly profitable station sale destinations, replacement of previous marks, organization HQ/Dominator base exclusions, hostile system selection/source/destination exclusions, descending quantity sorting, station purchases/sales and table row types, planet/station combinations, sorting, same-system routes, stock, captured planets, closed sectors, global search, rendered station names, selection of station route and silent clear');
'''.replace('SCRIPTS',json.dumps(scripts,ensure_ascii=False))
r=subprocess.run(['node','-e',js],text=True,capture_output=True);print(r.stdout,end='')
if r.returncode:print(r.stderr[:2300],file=sys.stderr)
raise SystemExit(r.returncode)
