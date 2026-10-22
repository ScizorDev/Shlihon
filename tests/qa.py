from common import *
from playwright.sync_api import sync_playwright
import json,sys,os
import os
A11Y=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'a11y.js')).read()
SHOT=len(sys.argv)>1 and sys.argv[1]=="shots"
os.makedirs('/tmp/shlihon-tests/qa/shots',exist_ok=True)
res={};errs=[]
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':375,'height':667},locale='he-IL',timezone_id='Asia/Jerusalem')
    W=lambda pg,t=400:pg.wait_for_timeout(t)
    # auth screens first
    X=ctx.new_page();X.goto('file:///tmp/shlihon-tests/t4.html');W(X,800);X.evaluate("localStorage.clear();sessionStorage.clear()");X.reload();W(X,800)
    def scan(pg,label):
        for theme in ["light","dark"]:
            pg.evaluate(f"document.documentElement.dataset.theme='{theme}'");W(pg,150)
            r=pg.evaluate(A11Y)
            for x in r:
                k=(x["rule"],x["el"][:60],x["msg"][:40] if x["rule"]!="contrast" else theme)
                res.setdefault(k,{"sev":x["sev"],"msg":x["msg"],"where":set()})["where"].add(label)
            if SHOT and theme=="light":pg.screenshot(path=f'/tmp/shlihon-tests/qa/shots/{label}.png')
        pg.evaluate("document.documentElement.dataset.theme='light'")
    scan(X,"auth-login")
    if X.query_selector('[data-act="avgo"][data-v="register"]'):X.click('[data-act="avgo"][data-v="register"]');W(X)
    scan(X,"auth-register");X.close()
    A,B=setup_pair(ctx,errs,W)
    def tab(pg,t):pg.evaluate(f"S.tab='{t}';S.chat=null;S.wiz=null;S.lastHtml='';render(true)");W(pg,250)
    for lang in ["he","en","ar"]:
        for pg in (A,B):pg.bring_to_front();pg.evaluate(f"setLang('{lang}')");W(pg,200)
        if lang=="he":
            post_job(A,W);match(A,B,W)
        A.bring_to_front()
        for t in ["jobs","couriers","matches","me","settings","dash","admin"]:tab(A,t);scan(A,f"S-{t}-{lang}")
        A.evaluate("S.tab='jobs';S.lastHtml='';render(true)");W(A);A.click('#view [data-act="newjob"]');W(A)
        for i in range(8):
            scan(A,f"S-wiz{i}-{lang}")
            if A.query_selector('[data-act="samplejob"]') and i==0:pass
            nxt=A.query_selector("#wiz-next")
            if not nxt:break
            if i==0:A.fill("#w-from","הרצל 5, חולון") if A.query_selector("#w-from") else None
            if A.query_selector("#w-to"):A.fill("#w-to","בלפור 3, בת ים")
            if A.query_selector(".tile input"):A.evaluate("(()=>{const i=document.querySelector('.tile input');if(i&&!document.querySelector('.tile input:checked')){i.click()}})()")
            if A.query_selector("#w-price"):A.fill("#w-price","60")
            A.click("#wiz-next");W(A,300)
        A.evaluate("S.wiz=null");tab(A,"matches")
        A.click(".chatrow");W(A);scan(A,f"S-chat-{lang}")
        A.click("#plusBtn");W(A);scan(A,f"S-plus-{lang}");A.click("#plusBtn");W(A)
        if A.query_selector("#infoBtn"):A.click("#infoBtn");W(A);scan(A,f"S-chatinfo-{lang}");A.click("#infoBtn");W(A)
        A.click('[data-act="closechat"]');W(A)
        A.click("#bellBtn");W(A);scan(A,f"S-notif-{lang}");A.keyboard.press("Escape");W(A)
        A.click("#langBtn");W(A);scan(A,f"S-langmenu-{lang}");A.keyboard.press("Escape");W(A)
        B.bring_to_front()
        for t in ["deck","mine","matches","me","settings","wallet"]:tab(B,t);scan(B,f"C-{t}-{lang}")
        tab(B,"mine")
        if B.query_selector('.jobcard:not(.fin) [data-act="stnext"]'):
            for k in range(3):B.click('.jobcard:not(.fin) [data-act="stnext"]');W(B,300)
            scan(B,f"C-mine-active-{lang}")
            B.click('.jobcard:not(.fin) [data-act="stnext"]');W(B,400);scan(B,f"C-donedlg-{lang}");handle_done_gate(B,W)
        tab(B,"me")
        if B.query_selector('[data-act="kycopen"]'):B.click('[data-act="kycopen"]');W(B);scan(B,f"C-kyc-{lang}");B.click('[data-act="kycclose"]');W(B)
        tab(B,"mine")
        if B.query_selector('.jobcard.fin [data-act="rate"]'):B.click('.jobcard.fin [data-act="rate"]');W(B);scan(B,f"C-rate-{lang}");B.keyboard.press("Escape");W(B)
        if lang=="he":
            B.evaluate("S.tour={i:-1,role:'courier'};tourGo(0)");W(B,500);scan(B,"C-tour0-he");B.click("#tourNext");W(B,400);scan(B,"C-tour1-he")
            while B.query_selector("#tourNext"):B.click("#tourNext");W(B,100)
    sev={"high":0,"med":1,"low":2}
    items=sorted(res.items(),key=lambda kv:(sev[kv[1]["sev"]],kv[0][0]))
    for k,v in items:
        w=sorted(v["where"]);print(f'[{v["sev"]}] {k[0]:9s} {k[1]:60s} {v["msg"][:90]} @{len(w)} {",".join(w[:4])}')
    print("TOTAL",len(items),"ERR",errs[:3])
    b.close()
