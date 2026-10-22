# שליחון (Shlihon) — project guide for Claude

Courier ↔ sender matching app ("Tinder for deliveries"), Hebrew-first, also English / Russian / Arabic.
Couriers swipe right/left on delivery requests; senders (private or business) post deliveries and swipe
on couriers that fit their area and vehicle. A mutual match opens a chat for coordination.

The whole app is ONE file: `index.html` (HTML + CSS + JS, no build step, no framework).
It is published as a Claude artifact: https://claude.ai/artifact/6P8Yo9ojXeTRnP5kTCRZgt
History of everything the owner asked for and what was built: `docs/HISTORY.md`.

## Source of truth & release workflow (owner's requirement)

The repository is the single source of truth. The Claude page is only a published copy of `index.html`.
After every change, in this order:
1. Edit `index.html` (and tests/docs) in the repo; run the relevant tests, then `tests/regress.sh`.
2. Commit and push.
3. Republish **this same file** to the existing page so the owner's test interface stays at the same link:
   Artifact tool → publish `file_path=<repo>/index.html`, `url=https://claude.ai/artifact/6P8Yo9ojXeTRnP5kTCRZgt`
   (omit `capabilities` to keep them; pass the full JSON below only if db rules change). Read the artifact first
   if this session hasn't published it yet. Never publish without `url` (that creates a duplicate page).
4. If a change was made directly in the Claude page instead, copy it back into the repo before anything else.

Local test interface (same two linked test screens, no Claude needed):
`python3 tests/serve.py` → http://localhost:8000 (courier + sender side by side; `app.html#testcourier`, `app.html#testsender`).

## Hard rules (from the owner — keep them in every change)

1. **Keep the test interface forever.** The owner (artifact owner only) has two connected test UIs:
   `#testcourier` and `#testsender`, plus a test bar (switch role / reset / exit).
   "Reset and start a new test" returns to the login/registration screen, and previously created
   test users can still log in. Never remove or break this; `tests/edge.py`, `tests/q1.py` check it.
2. **Worldwide**, not Israel-only: country picker for both roles; currency, payment methods and
   cities follow the country (`COUNTRY_CUR`, `payOpts`, region lists).
3. **Every UI string goes through `tr()`** and must be translated to en/ru/ar (see i18n below).
   RTL (he/ar) and LTR (en/ru) must both work.
4. **Be honest about what the platform can't do** inside a Claude artifact and say it in the UI:
   no real email sending (verification code shown in a labelled "demo inbox"), no GPS / map tiles
   (location falls back to typed address + map links; live map replaced by ETA sharing),
   no real payments or escrow (wallet is an earnings *log*), KYC is reviewed manually by the owner.
5. After every feature: run the relevant tests, then the full regression (`tests/regress.sh`).
6. Accessibility: contrast ≥ 4.5:1 (use the `--*-ink` tokens for text on soft backgrounds),
   targets ≥ 40px, every control has an accessible name, dialogs are `role=dialog aria-modal=true`
   (a global focus trap + focus-return handler exists), light and dark themes, big-text setting,
   `prefers-reduced-motion` respected. `tests/qa.py` scans every screen.

## Runtime / platform

The page runs inside a Claude artifact and uses `window.claude.use(name)` capabilities:
- `db` — realtime JSON document store. Limits: **256 KiB per document**, `limit(n)` ≤ 1000 docs per
  query (so ~1000 users per collection), 64 subscriptions per view.
- `user` — `id()`, `isOwner()`, `can("data.write")`, `me()` (scope `profile`).
- `assets` — image/audio upload (`upload:"interact"`), served at `/_blob/<id>`.
- `downloads` — `save({filename,data})` for CSV export.

Published capabilities (must be passed in full when republishing with new rules):
```json
{"db":{"rules":[
 {"path":"profiles","read":"view","write":"owner"},{"path":"profiles/{self}","write":"interact"},
 {"path":"jobs","read":"view","write":"owner"},{"path":"jobs/{self}","write":"interact"},
 {"path":"swipes","read":"view","write":"owner"},{"path":"swipes/{self}","write":"interact"},
 {"path":"chats","read":"view","write":"owner"},{"path":"chats/{self}","write":"interact"},
 {"path":"handles","read":"view","write":"owner"},{"path":"handles/{self}","write":"interact"},
 {"path":"ratings","read":"view","write":"owner"},{"path":"ratings/{self}","write":"interact"},
 {"path":"kyc","read":"owner","write":"owner"},{"path":"kyc/{self}","read":"interact","write":"interact"},
 {"path":"verify","read":"view","write":"owner"}]},
 "user":{"scopes":["profile"]},"assets":{"upload":"interact"},"downloads":true}
```
Outside Claude the page shows a "no database" screen; use the test harness (below) to run it locally.

