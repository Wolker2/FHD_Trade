const assert=require('node:assert/strict'),scripts=SCRIPTS,ns='Script.MarketGoodsFinder.';
const make=(id,name,data)=>({id,name,data});
const p1=make(101,'Планета А',{1:[30,10,8],5:[70,5,3],6:[50,20,18]});
const s1=make(201,'Научная база А',{1:[150,12,9],5:[110,6,4],6:[99,21,19]});
const p2=make(102,'Планета Б',{1:[40,14,25],5:[80,9,11],6:[60,25,40]});
const s2=make(202,'Бизнес-центр Б',{1:[190,15,30],5:[200,10,20],6:[0,40,50]});
const stars=[{id:1,name:'А',x:20,y:10,planets:[p1],stations:[s1]},{id:2,name:'Б',x:120,y:80,planets:[p2],stations:[s2]}];
const modalStop=Symbol('native modal stop');let stopOnNotice=false;const texts=new Map(),states=new Map(),images=new Map(),customTexts=new Map(),customStates=new Map(),customImages=new Map(),positions=new Map();let menu=[],menuSeen=[],forms=[],formCalls=0,credits=1000,moneyWrites=0,ether=null,notices=0;
const itemData=(p,g)=>(p.data[g]||[0,0,0]);
const api={newarray:n=>Array(n).fill(0),ArrayDim:a=>a.length,ArrayAdd:(a,x)=>a.push(x),ArrayDelete:(a,i)=>a.splice(i,1),free:()=>{},
ArraySort:(keys,rows)=>{const pairs=rows.map((r,i)=>[keys[i],r]).sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0);pairs.forEach((p,i)=>{keys[i]=p[0];rows[i]=p[1];});},
GetGameOptions:n=>{assert(['ResolutionX','ResolutionY'].includes(n));return n==='ResolutionX'?1920:1080;},Player:()=>1,ShipStar:()=>stars[0],GalaxyStars:()=>stars.length,GalaxyStar:i=>stars[i],StarToCon:s=>s,SectorVisible:()=>1,StarOwner:()=>0,StarCustomFaction:()=>'',
StarPlanets:(s,i)=>i===undefined?s.planets.length:s.planets[i],StarRuins:(s,i)=>i===undefined?s.stations.length:s.stations[i],PlanetOwner:()=>0,ShipType:()=> 'SB',
GoodsAdd:(p,g,n)=>{assert.equal(n,0);return itemData(p,g)[0];},GoodsBuyPrice:(p,g)=>itemData(p,g)[1],GoodsSellPrice:(p,g)=>itemData(p,g)[2],
Id:p=>p.id,Name:p=>p.name,StarName:s=>s.name,CoordX:s=>s.x,CoordY:s=>s.y,
findsubstr:(s,t)=>s.indexOf(t),substr:(s,p,n)=>n===undefined?s.slice(p):s.slice(p,p+n),min:Math.min,max:Math.max,
t_Luxury:0,t_Technics:1,t_Arms:2,t_Narcotics:3,t_Alcohol:4,t_Medicine:5,t_Food:6,t_Minerals:7,
ListBox:(title,list)=>{assert(menu.length,'unexpected menu: '+title);menuSeen.push({title,list:[...list]});return menu.shift();},MessageBox:()=>{notices++;if(stopOnNotice)throw modalStop;},__modalStop:modalStop,
CurTurn:()=>0,ShipMoney:(p,value)=>{if(value!==undefined){credits=value;moneyWrites++;}return credits;},
InterfaceText:(f,n,v)=>{const key=f+':'+n;if(v!==undefined)texts.set(key,v);return texts.get(key)||'0';},
InterfaceState:(f,n,v)=>{const key=f+':'+n;if(v!==undefined)states.set(key,v);return states.get(key)||0;},InterfacePos:(f,n,x,y,z)=>positions.set(f+':'+n,[x,y,z]),InterfaceSize:()=>{},InterfaceImage:(f,n,v)=>{const k=f+':'+n;if(v!==undefined)images.set(k,v);return images.get(k)||'';},ShipGoodsIllegalOnPlanet:(ship,g,planet)=>{assert(![s1,s2].includes(planet),'ShipGoodsIllegalOnPlanet called on station');return planet.illegal&&planet.illegal.includes(g)?1:0;},
CustomInterfaceSize:()=>{},CustomInterfacePos:(n,x,y)=>positions.set('Custom:'+n,[x,y]),CustomInterfaceText:(n,v)=>{if(v!==undefined)customTexts.set(n,v);return customTexts.get(n)||'0';},CustomInterfaceState:(n,v)=>{if(v!==undefined)customStates.set(n,v);return customStates.get(n)||0;},CustomInterfaceImage:(n,v)=>{if(v!==undefined)customImages.set(n,v);return customImages.get(n)||'';},
CloseCustomForm:code=>{api.__closeCode=code??1;},
OpenCustomForm:formName=>{
 if(formName==='FHDTradeGoodsSelect'){
  api.__closeCode=null;
  execute(ns+'Table.InitGoodsSelect');
  while(api.__closeCode===null){
   assert(menu.length,'unexpected goods select wait');
   const act=menu.shift();
   const list=Array.from({length:8},(_,i)=>(customTexts.get('MGFGoodPicked'+i)==='1'?'[X] ':'[ ] ')+customTexts.get('MGFGoodName'+i));
   menuSeen.push({title:customTexts.get('MGFGoodsPickStatus'),list});
   if(act<0)api.__closeCode=2;
   else if(act===8)execute(ns+'Table.ConfirmPickGoods');
   else execute(ns+'Table.TogglePickGood','good_index',act);
  }
  return api.__closeCode;
 }
 if(formName==='FHDTradeServiceMenu'){
  api.__closeCode=null;
  execute(ns+'InitServiceMenu');
  while(api.__closeCode===null){
   assert(menu.length,'unexpected service menu wait');
   const act=menu.shift();
   if(act<0)api.__closeCode=99;
   else if(act===8)execute(ns+'ConfirmServiceRow');
   else execute(ns+'SelectServiceRow','service_index',act);
  }
  return api.__closeCode;
 }
 assert(forms.length,'table reopened unexpectedly');formCalls++;return forms.shift();
},
IdToPlanet:id=>stars.flatMap(s=>s.planets).find(p=>p.id===Number(id))||0,IdToShip:id=>[s1,s2].find(p=>p.id===Number(id))||0,
Ether:(n,x,text,buy,sell)=>{ether={text,buy,sell};},GenerateCodeStringFromBlock:p=>p};
const execute=(p,...args)=>{assert(p in scripts,'missing script: '+p);const result=args.length%2?args.pop():null;const params=Object.fromEntries(Array.from({length:args.length/2},(_,i)=>[args[i*2],args[i*2+1]]));const vars={...api,...params};return new Function(...Object.keys(vars),'try{'+scripts[p].replace(/\breturn;/g,result?'return '+result+';':'return;')+(result?'\nreturn '+result+';':'')+'}catch(__error){if(__error!==__modalStop)throw __error;'+(result?'return '+result+';':'')+'}')(...Object.values(vars));};
api.ExecuteCodeFromString=execute;
const select=choices=>{menu=[...choices];menuSeen=[];return execute(ns+'Table.SelectGoods','selection');};
assert.equal(select([1,8]),'1','one product');
assert.equal(select([1,5,6,8]),'1$5$6','three products');assert(menuSeen.at(-1).list[1].includes('[X]'));
assert.equal(select([0,1,2,3,8]),'0$1$2','fourth product must not be selected');
assert.equal(select([1,5,1,6,8]),'5$6','deselecting works');
assert.equal(select([8,-1]),'','cannot start an empty selection');assert.equal(select([1,-1]),'','cancel discards selection');
const selectedRows=(selection,sort=1,mode=0)=>execute(ns+'Table.BuildSelectedRows','goods_selection',selection,'sort_mode',sort,'filter_star_id',2,'search_mode',mode,'rows').map(r=>r.split('$'));
const single=selectedRows('1');assert.equal(single.length,4);assert(single.every(r=>r[15]==='1'&&r[16]==='Техника'));
const merged=selectedRows('1$5$6');assert.equal(merged.length,10);assert.deepEqual([...new Set(merged.map(r=>r[15]))].sort(),['1','5','6']);
for(const r of merged){assert.equal(r.length,17);const place=[p1,p2,s1,s2].find(p=>p.id===Number(r[9]));assert.equal(Number(r[5]),itemData(place,Number(r[15]))[1]);assert.equal(Number(r[14]),itemData(place,Number(r[15]))[0]);}
assert.equal(selectedRows('1$1$5').length,8,'no duplicate product rows');assert(selectedRows('1$5$6$7').every(r=>r[15]!=='7'));
const qty=selectedRows('1$5$6',0).map(r=>Number(r[14]));assert.deepEqual(qty,[...qty].sort((a,b)=>b-a));
const profit=merged.map(r=>Number(r[7]));assert.deepEqual(profit,[...profit].sort((a,b)=>b-a));
const global=selectedRows('0$1$2$3$4$5$6$7',1,1);assert.equal(global.length,3,'BestPrices returns top 3 most profitable deals overall');
assert.deepEqual(global.map(r=>Number(r[7])),[...global.map(r=>Number(r[7]))].sort((a,b)=>b-a),'BestPrices sorted by descending profit');
execute(ns+'Table.RenderFresh','form_name','GoodsShop','goods_index','1$5$6','search_mode',0,'star_id',2);
assert(texts.get('GoodsShop:MGFGoodsStatus').includes('Медикаменты'));assert(texts.get('GoodsShop:MGFGoodsStatus').includes('Еда'));
for(let i=0;i<merged.length;i++)assert(texts.get('GoodsShop:MGFRow'+i+'SourceSystem').includes(merged[i][16]),'row product name must be shown');
const chosen=merged.findIndex(r=>r[15]==='5');assert(chosen>=0);for(let i=0;i<10;i++)for(const k of ['Buy','Sell'])states.set('Galaxy:MGF'+k+'Mark'+i,1);
assert.equal(execute(ns+'Table.MarkRoute','form_name','GoodsShop','row_index',chosen,'marked'),1);
assert(ether.text.includes('Медикаменты'));assert(ether.text.includes('Купить: '+merged[chosen][5]+' cr'));
assert.deepEqual([...states].filter(([n,v])=>n.startsWith('Galaxy:MGF')&&v===1).map(([n])=>n).sort(),['Galaxy:MGFBuyMark0','Galaxy:MGFSellMark0']);
assert.equal(texts.get('Galaxy:MGFMarkerNext'),'1');
for(let i=0;i<2;i++){forms=[200+chosen,1];formCalls=0;execute(ns+'Table.ShowShopForm');assert.equal(formCalls,1,'mark success must close, including repeated slot 0');}
stopOnNotice=true;forms=[200+chosen,1];formCalls=0;execute(ns+'Table.ShowShopForm');assert.equal(formCalls,1,'successful mark must close even when the native notification stops the code');stopOnNotice=false;
texts.set('GoodsShop:MGFStateStar','999');forms=[200,1];formCalls=0;execute(ns+'Table.ShowShopForm');assert.equal(formCalls,2,'invalid row must keep table open');
const open=(choices,mode)=>{menu=[...choices];credits=1000;moneyWrites=0;states.set('GoodsShop:MGFStateStar',1);execute(ns+'Table.Open','form_name','GoodsShop','search_mode',mode,'star_id',2);};
open([-1],0);assert.equal(credits,1000);assert.equal(moneyWrites,0,'cancel must not charge');
open([1,5,6,8],0);assert.equal(credits,985);assert.equal(moneyWrites,1);assert.equal(texts.get('GoodsShop:MGFStateGoods'),'1$5$6');
open([],1);assert.equal(credits,900);assert.equal(moneyWrites,1,'BestPrices charges one fee without asking SelectGoods');assert.equal(states.get('GoodsShop:MGFGoodsTab0'),0,'no top buttons in BestPrices');
const extra=make(103,'Планета В',{1:[90,11,9],5:[45,8,6],6:[80,22,17]});stars[0].planets.push(extra);
execute(ns+'Table.RenderFresh','form_name','GoodsShop','goods_index','1$5$6','search_mode',0,'star_id',2);
const all=selectedRows('1$5$6');assert.equal(all.length,16);execute(ns+'Table.PageRight','form_name','GoodsShop');assert.equal(texts.get('GoodsShop:MGFStatePage'),'1');
assert(texts.get('GoodsShop:MGFRow0SourceSystem').includes(all[10][16]));assert.equal(execute(ns+'Table.MarkRoute','form_name','GoodsShop','row_index',0,'marked'),1);assert(ether.text.includes(all[10][16]));assert(ether.text.includes('Купить: '+all[10][5]+' cr'));
stars[0].planets.pop();
const n=notices;execute(ns+'Markers.Clear');assert.equal(notices,n,'reset stays silent');
console.log('PASS: choose/toggle/cancel 1-3 goods, fourth blocked, legacy single choice, mixed row goods/prices/stock, sort, per-goods top3, rendered goods, correct marked row, first/repeated close, invalid row stays open, cancel fee0, single search fee, mixed pagination and silent reset');

