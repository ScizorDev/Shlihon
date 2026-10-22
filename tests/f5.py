from common import *
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse,parse_qs
log=[];errs=[]
def ok(c,m):log.append(("PASS " if c else "FAIL ")+m)
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':375,'height':667},locale='he-IL',timezone_id='Asia/Jerusalem')
    W=lambda pg,t=400:pg.wait_for_timeout(t)
    A,B=setup_pair(ctx,errs,W)
    B.click('[data-tab="mine"]');W(B);ok(B.query_selector(".routecard") is None,"no route without deliveries")
    post_job(A,W);match(A,B,W)
    B.click('[data-tab="mine"]');W(B)
    ok(B.query_selector(".routecard") is not None,"route card shown")
    ok(len(B.query_selector_all(".stops li"))==2,"one job -> pickup + drop-off")
    kinds=B.eval_on_selector_all(".stops .sk","e=>e.map(x=>x.classList.contains('pick')?'p':'d')");ok(kinds==['p','d'],"pickup before drop-off")
    # second job, picked up first job
    B.click('.jobcard [data-act="stnext"]');W(B);B.click('.jobcard [data-act="stnext"]');W(B)
    # new job with different address
    A.bring_to_front();A.click('[data-tab="jobs"]');W(A);A.click('#view [data-act="newjob"]');W(A);A.click('[data-act="samplejob"]');W(A)
    A.evaluate("S.wiz.d.from='הרצל 5, חולון';S.wiz.d.to='ויצמן 10, כפר סבא';S.wiz.d.toRegion='שרון'");A.click("#wiz-next");W(A,500)
    match(A,B,W);B.click('[data-tab="mine"]');W(B,500)
    kinds=B.eval_on_selector_all(".stops .sk","e=>e.map(x=>x.classList.contains('pick')?'p':'d')")
    ok(kinds==['p','d','d'],"picked job contributes only drop-off; pickups first "+str(kinds))
    txt=B.inner_text(".stops");ok(txt.index("הרצל")<txt.index("ויצמן"),"new pickup before its drop-off")
    href=B.get_attribute("#routeG","href");q=parse_qs(urlparse(href).query)
    ok("google.com/maps/dir" in href and len(q.get("waypoints",[""])[0].split("|"))==2,"google maps multi-stop link "+str(q.get("waypoints")))
    ok(B.get_attribute("#routeG","target")=="_blank","opens in new tab")
    ov=B.evaluate("document.documentElement.scrollWidth>innerWidth+1");ok(not ov,"no overflow")
    B.click("#langBtn");W(B);B.click('[data-l="en"]');W(B);ok("Suggested route" in B.inner_text(".routecard"),"translated")
    print("\n".join(log));print("FAILS",sum(l.startswith("FAIL") for l in log),"ERR",errs)
    b.close()
