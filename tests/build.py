"""Builds test harness pages into /tmp/shlihon-tests from ../index.html.

The app runs inside a Claude artifact and talks to window.claude.use(...)
capabilities (db, user, assets, downloads). These stubs replace them:
  t2.html  in-memory db, owner          t3.html  in-memory, ?uid= / ?nonowner / ?ro=1
  t4.html  localStorage db shared by all tabs (two linked test UIs), owner
  t5.html  same as t4 with ?uid= / ?nonowner
  tL.html  in-memory db pre-seeded with many users (load test, see load/seed.js)
"""
import os,shutil
HERE=os.path.dirname(os.path.abspath(__file__))
OUT='/tmp/shlihon-tests';os.makedirs(OUT,exist_ok=True)
src=open(os.path.join(HERE,'..','index.html'),encoding='utf8').read()
rd=lambda f:open(os.path.join(HERE,f),encoding='utf8').read()
stub=rd('stub2.js');stub4=rd('stub4.js');seed=rd('load/seed.js')
stub2=stub.replace('isOwner:async()=>true','isOwner:async()=>!/nonowner/.test(location.search)').replace('can:async()=>true','can:async()=>/ro=1/.test(location.search)?false:true').replace('id:async()=>"u_owner"','id:async()=>(location.search.match(/uid=(\\w+)/)||[0,"u_owner"])[1]')
stub5=stub4.replace('isOwner:async()=>true','isOwner:async()=>!/nonowner/.test(location.search)').replace('id:async()=>"u_owner"','id:async()=>(location.search.match(/uid=(\\w+)/)||[0,"u_owner"])[1]')
head='<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1"><style>:root{color-scheme:light}body{margin:0;font:14px system-ui}[hidden]{display:none!important}</style></head><body>'
for f,st in [('t3.html',stub2),('t2.html',stub),('t4.html',stub4),('t5.html',stub5),('tL.html',stub+'</script><script>'+seed)]:
    open(os.path.join(OUT,f),'w',encoding='utf8').write(head+'<script>'+st+'</script>'+src+'</body></html>')
for f in os.listdir(os.path.join(HERE,'assets')):shutil.copy(os.path.join(HERE,'assets',f),OUT)
print('built into',OUT)