// A filter must affect both rendered rows and the route selected by that row.
execute(ns+'Table.RenderFresh','form_name','GoodsShop','goods_index','1$5$6','search_mode',0,'star_id',2);
assert.equal(texts.get('GoodsShop:MGFStateFilter'),'-1','new search must start without a commodity filter');
const toggle=slot=>execute(ns+'Table.ToggleGoodsFilter','form_name','GoodsShop','goods_slot',slot);
const displayed=()=>Array.from({length:10},(_,i)=>texts.get('GoodsShop:MGFRow'+i+'SourceSystem')).filter(Boolean);
const creditsBefore=credits,chargesBefore=moneyWrites;
texts.set('GoodsShop:MGFStatePage','1');toggle(1);
assert.equal(texts.get('GoodsShop:MGFStateFilter'),'5');assert.equal(texts.get('GoodsShop:MGFStatePage'),'0');
assert.equal(displayed().length,4);assert(displayed().every(r=>r.includes('Медикаменты')),'medication tab must show only its deals');
assert(images.get('GoodsShop:MGFGoodsTab1').includes('Goods5S'),'selected tab needs a distinct style');
execute(ns+'Table.FillShopForm');assert.equal(customStates.get('MGFGoodsTab2'),true);assert.equal(customImages.get('MGFGoodsTab1'),images.get('GoodsShop:MGFGoodsTab1'));
execute(ns+'Table.SortAlpha','form_name','GoodsShop');assert(displayed().every(r=>r.includes('Медикаменты')));
assert.equal(execute(ns+'Table.MarkRoute','form_name','GoodsShop','row_index',0,'marked'),1);assert(ether.text.includes('Медикаменты'));assert(ether.text.includes('Купить: 6 cr'));
assert.equal(ether.buy.id,201,'quantity-sorted medication row must buy at the station, not an unfiltered row');
toggle(1);assert.equal(texts.get('GoodsShop:MGFStateFilter'),'-1');assert.equal(displayed().length,10);
toggle(1);toggle(2);assert.equal(displayed().length,2);assert(displayed().every(r=>r.includes('Еда')));toggle(2);
assert.equal(credits,creditsBefore);assert.equal(moneyWrites,chargesBefore,'tabs are free');
const keepFilter=texts.get('GoodsShop:MGFStateFilter');toggle(3);toggle(-1);assert.equal(texts.get('GoodsShop:MGFStateFilter'),keepFilter,'invalid slot must not mutate the filter');
execute(ns+'Table.RenderFresh','form_name','GoodsShop','goods_index','1','search_mode',0,'star_id',2);
assert.equal(states.get('GoodsShop:MGFGoodsTab0'),1);assert.equal(states.get('GoodsShop:MGFGoodsTab1'),0);assert.equal(states.get('GoodsShop:MGFGoodsTab2'),0);
toggle(1);assert.equal(texts.get('GoodsShop:MGFStateFilter'),'-1','hidden slot must not select a missing commodity');
execute(ns+'Table.RenderFresh','form_name','GoodsShop','goods_index','0$1','search_mode',0,'star_id',2);toggle(0);
assert.equal(displayed().length,0,'selected commodity with no deals must show an empty table');assert(texts.get('GoodsShop:MGFEmptyText'));
execute(ns+'Table.RenderFresh','form_name','GoodsShop','goods_index','1$5$6','search_mode',0,'star_id',2);
assert.equal(texts.get('GoodsShop:MGFStateFilter'),'-1');
toggle(1);forms=[300,1];formCalls=0;execute(ns+'Table.ShowShopForm');assert.equal(formCalls,2,'tab press must reopen the existing table');assert.equal(texts.get('GoodsShop:MGFStateFilter'),'1');
execute(ns+'Table.RenderFresh','form_name','StarMap','goods_index','1$5$6','search_mode',0,'star_id',2);
execute(ns+'Table.ToggleGoodsFilter','form_name','StarMap','goods_slot',2);assert.equal(texts.get('StarMap:MGFStateFilter'),'6');assert.equal(execute(ns+'Table.MarkRoute','form_name','StarMap','row_index',0,'marked'),1);assert(ether.text.includes('Еда'));
console.log('PASS: three pictorial commodity tabs, hide unused slots, selected highlight, filter/toggle/switch, reset page, sort under filter, matching mark target, empty result, invalid slots, free tabs, custom-form reopen, StarMap filtering');

