(function(){
const P=new URLSearchParams(location.search);const NC=+P.get("nc")||300,NS=+P.get("ns")||150,JK=+P.get("jk")||8,MSG=+P.get("msg")||20;
const st=window.__store;let r=12345;const rnd=()=>(r=(r*1103515245+12345)%2147483648)/2147483648;const pick=a=>a[Math.floor(rnd()*a.length)];
const REG=["גוש דן","שרון","שפלה","ירושלים והסביבה","חיפה והקריות","צפון","דרום ונגב"];const VEH=["bike","moto","car","van","truck"];
const SIZES=["מעטפה","חבילה קטנה","חבילה בינונית","חבילה גדולה","רהיטים"];const now=Date.now();
const C=[],Sd=[];
for(let i=0;i<NC;i++){const id="lc"+i;C.push(id);st["profiles/"+id]={role:"courier",name:"שליח "+i,phone:"050-"+String(1000000+i),vehicle:pick(VEH),regions:[pick(REG),pick(REG)],allCountry:rnd()<.1,exp:Math.floor(rnd()*10),hours:"כל היום",pay:["cash","bit"],country:"IL",updated:now-i*1000};st["handles/"+id]={u:"c"+i,eh:"x"}}
const jobsAll=[];
for(let s=0;s<NS;s++){const id="ls"+s;Sd.push(id);st["profiles/"+id]={role:"sender",name:"עסק "+s,phone:"052-"+String(1000000+s),kind:rnd()<.5?"business":"private",region:pick(REG),country:"IL",updated:now-s*1000};st["handles/"+id]={u:"s"+s,eh:"x"};
 const items={};for(let k=0;k<JK;k++){const jid="j"+s+"x"+k;const fr=pick(REG);items[jid]={country:"IL",cur:"ILS",fromRegion:fr,from:"רחוב "+k+" "+s,toRegion:pick(REG),to:"שדרה "+k,size:pick(SIZES),vehicle:pick(VEH),when:null,urgent:rnd()<.3,price:30+Math.floor(rnd()*200),notes:"הערה "+k,pay:["cash","bit"],status:rnd()<.2?"closed":"open",created:now-Math.floor(rnd()*60*86400e3)};jobsAll.push([id,jid])}
 st["jobs/"+id]={items}}
const sw={},chats={};
for(const c of C){const j={};for(let t=0;t<25;t++){const [o,jid]=pick(jobsAll);j[jid]=rnd()<.6?1:-1}sw[c]={jobs:j}}
for(const s of Sd){sw[s]={couriers:{}}}
let matches=0;
for(const c of C){for(const [jid,v] of Object.entries(sw[c].jobs)){if(v!==1)continue;const s="ls"+jid.slice(1).split("x")[0];if(rnd()<.5){(sw[s].couriers[jid]=sw[s].couriers[jid]||{})[c]=1;matches++;
  const mid=jid+"__"+c;const th=[];for(let m=0;m<MSG;m++)th.push({t:now-(MSG-m)*60000,x:"הודעה "+m});
  (chats[c]=chats[c]||{threads:{},status:{}}).threads[mid]=th.filter((_,i)=>i%2);(chats[s]=chats[s]||{threads:{}}).threads[mid]=th.filter((_,i)=>!(i%2));
  const n=Math.floor(rnd()*5);if(n)chats[c].status[mid]=["go","picked","arrived","done"].slice(0,n).map((k,i)=>({s:k,t:now-(5-i)*600000}))}}}
for(const [k,v] of Object.entries(sw))st["swipes/"+k]=v;for(const [k,v] of Object.entries(chats))st["chats/"+k]=v;
window.__seedInfo={NC,NS,jobs:jobsAll.length,matches,bytes:JSON.stringify(st).length,maxChat:Math.max(...Object.values(chats).map(x=>JSON.stringify(x).length)),maxJobs:Math.max(...Sd.map(s=>JSON.stringify(st["jobs/"+s]).length))};
})();
