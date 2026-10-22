#!/bin/bash
# Full regression. Usage: tests/regress.sh [report-file]
# Requires: python3, playwright (pip install playwright && playwright install chromium), Pillow
cd "$(dirname "$0")" && python3 build.py || exit 1
out=${1:-/tmp/shlihon-tests/report.txt}; : > $out; mkdir -p /tmp/shlihon-tests/logs
for t in f1 f2 f3 f4 f5 f6 f7 f8 f9 f10 size multi q1 edge auth_test run extra live glob_test; do
  echo "== $t" >> $out; timeout 600 python3 $t.py > /tmp/shlihon-tests/logs/$t.txt 2>&1
  grep -v proxy /tmp/shlihon-tests/logs/$t.txt | grep -E 'FAIL|Traceback' | cut -c1-200 >> $out
  echo "pass=$(grep -c '^PASS' /tmp/shlihon-tests/logs/$t.txt)" >> $out
done
for l in en ru ar; do echo "== lang $l" >> $out; timeout 300 python3 lang.py $l 2>&1 | grep -E 'ERR|Traceback' | cut -c1-150 >> $out; done
echo DONE >> $out; cat $out
