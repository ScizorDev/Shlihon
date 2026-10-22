from authhelp import ensure_auth
import json,re
from playwright.sync_api import sync_playwright
log=[];errs=[]
def ok(c,m):log.append(("PASS " if c else "FAIL ")+m)
with sync_playwright() as p:
    b=p.chromium.launch()
    def page(url,w=375,h=667,loc='he-IL',dark=False):
        ctx=b.new_context(viewport={'width':w,'height':h},locale=loc,color_scheme='dark' if dark else 'light')
        pg=ctx.new_page();pg.route("**/fonts.googleapis.com/**",lambda r:r.abort())
        pg.on("pageerror",lambda e:errs.append(str(e)));pg.goto(url);pg.wait_for_timeout(600)
        if "ro=1" not in url: ensure_auth(pg)
        return pg
    W=lambda pg,t=350: pg.wait_for_timeout(t)
    # 1. real non-owner user: full manual courier signup
    pg=page('file:///tmp/shlihon-tests/t3.html?nonowner&uid=u_real1')
    ok(pg.query_selector("#testbar:not([hidden])") is None,"non-owner: no test bar")
    ok("שליחים ושולחים" in pg.inner_text("#view"),"non-owner: role picker")
    pg.click('[data-role="courier"]');W(pg)
    ok(pg.query_selector('[data-act="quickprofile"]') is None,"non-owner: no quick profile")
    pg.click("#wiz-next");W(pg)
    pg.fill("#w-name","דני");pg.click("#wiz-next");W(pg)
    pg.fill("#w-phone","050-1112233");pg.click("#wiz-next");W(pg)
    pg.click("#wiz-next");W(pg);ok(pg.inner_text("#wiz-err")!="","vehicle required")
    pg.click('label.tile:has(input[value="moto"])');W(pg,700)
    ok("איפה" in pg.inner_text("#wiz-title"),"auto-advance vehicle->regions")
    pg.click("#wiz-next");W(pg);ok(pg.inner_text("#wiz-err")!="","regions required")
    pg.click('[data-act="allregions"]');W(pg);ok(pg.eval_on_selector_all('input[name="regions"]:checked','e=>e.length')==8,"select all regions")
    pg.click('[data-act="allregions"]');W(pg);ok(pg.eval_on_selector_all('input[name="regions"]:checked','e=>e.length')==0,"clear regions")
    pg.click('label.chip:has(input[value="שרון"])');pg.click("#wiz-next");W(pg)
    pg.click("#wiz-next");W(pg);ok(pg.inner_text("#wiz-err")!="","pay required")
    pg.click('label.chip:has(input[value="bit"])');pg.click("#wiz-next");W(pg)
    pg.fill("#w-exp","99");pg.click("#wiz-next");W(pg);ok(pg.inner_text("#wiz-err")!="","exp range validation")
    pg.fill("#w-exp","2");pg.click("#wiz-next");W(pg,700)
    pr=pg.evaluate("__store['profiles/u_real1']")
    ok(pr and pr['regions']==['שרון'] and pr['pay']==['bit'] and pr['exp']==2 and pr['vehicle']=='moto' and not pr.get('test'),"real profile fields "+json.dumps(pr,ensure_ascii=False)[:120])
    ok(pg.query_selector("#tourEl") is not None,"tour for real user")
    # back button in tour + arrow keys
    pg.keyboard.press("ArrowLeft");W(pg);pg.keyboard.press("ArrowLeft");W(pg);pg.keyboard.press("ArrowRight");W(pg)
    ok(pg.query_selector("#tourEl .tdots i.on") is not None,"tour keyboard nav")
    pg.keyboard.press("Escape");W(pg);ok(pg.query_selector("#tourEl") is None,"tour Esc closes")
    ok(pg.evaluate("localStorage.getItem('tour_u_real1_courier')")=="true","tour not repeated flag")
    ok("כרגע אין משלוחים" in pg.inner_text("#view"),"empty deck for real courier")
    # real user doesn't see test data: create test job via owner then reload as real user
    pg.reload();W(pg,700);ok(pg.query_selector("#tourEl") is None,"tour not shown again after reload")
    # 2. readonly user
    pr=page('file:///tmp/shlihon-tests/t3.html?nonowner&ro=1&uid=u_ro')
    ok("Contributor" in pr.inner_text("#view"),"readonly banner")
    pr.click('[data-act="avgo"][data-v="register"]');W(pr);pr.fill("#r-email","ro@example.com");pr.fill("#r-user","rouser");pr.fill("#r-pass","Secret123");pr.fill("#r-pass2","Secret123");pr.click('form[data-auth] button[type=submit]');W(pr,800)
    ok(pr.inner_text("#a-err")!="" and not pr.evaluate("!!__store['data/users/u_ro/auth']"),"readonly: cannot register")
    # 3. language switch mid-wizard keeps data
    pg2=page('file:///tmp/shlihon-tests/t3.html?nonowner&uid=u_l')
    pg2.click('[data-role="sender"]');W(pg2);pg2.click('label.tile:nth-child(2)');W(pg2,700);pg2.click("#wiz-next");W(pg2);pg2.fill("#w-name","Acme");W(pg2)
    pg2.click("#langBtn");W(pg2);pg2.click('[data-l="en"]');W(pg2)
    ok(pg2.input_value("#w-name")=="Acme" and "business" in pg2.inner_text("#wiz-title").lower(),"lang switch keeps wizard data: "+pg2.inner_text("#wiz-title"))
    ok(pg2.evaluate("document.documentElement.dir")=="ltr","dir ltr in English")
    pg2.click("#langBtn");W(pg2);pg2.keyboard.press("Escape");W(pg2);ok(pg2.query_selector("#langMenu") is None,"lang menu Esc")
    pg2.click("#langBtn");W(pg2);pg2.click('[data-l="ar"]');W(pg2);ok(pg2.evaluate("document.documentElement.dir")=="rtl" and pg2.evaluate("document.documentElement.lang")=="ar","arabic rtl")
    pg2.reload();W(pg2,700);ok(pg2.evaluate("document.documentElement.lang")=="ar","lang persisted after reload")
    # 4. LTR deck swipe semantics + archive swipe in English (owner test flow)
    q=page("file:///tmp/shlihon-tests/t3.html#testsender",loc="en-US")
    ok(q.evaluate("document.documentElement.lang")=="en","auto English from device locale")
    q.click('[data-act="quickprofile"]');W(q,600);q.click('[data-act="tourskip"]');W(q)
    q.click('#view [data-act="newjob"]');W(q);q.click('[data-act="samplejob"]');W(q);q.click("#wiz-next");W(q,500)
    q.evaluate("location.hash='testcourier'");ensure_auth(q);W(q,500);q.click('[data-act="quickprofile"]');W(q,600);q.click('[data-act="tourskip"]');W(q)
    bx=q.query_selector("#btn-no").bounding_box();by=q.query_selector("#btn-yes").bounding_box()
    ok(bx["x"]<by["x"],"LTR: skip left, take right")
    box=q.query_selector(".card.top").bounding_box();x=box["x"]+box["width"]/2;y=box["y"]+box["height"]/2
    q.mouse.move(x,y);q.mouse.down();[q.mouse.move(x+i*20,y) for i in range(1,10)];q.mouse.up();W(q,600)
    ok(1 in q.evaluate("Object.values(__store['swipes/'+S.me].jobs)"),"LTR: drag right = take")
    q.evaluate("location.hash='testsender'");ensure_auth(q);W(q,500);q.click('[data-tab="couriers"]');W(q);q.click("#btn-yes");W(q,800)
    ok(q.query_selector(".match-box") is not None and "match" in q.inner_text(".match-box").lower(),"English match popup")
    q.click('[data-act="closepop"]');W(q);q.click('[data-tab="matches"]');W(q,2500)
    f=q.query_selector(".swfront").bounding_box();x=f["x"]+f["width"]/2;y=f["y"]+f["height"]/2
    q.mouse.move(x,y);q.mouse.down();[q.mouse.move(x-i*15,y) for i in range(1,11)];q.mouse.up();W(q,600)
    ok(q.query_selector(".arcrow") is not None,"LTR: swipe left archives")
    # 5. layouts: deck buttons visible across viewports/langs, no horizontal overflow
    for (w,h) in [(320,568),(375,667),(414,896),(768,1024)]:
        for L in ['he','en','ru','ar']:
            r=page(f'file:///tmp/shlihon-tests/t3.html?uid=u_lay#testcourier',w=w,h=h)
            r.evaluate(f"setLang('{L}')");W(r,400)
            if r.query_selector('[data-act="quickprofile"]'):r.click('[data-act="quickprofile"]');W(r,500)
            if r.query_selector('[data-act="tourskip"]'):r.click('[data-act="tourskip"]');W(r)
            r.evaluate("""async()=>{const db=await claude.use('db');await db.doc('profiles/zz').set({role:'sender',kind:'business',name:'A very long business name Ltd',phone:'050',region:'גוש דן',test:true});await db.doc('jobs/zz').set({items:{j9:{fromRegion:'גוש דן',from:'Long street name 123, Tel Aviv-Yafo',toRegion:'שרון',to:'Another long address 45, Herzliya Pituach',size:'חבילה גדולה',vehicle:'moto',urgent:true,price:120,pay:['cash','bit','card','paybox'],notes:'Fragile, call before arriving. Third floor with no elevator, please be careful with the box.',status:'open',created:5}}});}""")
            W(r,500)
            r.evaluate("location.hash='testsender'");ensure_auth(r);W(r,300);r.evaluate("location.hash='testcourier'");ensure_auth(r);W(r,600)
            vis=r.evaluate("(()=>{const y=document.querySelector('#btn-yes');if(!y)return 'nobtn';const b=y.getBoundingClientRect();return b.bottom<=document.querySelector('nav.tabs').getBoundingClientRect().top+1})()")
            ovf=r.evaluate("document.documentElement.scrollWidth>innerWidth+1")
            ok(vis is True and not ovf,f"layout {w}x{h} {L}: buttons visible={vis} overflow={ovf}")
            r.context.close()
    # 6. big text + dark: buttons still visible
    d=page('file:///tmp/shlihon-tests/t3.html?uid=u_big#testcourier',dark=True)
    d.evaluate("document.documentElement.classList.add('big');localStorage.setItem('bigText','true')");W(d,300)
    if d.query_selector('[data-act="quickprofile"]'):d.click('[data-act="quickprofile"]');W(d,500)
    if d.query_selector('[data-act="tourskip"]'):d.click('[data-act="tourskip"]');W(d)
    ok(d.evaluate("getComputedStyle(document.body).backgroundColor")!="rgb(255, 255, 255)","dark mode applied")
    ok(d.evaluate("document.documentElement.classList.contains('big')"),"big text persisted")
    # 7. chat size trimming
    t=page('file:///tmp/shlihon-tests/t3.html?uid=u_trim#testsender')
    t.click('[data-act="quickprofile"]');W(t,500)
    res=t.evaluate("""async()=>{const big='x'.repeat(400);const th={};for(let i=0;i<12;i++){th['m'+i+'__c']=Array.from({length:120},(_,k)=>({t:k+i*1000,x:big}))}
      __store['chats/'+S.me]={threads:th};S.chats[S.me]=__store['chats/'+S.me];S.real.chats=true;
      await sendMsg('m0__c','hello');await new Promise(r=>setTimeout(r,100));return JSON.stringify(__store['chats/'+S.me]).length}""")
    ok(res<262144,f"chat doc trimmed below limit: {res}")
    print("\n".join(log));print("FAILS:",sum(1 for l in log if l.startswith("FAIL")),"ERRORS:",errs)
    b.close()
