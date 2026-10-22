"""Run the app locally with the same test interface as the Claude page.

    python3 tests/serve.py          -> http://localhost:8000

Opens two linked test screens (they share one local database through
localStorage, exactly like #testcourier / #testsender in the Claude page):
    http://localhost:8000/app.html#testcourier
    http://localhost:8000/app.html#testsender
Data lives only in this browser. "Reset" in the test bar clears it.
Rebuilds from ../index.html on every page load, so edits show after a refresh.
"""
import http.server,os,socketserver,sys
HERE=os.path.dirname(os.path.abspath(__file__))
PORT=int(sys.argv[1]) if len(sys.argv)>1 else 8000
def page():
    src=open(os.path.join(HERE,'..','index.html'),encoding='utf8').read()
    stub=open(os.path.join(HERE,'stub4.js'),encoding='utf8').read()
    return ('<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1"><title>שליחון (local)</title>'
      '<style>body{margin:0}[hidden]{display:none!important}</style></head><body><script>'+stub+'</script>'+src+'</body></html>').encode('utf8')
INDEX='''<!doctype html><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1"><title>שליחון – בדיקות</title>
<style>body{font:18px system-ui;max-width:900px;margin:24px auto;padding:0 16px}a{display:inline-block;margin:6px 8px 6px 0;padding:12px 18px;border-radius:12px;background:#C2410C;color:#fff;text-decoration:none;font-weight:600}
.f{display:flex;gap:12px;flex-wrap:wrap}iframe{width:390px;height:760px;border:1px solid #ccc;border-radius:16px}</style>
<h1>שליחון – ממשקי בדיקה מקומיים</h1>
<p><a href="app.html#testcourier" target="_blank">שליח בדיקה</a><a href="app.html#testsender" target="_blank">שולח בדיקה</a><a href="app.html" target="_blank">האפליקציה הרגילה</a></p>
<div class="f"><iframe src="app.html#testcourier" title="שליח בדיקה"></iframe><iframe src="app.html#testsender" title="שולח בדיקה"></iframe></div>'''
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path=self.path.split('?')[0].split('#')[0]
        body=page() if path=='/app.html' else INDEX.encode('utf8') if path in('/','/index.html') else None
        if body is None:self.send_response(404);self.end_headers();return
        self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
    def log_message(self,*a):pass
socketserver.TCPServer.allow_reuse_address=True
with socketserver.TCPServer(('',PORT),H) as s:
    print(f'Shlihon test UI: http://localhost:{PORT}  (Ctrl+C to stop)');s.serve_forever()
