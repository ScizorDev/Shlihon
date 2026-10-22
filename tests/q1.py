from common import *
from playwright.sync_api import sync_playwright
log=[];errs=[]
def ok(c,m):log.append(("PASS " if c else "FAIL ")+m)
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':375,'height':667})
    W=lambda pg,t=400:pg.wait_for_timeout(t)
    A,B=setup_pair(ctx,errs,W);post_job(A,W);match(A,B,W)
    B.bring_to_front();courier_done(B,W)
    B.click('.jobcard.fin [data-act="rate"]');W(B)
    inside=[]
    for i in range(12):B.keyboard.press("Tab");inside.append(B.evaluate("!!document.activeElement.closest('#rateDlg')"))
    ok(all(inside),"Tab stays inside dialog")
    B.keyboard.press("Shift+Tab");ok(B.evaluate("!!document.activeElement.closest('#rateDlg')"),"Shift+Tab stays inside")
    B.keyboard.press("Escape");W(B);ok(B.query_selector("#rateDlg") is None,"Escape closes")
    ok(B.evaluate("document.activeElement&&document.activeElement.dataset.act")=="rate","focus returns to opener")
    B.click('[data-tab="me"]');W(B);B.click(".walletmini");W(B)
    ok(B.get_attribute('[data-tab="me"]','aria-current')=="page","nav highlights profile in wallet")
    tb=B.query_selector(".testbar").bounding_box();ok(tb["height"]<=48,"test bar compact (%d px)"%tb["height"])
    ok(B.query_selector('.testbar [data-act="testreset"]') is not None and B.query_selector('.testbar [data-act="test"][data-r]') is not None,"test bar keeps switch/reset/exit")
    B.evaluate("say('בדיקה')");W(B,100);t=B.query_selector(".toast").bounding_box();ok(t["y"]<60,"toast at top")
    A.bring_to_front();A.click('[data-tab="jobs"]');W(A);ok(A.query_selector("#view h1") is not None,"jobs view has heading")
    A.evaluate("setLang('en')");W(A);A.click('[data-tab="couriers"]');W(A);h=A.inner_text("#view h1");ok("Couriers" in h or "courier" in h,"couriers title in English: "+h)
    ok(A.evaluate("document.documentElement.scrollWidth<=innerWidth"),"no overflow")
    print("\n".join(log));print("FAILS",sum(l.startswith("FAIL") for l in log),"ERR",errs)
    b.close()
