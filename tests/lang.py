from authhelp import ensure_auth
import re,sys
from playwright.sync_api import sync_playwright
HEB=re.compile('[֐-׿]')
L=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-fake-ui-for-media-stream","--use-fake-device-for-media-stream"]);ctx=b.new_context(viewport={'width':375,'height':667},locale='he-IL',permissions=["microphone"])
    pg=ctx.new_page();pg.route("**/fonts.googleapis.com/**",lambda r:r.abort())
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    W=lambda t=350: pg.wait_for_timeout(t)
    found=set()
    def scan(tag):
        txt=pg.evaluate("""()=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){const el=n.parentElement;if(!el||el.closest('script,style,[hidden]'))continue;const s=n.textContent.trim();if(s)out.push(s)}
          document.querySelectorAll('[aria-label],[placeholder],[title]').forEach(e=>{['aria-label','placeholder','title'].forEach(a=>{const v=e.getAttribute(a);if(v)out.push('@'+a+':'+v)})});return out}""")
        for t in txt:
            if HEB.search(t) and t not in found:
                found.add(t);print(f"[{tag}] {t[:110]}")
    pg.goto('file:///tmp/shlihon-tests/t2.html#app');W(600);ensure_auth(pg)
    pg.click("#langBtn");W();pg.click(f'[data-l="{L}"]');W(400)
    scan("rolepicker")
    pg.evaluate("location.hash='testsender'");ensure_auth(pg);W(600)
    for i in range(9):
        scan("swiz"+str(i))
        if pg.query_selector("#wiz-next"):
            pg.click("#wiz-next");W(400)
    pg.click('[data-act="tournext"]') if pg.query_selector('[data-act="tournext"]') else None
    for i in range(20):
        if not pg.query_selector("#tourNext"):break
        scan("tour"+str(i));pg.click("#tourNext");W(400)
    pg.click('#view [data-act="newjob"]');W()
    for i in range(8):
        scan("jwiz"+str(i))
        el=pg.query_selector(".wiz label.tile")
        if i==2: pg.click("label.tile:nth-child(2)");W(700);continue
        if i==4: pg.click('label.tile:has(input[value="at"])');W();scan("when-at")
        if i==0: pg.fill("#w-from","A st")
        if i==1: pg.fill("#w-to","B st")
        if i==5: pg.fill("#w-price","50")
        pg.click("#wiz-next");W(400)
    scan("jobs");pg.click('[data-tab="couriers"]');W();scan("couriers-empty")
    pg.evaluate("location.hash='testcourier'");ensure_auth(pg);W(600);pg.click('[data-act="quickprofile"]');W(600)
    for i in range(20):
        if not pg.query_selector("#tourNext"):break
        scan("ctour"+str(i));pg.click("#tourNext");W(400)
    scan("deck");pg.screenshot(path=f"lang_{L}_deck.png");pg.click("#btn-yes");W(500);scan("deck-empty")
    pg.evaluate("location.hash='testsender'");ensure_auth(pg);W(600);pg.click('[data-tab="couriers"]');W();scan("cdeck");pg.click("#btn-yes");W(800);scan("match");pg.click("#pop-go");W(400)
    pg.fill("#chatInput","hi");pg.press("#chatInput","Enter");W()
    pg.click("#plusBtn");W();scan("plus");pg.click('#plusMenu [data-act="payopen"]');W();scan("pay");pg.click('[data-act="paysend"]');W()
    pg.click("#plusBtn");W();pg.click('#plusMenu [data-act="gps"]');W(2500);scan("loc")
    if pg.is_visible("#locPanel"):pg.click('[data-act="locpick"][data-v="from"]');pg.click('[data-act="locsend"]');W()
    pg.click("#infoBtn");W();scan("info");pg.click("#infoBtn");W()
    pg.evaluate("location.hash='testcourier'");ensure_auth(pg);W(600)
    if pg.query_selector('[data-act="closepop"]'):pg.click('[data-act="closepop"]');W()
    pg.click('[data-tab="matches"]');W();scan("chatlist");pg.click(".more");W();scan("chatmenu");pg.keyboard.press("Escape")
    pg.click(".chatrow");W();pg.click("#plusBtn");W();pg.click('#plusMenu [data-act="payopen"]');W();pg.click('[data-act="paysend"]');W()
    pg.click("#infoBtn");W();pg.click("#closeChatBtn");W();scan("chat-closed");pg.screenshot(path=f"lang_{L}_chat.png")
    pg.click('[data-act="closechat"]');W();scan("chatlist2")
    pg.click('[data-tab="me"]');W();scan("me");pg.click('#view button.btn[data-act="opensettings"]');W();scan("settings");pg.click('[data-act="closesettings"]');W();pg.screenshot(path=f"lang_{L}_me.png")
    pg.click('[data-step="pay"]');W();scan("edit-pay")
    print("ERR",errs)
    b.close()
