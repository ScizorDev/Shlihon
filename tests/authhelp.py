def ensure_auth(pg):
    pg.wait_for_timeout(350)
    if not pg.query_selector('form[data-auth]'): return False
    if pg.query_selector('form[data-auth="login"]'):
        pg.click('[data-act="avgo"][data-v="register"]');pg.wait_for_timeout(300)
    n=pg.evaluate("Math.random().toString(36).slice(2,8)")
    pg.fill('#r-email',f'u{n}@example.com');pg.fill('#r-user',f'u{n}');pg.fill('#r-pass','Test1234');pg.fill('#r-pass2','Test1234')
    pg.click('form[data-auth="register"] button[type=submit]');pg.wait_for_timeout(1300)
    code=pg.inner_text('.mail .code').strip();pg.fill('#v-code',code);pg.click('form[data-auth="verify"] button[type=submit]');pg.wait_for_timeout(1300)
    return True

def handle_done_gate(B,W=None,code=None,mode="sig"):
    B.wait_for_timeout(300)
    if not B.query_selector("#doneDlg"): return False
    if B.query_selector("#dcode"):
        code=code or B.evaluate("(S.codes||{})[S.doneMid]")
        if code: B.fill("#dcode",code)
    if B.query_selector('#doneDlg [data-act="proofkind"][data-k="sig"]'):
        if mode=="sig":
            B.click('#doneDlg [data-act="proofkind"][data-k="sig"]');B.wait_for_timeout(150)
            bx=B.query_selector("#sigCanvas").bounding_box();x=bx["x"]+20;y=bx["y"]+bx["height"]/2
            B.mouse.move(x,y);B.mouse.down()
            for i in range(1,15):B.mouse.move(x+i*15,y+((-1)**i)*12)
            B.mouse.up()
    B.click("#doneBtn");B.wait_for_timeout(900);return True
