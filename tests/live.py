from authhelp import ensure_auth, handle_done_gate
from playwright.sync_api import sync_playwright
log=[];errs=[]
def ok(c,m):log.append(("PASS " if c else "FAIL ")+m)
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':375,'height':667},locale='he-IL')
    def pg_(h):
        pg=ctx.new_page();pg.route("**/fonts.googleapis.com/**",lambda r:r.abort());pg.on("pageerror",lambda e:errs.append(str(e)));pg.goto('file:///tmp/shlihon-tests/t4.html#'+h);pg.wait_for_timeout(700);ensure_auth(pg);return pg
    A=pg_('testsender');W=lambda pg,t=400:pg.wait_for_timeout(t)
    A.evaluate("localStorage.clear()");A.reload();W(A,700);ensure_auth(A)
    A.click('[data-act="quickprofile"]');W(A,600)
    steps=0
    while A.query_selector("#tourNext") and steps<15:
        if steps==0 or True:pass
        A.click("#tourNext");W(A,250);steps+=1
    ok(steps>=10,f"sender tour has bell step ({steps})")
    A.click('#view [data-act="newjob"]');W(A);A.click('[data-act="samplejob"]');W(A);A.click("#wiz-next");W(A,500)
    B=pg_('testcourier');W(B,500)
    B.click('[data-act="quickprofile"]');W(B,600)
    tb=[]
    while B.query_selector("#tourNext"):
        tb.append(B.inner_text("#tourT"));B.click("#tourNext");W(B,250)
    ok(any("המשלוחים שלי" in x for x in tb),"courier tour includes my-deliveries step")
    ok(B.query_selector('[data-tab="mine"]') is not None,"courier has 'my deliveries' tab")
    B.click('[data-tab="mine"]');W(B);ok("עוד אין לך משלוחים" in B.inner_text("#view"),"mine empty state")
    B.click('[data-tab="deck"]');W(B);B.click("#btn-yes");W(B,600)
    A.bring_to_front();W(A,600);A.click('[data-tab="couriers"]');W(A);A.click("#btn-yes");W(A,900)
    ok(A.query_selector(".match-box") is not None,"sender match popup");A.click('[data-act="closepop"]');W(A)
    W(B,800)
    ok(B.query_selector(".match-box") is not None,"courier match popup live");
    if B.query_selector('[data-act="closepop"]'):B.click('[data-act="closepop"]');W(B)
    B.click('[data-tab="mine"]');W(B)
    ok(B.query_selector(".stepper") is not None and "יצאתי לאיסוף" in B.inner_text("#view"),"mine card with stepper and next button")
    ok(B.query_selector('a[href^="https://waze.com/ul?q="]') is not None,"waze nav link")
    badge=B.inner_text('[data-tab="mine"]');ok("1" in badge,"mine tab badge: "+badge.replace("\n"," "))
    A.click('[data-tab="jobs"]');W(A)
    B.click('[data-act="stnext"]');W(B,800)
    ok(B.query_selector(".stepper li.cur") is not None,"courier stepper advanced")
    W(A,500)
    ok(A.query_selector("#banner") is not None and "יצאתי לאיסוף" in A.inner_text("#banner"),"sender banner on status change")
    ok(A.query_selector("#bellBtn .bdot") is not None,"sender bell count")
    ok(A.query_selector(".jobcard .stepper") is not None,"sender job card stepper live")
    B.click('[data-act="stnext"]');W(B,500);B.click('[data-act="stnext"]');W(B,500)
    W(A,500);ok("הגעתי ליעד" in A.inner_text("#banner"),"sender sees arrived")
    cur=A.inner_text(".jobcard .stepper li.cur");ok("הגעתי ליעד" in cur,"sender stepper at arrived: "+cur)
    B.click('[data-act="stundo"]');W(B,500);W(A,400)
    ok("נאסף" in A.inner_text(".jobcard .stepper li.cur"),"undo reflected to sender")
    B.click('[data-act="stnext"]');W(B,400);B.click('[data-act="stnext"]');W(B,500);handle_done_gate(B)
    ok("כל הכבוד" in B.inner_text("#view") or "הסתיימו" in B.inner_text("#view"),"delivered state for courier")
    # chat notifications both sides
    A.click("#bellBtn");W(A);ok(A.query_selector("#notifPanel .nitem") is not None,"notification panel lists items")
    n_items=len(A.query_selector_all("#notifPanel .nitem"));ok(n_items>=4,f"panel items {n_items}")
    A.click("#notifPanel .nitem");W(A,500);ok(A.query_selector("#chatView") is not None,"tap notification opens chat")
    ok("עדכן" in A.inner_text("#msgs"),"status events in chat thread")
    B.click('[data-tab="matches"]');W(B);B.click(".chatrow");W(B,400);B.fill("#chatInput","אני בדרך");B.press("#chatInput","Enter");W(B,600)
    W(A,500);ok(A.query_selector("#banner") is None or "אני בדרך" not in A.inner_text("#banner"),"no banner for open chat")
    ok("אני בדרך" in A.inner_text("#msgs"),"message live in open chat")
    A.click('[data-act="closechat"]');W(A)
    B.fill("#chatInput","הגעתי");B.press("#chatInput","Enter");W(B,600);W(A,500)
    ok(A.query_selector("#banner") is not None and "הגעתי" in A.inner_text("#banner"),"sender banner on new message")
    B.click('[data-act="closechat"]');W(B)
    A.click('[data-tab="matches"]');W(A);A.click(".chatrow");W(A,300);A.fill("#chatInput","תודה!");A.press("#chatInput","Enter");W(A,600);W(B,500)
    ok(B.query_selector("#banner") is not None and "תודה!" in B.inner_text("#banner"),"courier banner on new message")
    ok(B.query_selector("#bellBtn .bdot") is not None,"courier bell count")
    t=B.evaluate("document.title");ok(t.startswith("("),"title shows unread count: "+t)
    B.click("#bellBtn");W(B);B.click('[data-act="notifall"]');W(B);ok(B.query_selector("#bellBtn .bdot") is None,"mark all read")
    B.keyboard.press("Escape");W(B)
    B.click('[data-tab="me"]');W(B);B.click('#view button.btn[data-act="opensettings"]');W(B);ok("התראות" in B.inner_text("#view"),"notification settings in settings screen")
    B.click("#sw-snd");W(B);ok(B.evaluate("localStorage.getItem('notifSound')")=="false","sound toggle")
    B.click('[data-act="sysnotif"]');W(B,600);ok(True,"system notif button no crash")
    B.click('[data-act="closesettings"]');W(B)
    # language check for new UI
    B.click("#langBtn");W(B);B.click('[data-l="en"]');W(B);B.click('[data-tab="mine"]');W(B)
    import re;heb=[x for x in re.findall(r'[^\n]*[֐-׿][^\n]*',B.inner_text("body")) if not re.search('בדיקה|גבירול|ז\'בוטינסקי|^ש$|050',x)]
    ok(not heb,"english mine view no system hebrew: "+str(heb[:5]))
    B.click("#bellBtn");W(B);heb=[x for x in re.findall(r'[^\n]*[֐-׿][^\n]*',B.inner_text("#notifPanel")) if not re.search('בדיקה|תודה|הגעתי|אני בדרך',x)];ok(not heb,"english notif panel: "+str(heb[:5]))
    B.screenshot(path="live_b.png");A.screenshot(path="live_a.png")
    print("\n".join(log));print("FAILS",sum(l.startswith("FAIL") for l in log),"ERR",errs)
    b.close()
