from authhelp import ensure_auth
from playwright.sync_api import sync_playwright
log=[];errs=[]
def ok(c,m):log.append(("PASS " if c else "FAIL ")+m)
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':375,'height':667},locale='he-IL',timezone_id='Asia/Jerusalem')
    pg=ctx.new_page();pg.route("**/fonts.googleapis.com/**",lambda r:r.abort());pg.on("pageerror",lambda e:errs.append(str(e)))
    W=lambda t=350:pg.wait_for_timeout(t)
    pg.goto('file:///tmp/shlihon-tests/t2.html#testsender');W(600);ensure_auth(pg);pg.click('[data-act="quickprofile"]');W(600)
    while pg.query_selector("#tourNext"):pg.click("#tourNext");W(150)
    def to_price(size_idx,when,from_r=None,to_r=None):
        pg.click('#view [data-act="newjob"]');W()
        if from_r:pg.select_option("#w-fromRegion",from_r)
        pg.fill("#w-from","A st 1");pg.click("#wiz-next");W()
        if to_r:pg.select_option("#w-toRegion",to_r)
        pg.fill("#w-to","B st 2");pg.click("#wiz-next");W()
        pg.click(f"label.tile:nth-child({size_idx})");W(700);pg.click("#wiz-next");W()
        pg.click(f'label.tile:has(input[value="{when}"])');W();pg.click("#wiz-next");W()
    def val():
        t=pg.get_attribute('[data-act="usesuggest"]','data-v');return float(t)
    to_price(2,"flex");ok(pg.query_selector(".pricehint") is not None,"price hint shown");base=val();ok(base>0,f"base suggestion {base}")
    ok("₪" in pg.inner_text(".pricehint"),"in shekels")
    pg.click('[data-act="usesuggest"]');W();ok(float(pg.input_value("#w-price"))==base,"apply suggestion fills price")
    pg.click('[data-act="wizback"]');W();pg.click('label.tile:has(input[value="asap"])');W();pg.click("#wiz-next");W();u=val();ok(u>base,f"urgent raises ({u}>{base})")
    pg.click('[data-act="wizback"]');W();pg.click('[data-act="wizback"]');W();pg.click('[data-act="wizback"]');W();pg.click('[data-act="wizback"]');W()
    pg.select_option("#w-toRegion","שרון");pg.click("#wiz-next");W();pg.click("#wiz-next");W();pg.click("#wiz-next");W();pg.click("#wiz-next");W()
    c=val();ok(c>u,f"cross-region raises ({c}>{u})");ok("בין אזורים" in pg.inner_text(".pricehint"),"reason shown")
    # truck/furniture
    pg.click('[data-act="wizback"]');W();pg.click('[data-act="wizback"]');W();pg.click('[data-act="wizback"]');W()
    pg.click("label.tile:nth-child(5)");W(700);pg.click("#wiz-next");W();pg.click("#wiz-next");W();f=val();ok(f>c*3,f"furniture/truck much higher ({f})")
    pg.click('[data-act="wizback"]');W();pg.click('[data-act="wizback"]');W();pg.click('[data-act="wizback"]');W();pg.click('[data-act="wizback"]');W();pg.click('[data-act="wizback"]');W();pg.click('[data-act="wizback"]');W()
    # history median: post 3 small jobs with prices 30,40,50
    for pr in [30,40,50]:
        to_price(2,"flex");pg.fill("#w-price",str(pr));pg.click("#wiz-next");W();pg.click("#wiz-next");W();pg.click("#wiz-next");W(400)
    to_price(2,"flex");ok("חציון" in pg.inner_text(".pricehint") and pg.get_attribute('[data-act="usesuggest"]','data-v')=="40","median of similar jobs = 40")
    pg.click("#langBtn");W();pg.click('[data-l="en"]');W();ok("Suggested price" in pg.inner_text(".pricehint"),"translated")
    print("\n".join(log));print("FAILS",sum(l.startswith("FAIL") for l in log),"ERR",errs)
    b.close()
