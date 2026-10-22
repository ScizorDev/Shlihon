(()=>{
const out=[];const add=(sev,rule,el,msg)=>out.push({sev,rule,el:desc(el),msg});
function desc(el){if(!el||!el.tagName)return "";let s=el.tagName.toLowerCase();if(el.id)s+="#"+el.id;const c=(el.className&&el.className.baseVal===undefined?el.className:"")+"";if(c)s+="."+c.trim().split(/\s+/).slice(0,2).join(".");const a=el.dataset&&el.dataset.act;if(a)s+=`[act=${a}]`;const t=(el.innerText||el.getAttribute("aria-label")||"").trim().slice(0,30);return s+(t?` "${t}"`:"")}
const vis=el=>{const r=el.getBoundingClientRect();if(r.width<1||r.height<1)return false;const cs=getComputedStyle(el);if(cs.visibility==="hidden"||cs.display==="none"||+cs.opacity===0)return false;let p=el;while(p){if(p.hidden||p.getAttribute&&p.getAttribute("aria-hidden")==="true")return false;p=p.parentElement}return true};
function name(el){const l=el.getAttribute("aria-label");if(l&&l.trim())return l;const lb=el.getAttribute("aria-labelledby");if(lb){const t=lb.split(/\s+/).map(i=>(document.getElementById(i)||{}).innerText||"").join(" ").trim();if(t)return t}
 if(el.id){const f=document.querySelector(`label[for="${CSS.escape(el.id)}"]`);if(f&&f.innerText.trim())return f.innerText}const pl=el.closest("label");if(pl&&pl.innerText.trim())return pl.innerText;
 const t=(el.innerText||"").trim();if(t)return t;if(el.title)return el.title;const im=el.querySelector&&el.querySelector("img[alt]");if(im&&im.alt)return im.alt;if(el.placeholder)return el.placeholder;return ""}
const inter=[...document.querySelectorAll('button,a[href],input:not([type=hidden]),select,textarea,[role=button],[role=tab],[role=radio],[role=switch],[tabindex]:not([tabindex="-1"])')].filter(vis);
for(const el of inter){
 const tag=el.tagName.toLowerCase();const typ=el.type;
 if(!(tag==="input"&&(typ==="radio"||typ==="checkbox"))&&!name(el).trim())add("high","name",el,"interactive element has no accessible name");
 if(tag==="input"&&(typ==="radio"||typ==="checkbox"))continue;
 const r=el.getBoundingClientRect();
 if(el.closest(".msg")&&tag==="a")continue;
 if(r.width<24||r.height<24)add("high","target",el,`target ${Math.round(r.width)}x${Math.round(r.height)} < 24`);
 else if(r.height<40||r.width<40)add("low","target",el,`target ${Math.round(r.width)}x${Math.round(r.height)} < 40`);
}
for(const el of document.querySelectorAll('input:not([type=hidden]):not([type=radio]):not([type=checkbox]),select,textarea')){if(!vis(el))continue;const l=el.getAttribute("aria-label")||el.getAttribute("aria-labelledby")||(el.id&&document.querySelector(`label[for="${CSS.escape(el.id)}"]`))||el.closest("label");if(!l)add("med","label",el,"form field without label")}
for(const im of document.querySelectorAll("img")){if(vis(im)&&!im.hasAttribute("alt"))add("med","alt",im,"img without alt")}
const ids={};document.querySelectorAll("[id]").forEach(e=>{ids[e.id]=(ids[e.id]||0)+1});for(const [k,v] of Object.entries(ids))if(v>1)add("med","dupid",null,"duplicate id "+k);
for(const el of document.querySelectorAll("[aria-labelledby],[aria-describedby],[aria-controls]")){for(const at of ["aria-labelledby","aria-describedby","aria-controls"]){const v=el.getAttribute(at);if(v)for(const i of v.split(/\s+/))if(!document.getElementById(i))add("low","aria-ref",el,at+" -> missing #"+i)}}
// contrast
function rgb(s){const m=s.match(/rgba?\(([^)]+)\)/);if(!m)return null;const p=m[1].split(/[ ,\/]+/).filter(Boolean).map(Number);return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}}
function lum(c){const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(c.r)+.7152*f(c.g)+.0722*f(c.b)}
function bgOf(el){let layers=[];let p=el;while(p&&p.nodeType===1){const cs=getComputedStyle(p);const c=rgb(cs.backgroundColor);if(cs.backgroundImage&&cs.backgroundImage!=="none"&&!cs.backgroundImage.includes("gradient"))return null;if(c&&c.a>0){layers.push(c);if(c.a>=1)break}p=p.parentElement}
 let base=layers.length&&layers[layers.length-1].a>=1?layers.pop():{r:255,g:255,b:255,a:1};while(layers.length){const c=layers.pop();base={r:c.r*c.a+base.r*(1-c.a),g:c.g*c.a+base.g*(1-c.a),b:c.b*c.a+base.b*(1-c.a),a:1}}return base}
const seen=new Set();
const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
while(n=walker.nextNode()){if(!n.textContent.trim())continue;const el=n.parentElement;if(!el||seen.has(el)||!vis(el))continue;seen.add(el);if(el.closest("svg,.barcode,script,style,.sr"))continue;
 const cs=getComputedStyle(el);const fg=rgb(cs.color);const bg=bgOf(el);if(!fg||!bg)continue;
 const f2={r:fg.r*fg.a+bg.r*(1-fg.a),g:fg.g*fg.a+bg.g*(1-fg.a),b:fg.b*fg.a+bg.b*(1-fg.a)};let op=1;let p=el;while(p){op*=+getComputedStyle(p).opacity;p=p.parentElement}
 const L1=lum(f2),L2=lum(bg);let ratio=(Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);if(op<1)ratio=1+(ratio-1)*op;
 const px=parseFloat(cs.fontSize),bold=+cs.fontWeight>=700;const large=px>=24||(px>=18.66&&bold);const need=large?3:4.5;
 if(el.closest("button:disabled,[aria-disabled=true]"))continue;
 if(ratio<need)add(ratio<3?"high":"med","contrast",el,`contrast ${ratio.toFixed(2)} < ${need} (${cs.color} on rgb(${Math.round(bg.r)},${Math.round(bg.g)},${Math.round(bg.b)}) ${px}px)`);
 if(px<12)add("low","small-text",el,`font ${px}px`);
}
if(!document.documentElement.lang)add("high","lang",null,"html lang missing");
const h1=[...document.querySelectorAll("#view h1,#layer h1,#layer h2")].filter(vis);if(!document.querySelector("#view h1, #view h2")&&!document.querySelector("#layer [role=dialog]"))add("low","heading",null,"view has no heading");
// horizontal overflow
if(document.documentElement.scrollWidth>innerWidth+1)add("high","overflow",null,"horizontal overflow "+document.documentElement.scrollWidth);
return out;
})()
