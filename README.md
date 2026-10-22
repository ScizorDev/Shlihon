# שליחון · Shlihon

אפליקציית מאצ' בין שליחים לשולחים: שליחים מחליקים על משלוחים, שולחים בוחרים שליחים לפי אזור ורכב, ומאצ' הדדי פותח צ'אט לתיאום.
A courier ↔ sender matching app: couriers swipe on deliveries, senders pick couriers by area and vehicle, and a mutual match opens a chat.

- **App:** `index.html` — single file, runs as a Claude artifact ([live version](https://claude.ai/artifact/6P8Yo9ojXeTRnP5kTCRZgt)).
- **Languages:** עברית · English · Русский · العربية (RTL + LTR), light/dark.
- **Features:** swipe matching, chat (location, photos, voice, payments), live delivery status, ratings, proof of delivery, delivery codes, smart routes, recurring deliveries, ETA, courier ID verification, courier wallet, business dashboard, worldwide countries, login/registration, built-in test mode.

## Run the tests
```bash
pip install playwright pillow && playwright install chromium
tests/regress.sh
```

See [`CLAUDE.md`](CLAUDE.md) for architecture and rules, and [`docs/HISTORY.md`](docs/HISTORY.md) for the full development history.