## Data model (one document per persona in each collection)

- Persona `S.me`: real users = Claude user id; test accounts = `"test_"+accountId`. `S.realMe` = Claude id.
- `profiles/{me}` — role courier|sender, name, phone, country, vehicle, regions, pay[], kind (private/business)…
- `jobs/{me}` — `{items:{jobId:{from,fromRegion,to,toRegion,size,vehicle,when,urgent,price,cur,pay,status,created,tmpl?}}, templates:{tid:{…,recur:{days,time},active,pref,gen}}}`
- `swipes/{me}` — courier `{jobs:{jobId:±1}}`, sender `{couriers:{jobId:{courierId:±1}}}`
- match id = `jobId+"__"+courierId` (match = sender liked courier AND courier liked job)
- `chats/{me}` — `{threads:{mid:[{t,x,pay?,loc?,img?,aud?}]}, meta:{mid:{a|d|c}}, status:{mid:[{s:go|picked|arrived|done,t,proof?,code?,manual?}]}, dcode:{mid:hash}, dok:{mid}, eta:{mid}, recv:{mid}}`
- `ratings/{me}` — `{given:{mid:{to,s,x,t,role}}}`; `handles/{me}` — `{u, eh}` (username, email hash)
- `kyc/{me}` — courier ID+selfie asset ids (owner-readable only); `verify/{courierId}` — `{ok,note,t}` written by owner
- private: `data/users/<realMe>/auth` (accounts, PBKDF2 password hashes), `data/users/<realMe>/codes` (plain delivery codes)
- `compacted()` / `housekeep()` keep each own doc under ~170 KB (old chats trimmed, old closed jobs slimmed);
  a write rejected with `invalid_argument` compacts and retries once.

## Code map (index.html)

- `I18N` dict + `tr(s,flags)` (keys are the Hebrew strings), `LANGS`, `isRTL()`, `arr()`, `LOCALE()`, `setLang()`
- state `S`, `render(force)` → `renderMain()` → `setView(html)` (HTML diffing via `S.lastHtml`)
- click delegation: one `switch` on `data-act`; tabs via `data-tab`
- writes are serialized per collection with `queue(col, fn)`; `mergeMine(col, partial)`
- wizards: `profileSteps()` / `jobSteps()` with `body/valid/auto`
- `allMatches()` / `myMatches()` are memoized per task; any code that replaces `S.jobs|swipes|profiles[S.me]`
  must set `_amC=null` first (render/changed also clear it). Snapshots call `changedSoon()` (coalesced).
- Feature areas: suggested price (`suggestPrice`), ratings, proof of delivery (`openDoneDialog`, signature
  canvas), delivery code, multi-stop route (`planRoute`), recurring deliveries (`templates`, `genRecurring`),
  ETA, KYC + admin (`kycBlock`, `adminView`), courier wallet (`walletView`, `ledger`), sender dashboard
  (`dashView`), notifications (`scanEvents`, bell panel), tour (`tourSteps`), test mode (`renderTestbar`).

## i18n workflow

1. Write the Hebrew string in code as `tr("…")`.
2. Put `hebrew|english|russian|arabic` lines in a text file and run `python3 tools/addtr.py file.txt`.
   It inserts them into `I18N` and prints Hebrew keys that still have no translation (must be `[]`).

## Tests

```
pip install playwright pillow && playwright install chromium
python3 tests/build.py          # builds harness pages into /tmp/shlihon-tests
tests/regress.sh                # full regression (~20 suites, ~450 checks, ~25 min)
python3 tests/f9.py             # any single suite
python3 tests/qa.py shots       # accessibility scan of every screen (+ screenshots)
python3 tests/load.py "nc=700&ns=300&jk=10&msg=40"   # load test (700 couriers, 3000 jobs)
```
- `stub2.js` = in-memory db; `stub4.js` = localStorage db shared across tabs (the two linked test UIs).
- Suites: `f1`–`f10` (the 10 features), `run` (core flows), `extra`, `live` (two tabs realtime), `edge`,
  `auth_test`, `glob_test` (countries), `lang.py en|ru|ar` (no Hebrew leaks), `size` (doc-size limits),
  `multi` (5 couriers + sender concurrently), `q1` (focus trap, test bar, headings).
- Don't run `build.py` while `regress.sh` is running (it overwrites the harness pages).

## Known limits

- ~1,000 users per collection (db query limit); owner sees a "System load" meter in Settings → Admin.
- Chats are readable by anyone with view access to the artifact (no per-pair ACL in this store).
  A production version needs a real backend for this, for payments, push notifications and maps.
