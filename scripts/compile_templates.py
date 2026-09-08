from pathlib import Path
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('app/templates'))
base = Path('app/templates')
ok = fail = 0
for p in sorted(base.rglob('*.html')):
    rel = p.relative_to(base).as_posix()
    try:
        env.get_template(rel)
        print('OK  ', rel); ok += 1
    except Exception as e:
        print('FAIL', rel, '->', e); fail += 1
print('done ok=%d fail=%d' % (ok, fail))