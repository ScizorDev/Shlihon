from authhelp import ensure_auth, handle_done_gate as _hdg
def setup_pair(ctx,errs,W):
    def pg_(h):
        pg=ctx.new_page();pg.route("**/fonts.googleapis.com/**",lambda r:r.abort());pg.on("pageerror",lambda e:errs.append(str(e)));pg.goto('file:///tmp/shlihon-tests/t4.html#'+h);pg.wait_for_timeout(700);return pg
    A=pg_('testsender');A.evaluate("localStorage.clear();sessionStorage.clear()");A.reload();W(A,700);ensure_auth(A)
    A.click('[data-act="quickprofile"]');W(A,600)
    while A.query_selector("#tourNext"):A.click("#tourNext");W(A,120)
    B=pg_('testcourier');ensure_auth(B);B.click('[data-act="quickprofile"]');W(B,600)
    while B.query_selector("#tourNext"):B.click("#tourNext");W(B,120)
    return A,B
def post_job(A,W,price=None):
    A.click('[data-tab="jobs"]');W(A);A.click('#view [data-act="newjob"]');W(A);A.click('[data-act="samplejob"]');W(A)
    A.click("#wiz-next");W(A,500)
def match(A,B,W):
    B.bring_to_front();B.click('[data-tab="deck"]');W(B,400);B.click("#btn-yes");W(B,500)
    A.bring_to_front();W(A,500);A.click('[data-tab="couriers"]');W(A);A.click("#btn-yes");W(A,900)
    if A.query_selector('[data-act="closepop"]'):A.click('[data-act="closepop"]');W(A)
    B.bring_to_front();W(B,600)
    if B.query_selector('[data-act="closepop"]'):B.click('[data-act="closepop"]');W(B)
def courier_done(B,W):
    B.click('[data-tab="mine"]');W(B)
    for i in range(4):
        if B.query_selector('.jobcard:not(.fin) [data-act="stnext"]'):B.click('.jobcard:not(.fin) [data-act="stnext"]');W(B,500)
        handle_done_gate(B,W)
def handle_done_gate(B,W,code=None):
    return _hdg(B,W,code)
