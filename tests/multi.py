from common import *
from playwright.sync_api import sync_playwright
import time
log=[];errs=[]
def ok(c,m):log.append(("PASS " if c else "FAIL ")+m)
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':375,'height':667})
    W=lambda pg,t=400:pg.wait_for_timeout(t)
    def pg_(h,clear=False):
        pg=ctx.new_page();pg.route("**/fonts.googleapis.com/**",lambda r:r.abort());pg.on("pageerror",lambda e:errs.append(str(e)));pg.goto('file:///tmp/shlihon-tests/t4.html#'+h);W(pg,600)
        if clear:pg.evaluate("localStorage.clear();sessionStorage.clear()");pg.reload();W(pg,600)
        if not pg.query_selector('form[data-auth]'):pg.evaluate("doLogout()");W(pg,600)
        if pg.query_selector('form[data-auth="login"]'):pg.click('[data-act="avgo"][data-v="register"]');W(pg,300)
        n=pg.evaluate("Math.random().toString(36).slice(2,8)")
        pg.fill('#r-email',f'u{n}@example.com');pg.fill('#r-user',f'u{n}');pg.fill('#r-pass','Test1234');pg.fill('#r-pass2','Test1234')
        if pg.is_checked('#r-rem'):pg.uncheck('#r-rem')
        pg.click('form[data-auth="register"] button[type=submit]');W(pg,1300)
        code=pg.inner_text('.mail .code').strip();pg.fill('#v-code',code);pg.click('form[data-auth="verify"] button[type=submit]');W(pg,1300)
        pg.click('[data-act="quickprofile"]');W(pg,500)
        while pg.query_selector("#tourNext"):pg.click("#tourNext");W(pg,80)
        return pg
    A=pg_('testsender',True)
    for i in range(4):post_job(A,W)
    ok(A.evaluate("myJobs().length")==4,"4 jobs posted")
    Cs=[pg_('testcourier') for _ in range(5)]
    ids=[c.evaluate("S.me") for c in Cs];ok(len(set(ids))==5,"5 distinct couriers")
    t=time.time()
    for c in Cs:
        c.bring_to_front();c.click('[data-tab="deck"]');W(c,300)
        for k in range(4):
            if c.query_selector("#btn-yes"):c.click("#btn-yes");W(c,250)
    ok(all(c.evaluate("Object.values(cSw(S.me)).filter(v=>v===1).length")==4 for c in Cs),"each courier liked 4 jobs")
    A.bring_to_front();W(A,1000);A.click('[data-tab="couriers"]');W(A,500)
    n=0
    for k in range(40):
        if A.query_selector('[data-act="closepop"]'):A.click('[data-act="closepop"]');W(A,150)
        if A.query_selector("#btn-yes"):A.click("#btn-yes");W(A,250);n+=1
        else:
            nxt=A.evaluate("(()=>{const j=myJobs().find(j=>courierCandidatesFor(j).length);return j?j.id:null})()")
            if not nxt:break
            A.evaluate(f"S.jobSel='{nxt}';S.lastHtml='';render(true)");W(A,200)
    if A.query_selector('[data-act="closepop"]'):A.click('[data-act="closepop"]')
    W(A,800);mm=A.evaluate("myMatches().length");ok(mm==20,"sender has 20 matches (%d) after %d approvals"%(mm,n))
    for c in Cs:c.bring_to_front();W(c,300)
    ok(all(c.evaluate("myMatches().length")==4 for c in Cs),"each courier sees 4 matches")
    # all couriers message simultaneously
    for i,c in enumerate(Cs):
        for m in c.evaluate("myMatches().map(m=>m.id)"):c.evaluate(f"sendMsg('{m}','hi {i}')")
    W(A,1500);A.bring_to_front();A.evaluate("changed()");W(A,600)
    got=A.evaluate("myMatches().reduce((n,m)=>n+thread(m).length,0)");ok(got==20,"sender received 20 messages (%d)"%got)
    unread=A.evaluate("notifs().filter(x=>!x.r&&x.kind==='msg').length");ok(unread>=1,"message notifications (%d)"%unread)
    print("elapsed %.1fs"%(time.time()-t))
    print("\n".join(log));print("FAILS",sum(l.startswith("FAIL") for l in log),"ERR",errs)
    b.close()
