(function(){
const store={}; // path->obj
const listeners=[];const docL=[];// {col,cb}
const clone=o=>JSON.parse(JSON.stringify(o));
const freeze=o=>{if(o&&typeof o==="object"){Object.freeze(o);Object.values(o).forEach(freeze)}return o};
function merge(a,b){for(const [k,v] of Object.entries(b)){if(v&&typeof v==="object"&&!Array.isArray(v)&&a[k]&&typeof a[k]==="object"&&!Array.isArray(a[k]))merge(a[k],v);else a[k]=clone(v)}return a}
function notify(col,path){setTimeout(()=>{listeners.filter(l=>l.col===col).forEach(l=>l.cb(snap(col)));docL.filter(l=>!path||l.path===path).forEach(l=>l.cb({exists:!!store[l.path],data:()=>store[l.path]?JSON.parse(JSON.stringify(store[l.path])):undefined}))},5)}
function snap(col){const docs=Object.keys(store).filter(p=>p.split("/").length===2&&p.startsWith(col+"/")).map(p=>{const d=freeze(clone(store[p]));return {id:p.split("/")[1],exists:true,data:()=>d}});return {docs,size:docs.length,empty:!docs.length}}
function check(o){const n=JSON.stringify(o).length;if(n>262144)throw {code:"invalid_argument",message:"too big "+n}}
const db={
 collection:c=>({limit:()=>({onSnapshot:(cb,err)=>{listeners.push({col:c,cb});setTimeout(()=>cb(snap(c)),5);return()=>{}}})}),
 doc:path=>{const col=path.split("/")[0];return {
  set:async d=>{if(typeof d!=="object"||Array.isArray(d))throw {code:"invalid_argument"};check(d);store[path]=clone(d);window.__writes++;notify(col,path)},
  update:async d=>{if(!store[path])throw {code:"invalid_argument",message:"update missing doc "+path};const n=merge(clone(store[path]),d);check(n);store[path]=n;window.__writes++;notify(col,path)},
  delete:async()=>{delete store[path];notify(col,path)},
  get:async()=>({exists:!!store[path],data:()=>store[path]}),onSnapshot:(cb)=>{docL.push({path,cb});setTimeout(()=>cb({exists:!!store[path],data:()=>store[path]?JSON.parse(JSON.stringify(store[path])):undefined}),5);return()=>{}}}}
};
window.__store=store;window.__writes=0;
let n=0;
window.claude={use:async name=>{
 if(name==="db")return db;
 if(name==="user")return {id:async()=>"u_owner",isOwner:async()=>true,me:async()=>({name:"בעל האפליקציה"}),can:async()=>true};
 if(name==="downloads")return {save:async o=>{window.__dl=(window.__dl||[]).concat({filename:o.filename,data:String(o.data)});return "saved"}};
 if(name==="assets")return {upload:async(b,o)=>{if(!b||!b.size)throw {code:"invalid_request"};window.__uploads=(window.__uploads||[]).concat({type:o&&o.type,size:b.size});return {id:"a".repeat(24)+String(++n).padStart(8,"0"),url:"/x",sizeBytes:b.size,contentType:o.type}}};
 return null}};
})();
