# Adds translations. Input file: one line per string, "hebrew|english|russian|arabic". Prints Hebrew tr("...") keys still missing.
import json,sys
import os
p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html');s=open(p).read()
i=s.index('const I18N=')+len('const I18N=');j=s.index(';\nconst LANGS')
D=json.loads(s[i:j])
for line in open(sys.argv[1]):
    line=line.rstrip('\n')
    if not line.strip():continue
    he,en,ru,ar=line.split('|');D['en'][he]=en;D['ru'][he]=ru;D['ar'][he]=ar
s=s[:i]+json.dumps(D,ensure_ascii=False)+s[j:]
open(p,'w').write(s)
import re
keys=[k for k in re.findall(r'tr\("((?:[^"\\])*)"',s) if re.search('[֐-׿]',k) and k not in D['en']]
print("missing:",sorted(set(keys)))
