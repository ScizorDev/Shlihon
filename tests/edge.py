from authhelp import ensure_auth
from playwright.sync_api import sync_playwright
log=[];errs=[];dialogs=[]
def ok(c,m):log.append(("PASS " if c else "FAIL ")+m)
with sync_playwright() as p:
    b=p.chromium.launch()
    shared=b.new_context(viewport={'width':375,'height':667},locale='he-IL',timezone_id='Asia/Jerusalem')
    def mk(q,w=375,h=667,dark=False,share=False):
        ctx=shared if share else b.new_context(viewport={'width':w,'height':h},locale='he-IL',timezone_id='Asia/Jerusalem',color_scheme='dark' if dark else 'light')
        pg=ctx.new_page();pg.route("**/fonts.googleapis.com/**",lambda r:r.abort());pg.on("pageerror",lambda e:errs.append(str(e)));pg.on("dialog",lambda d:(dialogs.append(d.message),d.dismiss()))
        pg.goto('file:///tmp/shlihon-tests/t5.html'+q);pg.wait_for_timeout(700);return pg
    W=lambda pg,t=400:pg.wait_for_timeout(t)
    # XSS via names, messages, addresses
    A=mk('?nonowner&uid=xa',share=True);A.evaluate("localStorage.clear()");A.reload();W(A,700);ensure_auth(A)
    X='<img src=x onerror=alert(1)>"\''
    A.click('[data-role="sender"]');W(A);A.click('label.tile:nth-child(2)');W(A,700);A.click("#wiz-next");W(A)
    A.fill("#w-name",X);A.click("#wiz-next");W(A);A.fill("#w-phone","050-1234567");A.click("#wiz-next");W(A)
    A.click('label.chip:has(input[value="גוש דן"])');W(A,700);A.fill("#w-about",X);A.click("#wiz-next");W(A,800)
    while A.query_selector("#tourNext"):A.click("#tourNext");W(A,150)
    A.click('#view [data-act="newjob"]');W(A);A.fill("#w-from",X+" st");A.click("#wiz-next");W(A);A.fill("#w-to","to "+X);A.click("#wiz-next");W(A)
    A.click("label.tile:nth-child(1)");W(A,700);A.click("#wiz-next");W(A);A.click('label.tile:has(input[value="flex"])');W(A);A.click("#wiz-next");W(A)
    A.fill("#w-notes",X*3);A.click("#wiz-next");W(A);A.click("#wiz-next");W(A);A.click("#wiz-next");W(A,700)
    B=mk('?nonowner&uid=xb',share=True);ensure_auth(B)
    B.click('[data-role="courier"]');W(B);B.click("#wiz-next");W(B);B.fill("#w-name","A"*60);B.click("#wiz-next");W(B);B.fill("#w-phone","050-7654321");B.click("#wiz-next");W(B)
    B.click('label.tile:has(input[value="car"])');W(B,700);B.click('[data-act="allregions"]');B.click("#wiz-next");W(B);B.click('label.chip:has(input[value="cash"])');B.click("#wiz-next");W(B);B.click("#wiz-next");W(B,800)
    while B.query_selector("#tourNext"):B.click("#tourNext");W(B,150)
    W(B,400);ok(B.query_selector(".card.top") is not None,"courier sees job with hostile text")
    ok(B.evaluate("document.querySelectorAll('img[src=\"x\"]').length")==0,"no injected <img> elements")
    ok(X in B.inner_text(".card.top"),"hostile text shown as text")
    ov=B.evaluate("document.documentElement.scrollWidth>innerWidth+1");ok(not ov,"no overflow with long content")
    B.click("#btn-yes");W(B,500);A.bring_to_front();W(A,700);A.click('[data-tab="couriers"]');W(A);A.click("#btn-yes");W(A,900)
    if A.query_selector("#pop-go"):A.click("#pop-go");W(A)
    A.fill("#chatInput",X);A.press("#chatInput","Enter");W(A,500)
    ok(A.evaluate("document.querySelectorAll('img[src=\"x\"]').length")==0,"chat message escaped")
    ok(not dialogs,"no alert() fired")
    # logout while chat open -> clean state
    A.click('[data-act="closechat"]');W(A);A.click('[data-tab="me"]');W(A);A.click('#view button.btn[data-act="opensettings"]');W(A)
    A.click('[data-act="setlang"][data-l="en"]');W(A);ok("Settings" in A.inner_text("#view"),"lang switch keeps settings screen")
    A.click('[data-act="setlang"][data-l="he"]');W(A)
    A.click('[data-act="tourstart"]');W(A,600);ok(A.query_selector("#tourEl") is not None,"tour from settings")
    A.keyboard.press("Escape");W(A)
    A.click('[data-tab="me"]');W(A);A.click('#view button.btn[data-act="opensettings"]');W(A);A.click('[data-act="logout"]');W(A,600)
    ok(A.query_selector("#banner") is None and A.query_selector(".match-box") is None and A.query_selector("nav.tabs:not([hidden])") is None,"logout clears UI")
    ok(not A.evaluate("document.querySelector('#bellBtn').hidden===false"),"bell hidden when logged out")
    # Enter key submits login
    A.fill("#l-id","nonexist");A.fill("#l-pass","Whatever1");A.press("#l-pass","Enter");W(A,800);ok(A.inner_text("#a-err")!="","Enter submits login")
    # unverified account login -> verify screen
    C=mk('?nonowner&uid=xc');C.click('[data-act="avgo"][data-v="register"]');W(C);C.fill("#r-email","c@example.com");C.fill("#r-user","cuser");C.fill("#r-pass","Secret123");C.fill("#r-pass2","Secret123");C.click('form[data-auth] button[type=submit]');W(C,900)
    C.click('[data-act="avgo"][data-v="login"]');W(C);C.fill("#l-id","cuser");C.fill("#l-pass","Secret123");C.click('form[data-auth] button[type=submit]');W(C,900)
    ok(C.query_selector('form[data-auth="verify"]') is not None,"unverified login -> verify screen")
    # double submit register
    D=mk('?nonowner&uid=xd');D.click('[data-act="avgo"][data-v="register"]');W(D);D.fill("#r-email","d@example.com");D.fill("#r-user","duser");D.fill("#r-pass","Secret123");D.fill("#r-pass2","Secret123")
    D.evaluate("()=>{const f=document.querySelector('form[data-auth]');f.requestSubmit();f.requestSubmit()}");W(D,1200)
    n=D.evaluate("Object.keys(JSON.parse(localStorage.__db)['data/users/xd/auth'].accounts).length");ok(n==1,f"double submit creates one account ({n})")
    # settings/auth layouts at 320 all langs, dark
    for L in ['he','en','ru','ar']:
        E=mk('?nonowner&uid=xe'+L,w=320,h=568,dark=True);E.evaluate(f"setLang('{L}')");W(E)
        ov1=E.evaluate("document.documentElement.scrollWidth>innerWidth+1");ensure_auth(E)
        E.click('[data-role="courier"]');W(E);ov2=E.evaluate("document.documentElement.scrollWidth>innerWidth+1")
        E.click("#wiz-next");W(E);E.fill("#w-name","N");E.fill("#w-name","Nn");E.click("#wiz-next");W(E);E.fill("#w-phone","050-1234567");E.click("#wiz-next");W(E)
        E.click('label.tile:has(input[value="car"])');W(E,700);E.click('[data-act="allregions"]');E.click("#wiz-next");W(E);E.click('label.chip:has(input[value="cash"])');E.click("#wiz-next");W(E);E.click("#wiz-next");W(E,800)
        while E.query_selector("#tourNext"):E.click("#tourNext");W(E,120)
        for tab in ["deck","mine","matches","me"]:
            E.click(f'[data-tab="{tab}"]');W(E,250)
            if E.evaluate("document.documentElement.scrollWidth>innerWidth+1"):ok(False,f"overflow {L} tab {tab}")
        E.click('#view button.btn[data-act="opensettings"]');W(E);ov3=E.evaluate("(()=>{const v=document.getElementById('view');return document.documentElement.scrollWidth>innerWidth+1||v.scrollWidth>v.clientWidth+1})()")
        E.click("#bellBtn");W(E);ov4=E.evaluate("(()=>{const r=document.getElementById('notifPanel').getBoundingClientRect();return r.left<0||r.right>innerWidth})()")
        ok(not(ov1 or ov2 or ov3 or ov4),f"320px dark {L}: auth/role/settings/bell fit ({ov1},{ov2},{ov3},{ov4})")
        if L=='ar':E.keyboard.press("Escape");E.screenshot(path="edge_ar_settings.png")
        E.context.close()
    print("\n".join(log));print("FAILS",sum(l.startswith("FAIL") for l in log),"ERR",errs,"DIALOGS",dialogs)
    b.close()
