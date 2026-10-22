import sys,json,time
from authhelp import ensure_auth
from playwright.sync_api import sync_playwright
q=sys.argv[1] if len(sys.argv)>1 else "nc=300&ns=150&jk=8"
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':375,'height':667})
    pg=ctx.new_page();pg.on("pageerror",lambda e:errs.append(str(e)));pg.route("**/fonts.googleapis.com/**",lambda r:r.abort())
    t0=time.time();pg.goto('file:///tmp/shlihon-tests/tL.html?'+q+'#testcourier');pg.wait_for_timeout(600);ensure_auth(pg)
    pg.click('[data-act="quickprofile"]');pg.wait_for_timeout(800)
    while pg.query_selector("#tourNext"):pg.click("#tourNext");pg.wait_for_timeout(100)
    print("seed",pg.evaluate("window.__seedInfo"))
    def meas(label,js,n=5):
        ms=pg.evaluate(f"(()=>{{const a=[];for(let i=0;i<{n};i++){{const t=performance.now();{js};a.push(performance.now()-t)}}return a.reduce((x,y)=>x+y)/a.length}})()")
        print(f"{label:28s} {ms:8.1f} ms");return ms
    meas("allMatches()","allMatches()")
    meas("allJobs()","allJobs()")
    for who in ["lc3","ls2"]:
        pg.evaluate(f"S.me='{who}';S.lastHtml='';S.tab=null;render(true)");pg.wait_for_timeout(300)
        print("--",who,pg.evaluate("myProfile().role"),"matches",pg.evaluate("myMatches().length"))
        tabs=pg.evaluate("myProfile().role==='courier'?['deck','mine','matches','me']:['jobs','couriers','matches','me']")+(["wallet"] if who.startswith("lc") else ["dash"])
        for t in tabs:
            meas("render "+t,f"S.tab='{t}';S.lastHtml='';render(true)")
        meas("notifications calc","typeof computeNotifs==='function'?computeNotifs():0")
        m=pg.evaluate("myMatches()[0]&&myMatches()[0].id")
        if m: meas("open chat",f"S.chat='{m}';S.lastHtml='';render(true)");pg.evaluate("S.chat=null")
    pg.evaluate("(()=>{const o=changed;window.__ct=[];changed=function(){const t=performance.now();o();__ct.push(performance.now()-t)}})()")
    # snapshot churn: simulate 20 remote writes
    t=pg.evaluate("(async()=>{const t=performance.now();for(let i=0;i<20;i++){await S.db.doc('chats/lc'+(i%50)).update({x:i});}await new Promise(r=>setTimeout(r,400));return performance.now()-t})()")
    print(f"{'20 remote writes+render':28s} {t:8.1f} ms")
    print("changed() avg ms",pg.evaluate("__ct.length?__ct.reduce((a,b)=>a+b)/__ct.length:0"),"n",pg.evaluate("__ct.length"))
    print("heap MB",pg.evaluate("performance.memory?Math.round(performance.memory.usedJSHeapSize/1e6):-1"))
    print("ERR",errs[:3])
    b.close()
