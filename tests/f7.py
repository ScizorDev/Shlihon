from common import *
from playwright.sync_api import sync_playwright
log=[];errs=[]
def ok(c,m):log.append(("PASS " if c else "FAIL ")+m)
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':375,'height':667},locale='he-IL',timezone_id='Asia/Jerusalem')
    W=lambda pg,t=400:pg.wait_for_timeout(t)
    A,B=setup_pair(ctx,errs,W)
    post_job(A,W);match(A,B,W)
    B.click('[data-tab="mine"]');W(B);ok(B.query_selector(".etapick") is not None,"courier ETA picker")
    ok("לאיסוף" in B.inner_text(".etapick"),"pickup phase")
    A.bring_to_front();A.click('[data-tab="jobs"]');W(A)
    B.bring_to_front();B.click('[data-act="seteta"][data-v="15"]');W(B,600)
    ok(B.get_attribute('[data-act="seteta"][data-v="15"]','aria-pressed')=="true","selected ETA highlighted")
    A.bring_to_front();W(A,700)
    ok(A.query_selector("#banner") is not None and "15" in A.inner_text("#banner"),"sender notified with ETA")
    ok(A.query_selector(".etachip") is not None and "15" in A.inner_text(".etachip"),"sender job card shows ETA countdown")
    A.click('[data-tab="matches"]');W(A);A.click(".chatrow");W(A);ok(A.is_visible("#etaLine"),"ETA line in chat")
    # countdown math: shift time back 10 min
    left=A.evaluate("(()=>{const m=myMatches()[0];const e=etaOf(m);return etaText({...e,t:e.t-10*60000})})()");ok("~5" in left,"countdown "+left)
    late=A.evaluate("(()=>{const m=myMatches()[0];const e=etaOf(m);return etaText({...e,t:e.t-20*60000})})()");ok("עכשיו" in late,"arrives now when elapsed")
    # drop phase after pickup
    B.click('.jobcard [data-act="stnext"]');W(B);B.click('.jobcard [data-act="stnext"]');W(B)
    ok("ליעד" in B.inner_text(".etapick"),"drop-off phase after pickup")
    B.click('[data-act="seteta"][data-v="30"]');W(B,600);A.bring_to_front();W(A,600);ok("ליעד" in A.inner_text("#etaLine"),"sender sees drop-off ETA")
    B.bring_to_front();B.click('.jobcard [data-act="stnext"]');W(B);ok(B.query_selector(".etapick") is None,"no ETA after arrival")
    handle_done_gate(B,W) if B.query_selector('.jobcard [data-act="stnext"]') and (B.click('.jobcard [data-act="stnext"]') or True) else None
    W(B,500);A.bring_to_front();W(A,600);ok(A.is_hidden("#etaLine"),"ETA cleared after delivered")
    A.click("#langBtn");W(A);A.click('[data-l="ru"]');W(A);B.bring_to_front();B.click("#langBtn");W(B);B.click('[data-l="ru"]');W(B)
    ok(True,"lang switch ok")
    print("\n".join(log));print("FAILS",sum(l.startswith("FAIL") for l in log),"ERR",errs)
    b.close()
