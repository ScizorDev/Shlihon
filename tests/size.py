from common import *
from playwright.sync_api import sync_playwright
log=[];errs=[]
def ok(c,m):log.append(("PASS " if c else "FAIL ")+m)
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':375,'height':667})
    W=lambda pg,t=400:pg.wait_for_timeout(t)
    pg=ctx.new_page();pg.on("pageerror",lambda e:errs.append(str(e)));pg.goto('file:///tmp/shlihon-tests/t2.html#testcourier');W(pg,700);ensure_auth(pg)
    pg.click('[data-act="quickprofile"]');W(pg,600)
    while pg.query_selector("#tourNext"):pg.click("#tourNext");W(pg,100)
    # build a near-limit chats doc
    pg.evaluate("""(()=>{const th={};for(let i=0;i<30;i++){const a=[];for(let k=0;k<110;k++)a.push({t:Date.now()-1e9+k,x:'x'.repeat(60)});th['old'+i+'__'+S.me]=a}
      const d={threads:th};window.__store['chats/'+S.me]=d;S.chats[S.me]=JSON.parse(JSON.stringify(d));S.real.chats=true})()""")
    sz=pg.evaluate("docSize(S.chats[S.me])");ok(sz>200000,"seeded big chats doc %d"%sz)
    # a write that would exceed limit
    pg.evaluate("(async()=>{const big='y'.repeat(70000);await queue('chats',()=>mergeMine('chats',{note:big}))})()");W(pg,1200)
    sz2=pg.evaluate("JSON.stringify(window.__store['chats/'+S.me]).length");ok(sz2<262144 and "note" in pg.evaluate("Object.keys(window.__store['chats/'+S.me])"),"write succeeded after compaction %d"%sz2)
    ok(not pg.evaluate("S.readOnly"),"not read-only")
    ok(not pg.evaluate("S.err"),"no error")
    # housekeeping on soft limit
    pg.evaluate("""(()=>{const it={};for(let i=0;i<500;i++)it['j'+i]={country:'IL',cur:'ILS',fromRegion:'גוש דן',from:'רחוב ארוך מאוד '+i,toRegion:'שרון',to:'שדרה '+i,size:'חבילה קטנה',vehicle:'car',price:50,notes:'n'.repeat(120),pay:['cash'],status:'closed',created:Date.now()-60*864e5};
      window.__store['jobs/'+S.me]={items:it};S.jobs[S.me]={items:it};S.real.jobs=true;S.hkT=0})()""")
    pg.evaluate("changed()");W(pg,1200)
    js=pg.evaluate("JSON.stringify(window.__store['jobs/'+S.me]).length");ok(js<170000,"jobs doc compacted %d"%js)
    ok(pg.evaluate("Object.keys(window.__store['jobs/'+S.me].items).length")==500,"history kept (slim)")
    print("\n".join(log));print("FAILS",sum(l.startswith("FAIL") for l in log),"ERR",errs)
    b.close()