// Top tabs must be visible outside the clipped window and close with the table.
texts.set('StarMap:MGFStateGoods','1$5$6');states.set('StarMap:MGFTablePanel',1);
execute(ns+'Table.UpdateGoodsTabs','form_name','StarMap');
assert.deepEqual(positions.get('StarMap:MGFGoodsTabsPanel'),[842,166,-252]);assert.equal(states.get('StarMap:MGFGoodsTabsPanel'),true);
states.set('StarMap:MGFTableRoot',1);execute(ns+'Table.Close','form_name','StarMap');assert.equal(states.get('StarMap:MGFTableRoot'),0);
menu=[1,5,6,8];credits=1000;execute(ns+'Table.Open','form_name','StarMap','search_mode',0,'star_id',2);
assert.equal(states.get('StarMap:MGFTableRoot'),1);assert.equal(states.get('StarMap:MGFGoodsTabsPanel'),true);
assert.equal(execute(ns+'Table.MarkRoute','form_name','StarMap','row_index',0,'marked'),1);assert.equal(states.get('StarMap:MGFTableRoot'),0,'marking must also hide the top tab host');
console.log('PASS: StarMap top tabs anchored at842,166 and root visibility follows open/close/mark');

execute(ns+'Tests.LayoutBefore');
assert.deepEqual(positions.get('Custom:Window'),[480,200],'table anchor must remain unchanged');
assert.deepEqual(positions.get('Custom:MGFHUDFrame'),[461,152],'frame anchor must remain unchanged');
assert.deepEqual(positions.get('Custom:MGFGoodsTabsPanel'),[842,166],'custom header tabs must use screen coordinates');
console.log('PASS: compiled custom-form initializer keeps Window480,200 / Frame461,152 and anchors top tabs842,166');


