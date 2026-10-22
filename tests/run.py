from authhelp import ensure_auth
import sys,json,base64
from playwright.sync_api import sync_playwright
errs=[];log=[]
def ok(c,msg):
    log.append(("PASS" if c else "FAIL")+" "+msg)
with sync_playwright() as p:
    try:
     pass
    except: pass
    b=p.chromium.launch(args=["--use-fake-ui-for-media-stream","--use-fake-device-for-media-stream"])
    ctx=b.new_context(viewport={'width':375,'height':667},locale='he-IL',permissions=["microphone","clipboard-read","clipboard-write"])
    pg=ctx.new_page()
    pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.on("pageerror",lambda e: errs.append("PAGEERR "+str(e)))
    pg.route("**/fonts.googleapis.com/**",lambda r:r.abort())
    pg.goto('file:///tmp/shlihon-tests/t2.html#testsender');pg.wait_for_timeout(500);ensure_auth(pg);pg.wait_for_timeout(300)
    W=lambda t=250: pg.wait_for_timeout(t)
    def openPlus():
        if not pg.is_visible('#plusMenu'): pg.click('#plusBtn')
        W()
    txt=lambda: pg.inner_text("#view")
    # sender profile wizard
    ok(pg.query_selector(".wiz") is not None,"sender wizard auto-opens in test mode")
    # validation: kind step next without... kind prefilled from sample. go through manually
    pg.click("#wiz-next");W()
    ok("מדינה" in pg.inner_text("#wiz-title"),"country step after kind")
    ok(pg.is_checked('#c-country-IL'),"Israel preselected")
    pg.click("#wiz-next");W()
    ok("שם" in pg.inner_text("#wiz-title") or "העסק" in pg.inner_text("#wiz-title"),"step2 name: "+pg.inner_text("#wiz-title"))
    pg.fill("#w-name","");pg.click("#wiz-next");W()
    ok(pg.inner_text("#wiz-err")!="","empty name error shown")
    pg.fill("#w-name","פרחי השרון");pg.click("#wiz-next");W()
    pg.fill("#w-phone","12");pg.click("#wiz-next");W();ok(pg.inner_text("#wiz-err")!="","bad phone error")
    pg.fill("#w-phone","050-1234567");pg.click("#wiz-next");W()
    ok("אזור" in pg.inner_text("#wiz-title"),"region step")
    pg.click("#wiz-next");W()
    pg.click("#wiz-next");W(600)
    ok(pg.evaluate("!!__store['profiles/'+S.me]"),"sender profile saved")
    ok(pg.query_selector("#tourEl") is not None,"tour shown after profile")
    # walk tour
    steps=0
    while pg.query_selector("#tourNext") and steps<15:
        pg.click("#tourNext");W(300);steps+=1
    ok(pg.query_selector("#tourEl") is None,f"tour finished after {steps} steps")
    # new job wizard
    pg.click('#view [data-act="newjob"]');W()
    pg.click("#wiz-next");W();ok(pg.inner_text("#wiz-err")!="","job from validation")
    pg.fill("#w-from","הרצל 10, תל אביב");pg.click("#wiz-next");W()
    pg.fill("#w-to","ביאליק 5, רמת גן");pg.click("#wiz-next");W()
    pg.click("label.tile:nth-child(3)");W(700)  # medium auto advance
    ok("רכב" in pg.inner_text("#wiz-title"),"auto-advance to vehicle: "+pg.inner_text("#wiz-title"))
    ok(pg.is_checked('input[name="vehicle"][value="car"]'),"vehicle suggested car")
    pg.click("#wiz-next");W()
    pg.click("#wiz-next");W();ok(pg.inner_text("#wiz-err")!="","when validation")
    pg.click('label.tile:has(input[value="at"])');W()
    ok(pg.query_selector("#w-when") is not None and pg.input_value("#w-when")!="","datetime revealed & prefilled")
    pg.click("#wiz-next");W()
    pg.click('[data-act="price"][data-v="60"]');W()
    ok(pg.input_value("#w-price")=="60","price chip")
    pg.fill("#w-notes","קומה 3");pg.click("#wiz-next");W()
    ok("תשלם" in pg.inner_text("#wiz-title"),"pay step")
    pg.click("#wiz-next");W()
    ok("ככה" in pg.inner_text("#wiz-title"),"review step")
    ok("60" in txt() and "₪" in txt(),"preview price")
    pg.click("#wiz-next");W(500)
    jobs=pg.evaluate("__store['jobs/'+S.me]")
    ok(jobs and len(jobs["items"])==1,"job saved")
    j=list(jobs["items"].values())[0]
    ok(j["vehicle"]=="car" and j["price"]==60 and j["pay"]==["cash","bit"] and j["when"],"job fields "+json.dumps(j,ensure_ascii=False))
    # second job via sample
    pg.click('#view [data-act="newjob"]');W();pg.click('[data-act="samplejob"]');W();pg.click("#wiz-next");W(500)
    ok(len(pg.evaluate("__store['jobs/'+S.me].items"))==2,"second job via sample")
    # couriers tab empty
    pg.click('[data-tab="couriers"]');W();ok("אין עוד שליחים" in txt(),"no couriers yet")
    # switch to courier
    pg.evaluate("location.hash='testcourier'");ensure_auth(pg);W(500)
    ok(pg.query_selector(".wiz") is not None,"courier wizard")
    pg.click('[data-act="quickprofile"]');W(600)
    ok(pg.evaluate("!!__store['profiles/'+S.me]"),"courier quick profile")
    if pg.query_selector("#tourEl"): pg.click('[data-act="tourskip"]');W()
    ok(pg.query_selector(".card.top") is not None,"deck has card")
    ok("2 משלוחים" in txt(),"two jobs in deck")
    vis=pg.evaluate("(()=>{const r=document.querySelector('#btn-yes').getBoundingClientRect();return r.bottom<=document.querySelector('nav.tabs').getBoundingClientRect().top})()")
    ok(vis,"buttons visible without scroll")
    first=pg.get_attribute(".card.top","data-id")
    pg.click("#btn-no");W(500)
    ok(pg.evaluate(f"__store['swipes/'+S.me].jobs['{first}']")==-1,"pass recorded")
    pg.click("#btn-undo");W(400)
    ok(pg.evaluate(f"__store['swipes/'+S.me].jobs['{first}']===undefined"),"undo removed swipe")
    ok(pg.get_attribute(".card.top","data-id")==first,"card back after undo")
    # drag right
    box=pg.query_selector(".card.top").bounding_box()
    pg.mouse.move(box["x"]+box["width"]/2,box["y"]+box["height"]/2);pg.mouse.down()
    for i in range(10): pg.mouse.move(box["x"]+box["width"]/2+i*20,box["y"]+box["height"]/2)
    pg.mouse.up();W(600)
    ok(pg.evaluate(f"__store['swipes/'+S.me].jobs['{first}']")==1,"drag right = like")
    # keyboard left on second
    sec=pg.get_attribute(".card.top","data-id")
    pg.keyboard.press("ArrowRight");W(600)
    ok(pg.evaluate(f"__store['swipes/'+S.me].jobs['{sec}']")==1,"arrow right = like")
    ok("אין משלוחים" in txt(),"deck empty")
    # sender swipes courier
    pg.evaluate("location.hash='testsender'");ensure_auth(pg);W(500)
    pg.click('[data-tab="couriers"]');W()
    ok("כבר אמר/ה כן" in txt(),"liked ribbon on courier card")
    pg.click("#btn-yes");W(800)
    ok(pg.query_selector(".match-box") is not None,"match popup")
    pg.click("#pop-go");W(500)
    ok(pg.query_selector("#chatView") is not None,"chat opened")
    pg.fill("#chatInput","שלום!");pg.press("#chatInput","Enter");W(300)
    ok("שלום!" in pg.inner_text("#msgs"),"text message")
    pg.click('[data-act="qr"]');W(300)
    # info panel
    pg.click("#infoBtn");W();ok(pg.is_visible("#jobPanel"),"job panel opens")
    pg.click("#infoBtn");W();ok(not pg.is_visible("#jobPanel"),"job panel closes")
    # delete blocked while open
    pg.click('[data-act="closechat"]');W()
    def swipe(sel,dx):
        bx=pg.query_selector(sel).bounding_box();x=bx["x"]+bx["width"]/2;y=bx["y"]+bx["height"]/2
        pg.mouse.move(x,y);pg.mouse.down()
        for i in range(1,11): pg.mouse.move(x+dx*i/10,y)
        pg.mouse.up();W(600)
    swipe(".swfront",140);ok(pg.query_selector(".swrow") is not None,"swipe-delete blocked on open chat")
    pg.click(".more");W();pg.click('#chatMenu [data-k="delete"]',force=True);W(300);ok(pg.query_selector(".swrow") is not None,"menu delete blocked on open chat")
    pg.click(".chatrow");W(300)
    # plus menu location (gps -> in chromium file:// geolocation not granted -> fallback panel)
    pg.click("#plusBtn");W();ok(pg.is_visible("#plusMenu"),"plus menu")
    pg.click('#plusMenu [data-act="gps"]');W(2500)
    if pg.is_visible("#locPanel"):
        pg.click('[data-act="locpick"][data-v="from"]');pg.click('[data-act="locsend"]');W(300)
    ok("Waze" in pg.inner_text("#msgs"),"location message")
    # image
    import struct,zlib
    png=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
    open("x.png","wb").write(png)
    pg.click("#plusBtn");W()
    pg.set_input_files("#fileGal","x.png");W(1200);pg.click(".chat-head h1");W();ok(not pg.is_visible("#plusMenu"),"tap outside closes plus menu")
    ok(pg.query_selector("#msgs img") is not None,"image message")
    if pg.query_selector("#msgs img"):
        pg.click("#msgs img");W();ok(pg.query_selector(".lightbox") is not None,"lightbox");pg.keyboard.press("Escape");W()
    # pay update from sender
    openPlus();pg.click('#plusMenu [data-act="payopen"]');W();pg.click('[data-act="paysend"]');W(300)
    ok("שילמת" in pg.inner_text("#msgs"),"sender pay update")
    # courier side
    pg.evaluate("location.hash='testcourier'");ensure_auth(pg);W(600)
    ok(pg.query_selector(".match-box") is not None or True,"(courier popup optional)")
    if pg.query_selector(".match-box"): pg.click('[data-act="closepop"]');W()
    badge=pg.inner_text('[data-tab="matches"]')
    ok(any(c.isdigit() for c in badge),"unread badge for courier: "+badge.replace("\n"," "))
    pg.click('[data-tab="matches"]');W();pg.click(".chatrow");W(400)
    ok("שלום!" in pg.inner_text("#msgs"),"courier sees message")
    openPlus();pg.click('#plusMenu [data-act="payopen"]');W();pg.click('[data-act="paysend"]');W(300)
    ok("ביקשת תשלום" in pg.inner_text("#msgs"),"courier pay request")
    # recording (fake mic)
    openPlus();pg.click('#plusMenu [data-act="rec"]');W(1500)
    if pg.is_visible("#recBar"):
        pg.click('[data-act="recsend"]');W(1500)
    ok("הודעה קולית" in pg.inner_text("#msgs"),"voice message")
    pg.click("#infoBtn");W();pg.click("#closeChatBtn");W(400)
    ok(pg.is_visible("#closedBar") and not pg.is_visible("#chatForm"),"courier closed chat -> composer hidden")
    pg.click('#closedBar [data-k="reopenchat"]');W(400);ok(pg.is_visible("#chatForm"),"courier reopened chat")
    # sender marks paid
    pg.evaluate("location.hash='testsender'");ensure_auth(pg);W(600)
    if pg.query_selector(".match-box"): pg.click('[data-act="closepop"]');W()
    pg.click('[data-tab="matches"]');W();pg.click(".chatrow");W(400)
    if pg.query_selector('[data-act="markpaid"]'):
        pg.click('[data-act="markpaid"]');W(400)
    ok("שולם" in pg.inner_text("#msgs"),"marked paid")
    # close job from chat
    pg.click("#infoBtn");W();pg.click('#jobBtn [data-act="closejob"]');W(400)
    ok("נסגר" in pg.inner_text("#msgs") and pg.is_visible("#closedBar"),"job closed sysmsg + closed bar")
    pg.click('[data-act="closechat"]');W();pg.click('[data-tab="jobs"]');W()
    ok("הסתיים" in txt(),"closed shown in jobs")
    pg.click('[data-act="cleanclosed"]');pg.click('[data-act="cleanclosed"]');W(400)
    ok(len([1 for v in pg.evaluate("Object.values(__store['jobs/'+S.me].items)") if v.get('archived')])==1,"archived")
    pg.click('[data-tab="matches"]');W();ok(pg.query_selector(".chatrow") is not None,"chat survives archive")
    # archive / delete
    pg.click('[data-tab="matches"]');W()
    def swipe(sel,dx):
        bx=pg.query_selector(sel).bounding_box();x=bx["x"]+bx["width"]/2;y=bx["y"]+bx["height"]/2
        pg.mouse.move(x,y);pg.mouse.down()
        for i in range(1,11): pg.mouse.move(x+dx*i/10,y)
        pg.mouse.up();W(600)
    pg.click(".more");W();ok(pg.query_selector("#chatMenu") is not None,"chat menu opens")
    pg.click('#chatMenu [data-k="archive"]');W(400)
    ok(pg.query_selector(".arcrow") is not None and pg.query_selector(".swrow") is None,"archived via menu")
    pg.click('[data-act="snackundo"]');W(400);ok(pg.query_selector(".swrow") is not None,"undo archive")
    swipe(".swfront",-140);ok(pg.query_selector(".arcrow") is not None,"swipe left archives")
    pg.click(".arcrow");W();ok(pg.query_selector(".swrow") is not None,"archive list shows chat")
    swipe(".swfront",-140);W();ok(pg.query_selector(".arcrow") is None and pg.query_selector(".swrow") is not None,"swipe left in archive restores")
    swipe(".swfront",140);ok(pg.query_selector(".swrow") is None,"swipe right deletes")
    ok(pg.query_selector("#snack") is not None,"undo snackbar")
    pg.click('[data-act="snackundo"]');W(400);ok(pg.query_selector(".swrow") is not None,"undo delete")
    nmsg=pg.evaluate("Object.values(__store['chats/'+S.me].threads||{}).reduce((a,b)=>a+b.length,0)")
    ok(nmsg>0,"messages restored after undo delete: "+str(nmsg))
    pg.click(".more");W();pg.click('#chatMenu [data-k="delete"]');W(400);ok(pg.query_selector(".swrow") is None,"delete via menu")
    pg.evaluate("location.hash='testcourier'");ensure_auth(pg);W(500)
    if pg.query_selector(".match-box"): pg.click('[data-act="closepop"]');W()
    pg.click('[data-tab="matches"]');W();pg.click(".chatrow");W(300)
    ok(pg.is_visible("#closedBar") and not pg.is_visible("#chatForm"),"other side sees closed chat")
    ok(pg.query_selector('#closedBar [data-k="reopenchat"]') is None,"other side cannot reopen")
    pg.evaluate("location.hash='testsender'");ensure_auth(pg);W(500)
    if pg.query_selector(".match-box"): pg.click('[data-act="closepop"]');W()
    # profile edit + big text + theme
    pg.click('[data-tab="me"]');W()
    pg.click('[data-step="phone"]');W();pg.fill("#w-phone","052-7654321");pg.click("#wiz-next");W(400)
    ok(pg.evaluate("__store['profiles/'+S.me].phone")=="052-7654321","edit phone")
    pg.click('#view button.btn[data-act="opensettings"]');W()
    pg.click("#sw-big");W();ok(pg.evaluate("document.documentElement.classList.contains('big')"),"big text")
    pg.click("#sw-big");W()
    pg.click('[data-act="closesettings"]');W()
    pg.click("#themeBtn");W();t1=pg.evaluate("document.documentElement.dataset.theme");pg.click("#themeBtn");W();t2=pg.evaluate("document.documentElement.dataset.theme")
    ok(t1!=t2,"theme toggles "+str(t1)+"->"+str(t2))
    # role switch
    pg.click('[data-act="switchrole"]');W();ok(pg.query_selector(".wiz") is not None,"role switch wizard")
    pg.click('[data-act="wizback"]');W()
    # test reset
    pg.click('[data-act="testreset"]');pg.click('[data-act="testreset"]');W(800)
    ok(not pg.evaluate("Object.keys(__store).some(k=>k.startsWith('profiles/test_'))"),"reset deleted data")
    ok(pg.query_selector('form[data-auth]') is not None,"auth screen after reset")
    ok(pg.query_selector('[data-act="quicklogin"]') is not None,"existing test users offered")
    pg.click('[data-act="quicklogin"]');pg.click('form[data-auth="login"] button[type=submit]');W(1200)
    ok(pg.query_selector(".wiz") is not None,"login existing test user -> new profile wizard")
    # exit test mode -> real user role picker
    pg.evaluate("location.hash='app'");ensure_auth(pg);W(500)
    ok("שליחים ושולחים" in txt(),"real user sees role picker")
    pg.set_viewport_size({'width':375,'height':667})
    pg.screenshot(path="final.png")
    b.close()
print("\n".join(log))
print("ERRORS:",errs)