// Test new 'Нужный товар' (search_mode=2) & Service Menu & Contraband red highlighting
{
 // Service menu: 3 services with costs 15..250, 50..1000, 100..1700
 execute(ns+'InitServiceMenu');
 assert.equal(customTexts.get('MGFServiceLabel0'),'Поиск товара по системе (15 cr)');
 assert.equal(customTexts.get('MGFServiceLabel1'),'Нужный товар (50 cr)');
 assert.equal(customTexts.get('MGFServiceLabel2'),'Выгодное предложение (100 cr)');
 assert.equal(customStates.get('MGFServiceSel0'),1);
 execute(ns+'SelectServiceRow','service_index',1);
 assert.equal(customStates.get('MGFServiceSel1'),true);
 execute(ns+'ConfirmServiceRow');
 assert.equal(api.__closeCode,11,'service 1 (Нужный товар) confirms with code 11');

 // Prepare data for 'Нужный товар' (search_mode=2):
 // Current mode 2 supports goods 0..6, including medicine and food.
 // Minerals (7) must not be searched in mode 2.
 // Unprofitable goods (buy >= sell, e.g. buy 40 sell 30) must NOT be shown.
 p1.data[0]=[40,20,18]; p2.data[0]=[30,35,30]; // Luxury: buy 20 -> sell 30 (profit +10, shown)
 s1.data[0]=[120,18,15]; s2.data[0]=[150,40,35]; // Luxury station: buy 18 -> sell 35 (profit +17, best!)
 p1.data[2]=[50,40,35]; p2.data[2]=[50,35,30]; // Arms: buy 40 -> sell 30 (profit -10, unprofitable -> NOT shown!)
 s1.data[2]=[0,0,0]; s2.data[2]=[0,0,0];
 p1.data[3]=[60,25,20]; p2.data[3]=[40,50,45]; // Narcotics: buy 25 -> sell 45 (profit +20, shown)
 p2.illegal=[3]; // Narcotics is contraband on Planet Б!

 credits=1000;moneyWrites=0;states.set('GoodsShop:MGFStateStar',1);
 execute(ns+'Table.Open','form_name','GoodsShop','search_mode',2,'star_id',2);
 assert.equal(credits,950,'Нужный товар charges 50 cr at turn 0 without asking SelectGoods');
 assert.equal(moneyWrites,1);
 p1.data[7]=[50,10,8]; p2.data[7]=[50,40,35]; // Minerals (7) profitable, but must NOT be searched in mode 2!
 const neededRows=execute(ns+'Table.BuildSelectedRows','goods_selection','0$1$2$3$4$5$6','sort_mode',1,'filter_star_id',2,'search_mode',2,'rows').map(r=>r.split('$'));
 // Goods 0 (Роскошь), 1 (Техника), 3 (Наркотики), 5 (Медикаменты), 6 (Еда) are profitable among 0..6; Arms (2) is unprofitable (40->30), Alcohol (4) has no data, and Minerals (7) is excluded!
 assert.deepEqual(neededRows.map(r=>r[15]).sort(),['0','1','3','5','6'],'only profitable goods from 0..6 (including Medicine 5 and Food 6, excluding Minerals 7) are returned');
 assert.equal(states.get('GoodsShop:MGFGoodsTab0'),0,'no top buttons in NeededGoods');
 assert.equal(states.get('GoodsShop:MGFGoodsTab1'),0,'no top buttons in NeededGoods');
 assert.equal(states.get('GoodsShop:MGFGoodsTab2'),0,'no top buttons in NeededGoods');
 delete p1.data[7];delete p2.data[7];
 // Verify 1 option per good and best buy/sell selected for Luxury (18 -> 35, profit 17)
 const luxRow=neededRows.find(r=>r[15]==='0');
 assert.equal(luxRow[5],'18');assert.equal(luxRow[6],'35');assert.equal(luxRow[7],'17');
 // Verify contraband red color (<color=235,80,60>) on Narcotics row!
 const narcIdx=neededRows.findIndex(r=>r[15]==='3');
 assert(narcIdx>=0);
 assert(texts.get('GoodsShop:MGFRow'+narcIdx+'SourceSystem').includes('<color=235,80,60>Наркотики</color>'),'contraband commodity name must be red');
 assert(texts.get('GoodsShop:MGFRow'+narcIdx+'DestinationPlace').includes('<color=235,80,60>Планета Б</color>'),'contraband planet must be red');
 // Clean up test data
 delete p1.data[0];delete p2.data[0];delete s1.data[0];delete s2.data[0];
 delete p1.data[2];delete p2.data[2];delete s1.data[2];delete s2.data[2];
 delete p1.data[3];delete p2.data[3];delete p2.illegal;
 console.log('PASS: FHDTradeServiceMenu, FHDTradeGoodsSelect checkmark start, NeededGoods (50..1000 cr, 1 best option per good for 0..6, unprofitable excluded), and Contraband red text');
}
