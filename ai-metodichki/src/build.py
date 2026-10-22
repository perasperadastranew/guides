"""Сборка методичек Mission to AI.

Запуск:  python3 ai-metodichki/src/build.py
Результат: ai-metodichki/index.html (его показывает GitHub Pages и ZenClass).
Руками index.html не правим: все правки только в папке src.
"""
import json, glob, os, sys

D = os.path.dirname(os.path.abspath(__file__)) + '/'
OUT = os.path.abspath(D + '../') + '/'


def rd(p, mode='r'):
    with open(p, mode, **({} if 'b' in mode else {'encoding': 'utf-8'})) as f:
        return f.read()


def data():
    meta = json.loads(rd(D + 'meta.json'))
    meta['figs'] = {}
    L = {}
    for f in sorted(glob.glob(D + 'lessons/*.json')):
        x = json.loads(rd(f))
        L[x['id']] = x
    meta['lessons'] = L
    meta.setdefault('titles', {})
    meta.setdefault('short', {})
    for k, x in L.items():
        meta['titles'].setdefault(k, x['title'])
    return meta


def page(imgbase='img/'):
    meta = data()
    SNIP = rd(D + 'shell_snip.html').strip().replace("background:#1c1c1c';f.src", "background:transparent;color-scheme:normal';f.src")
    css = rd(D + 'base.css') + rd(D + 'extra.css') + rd(D + 'ai.css') + '\n.embed .top,.embed .pager{display:none}.embed .where a.pill{pointer-events:none}html,body{margin:0}\n:root.embed-root{color-scheme:normal;background:transparent}body.embed{background:transparent;padding:0}\n'
    js = rd(D + 'app.js')
    js = (js.replace('__DATA__', json.dumps(meta, ensure_ascii=False).replace('</', '<\\/'))
            .replace('__IMG__', '{}').replace('__CODE__', '{}')
            .replace("var app=document.getElementById('app');", "var app=document.getElementById('app');if(window.PAAA_SHELL)return;"))
    fonts = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&family=Caveat:wght@500&display=swap">'
    body = ('<script>window.IMGBASE="' + imgbase + '"</script>\n' + SNIP + '''
<script>if(/embed/.test(location.search)){document.body.className='embed';document.documentElement.className='embed-root'}</script>
<script>if(/embed/.test(location.search)&&parent!==window){(function(){var last=0;function send(){var h=Math.ceil(document.body.getBoundingClientRect().height);if(h!==last){last=h;parent.postMessage({type:'paaa-h',h:h,hash:location.hash},'*')}}addEventListener('load',send);addEventListener('hashchange',function(){last=0;setTimeout(send,50)});setInterval(send,700)})()}</script>
<div class="wrap" id="app"></div>
<script>''' + js + '</script>\n')
    return ('''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Методички курса Mission to AI</title><meta name="robots" content="noindex">
''' + fonts + '<style>' + css + '</style></head><body>\n' + body + '</body></html>\n')


if __name__ == '__main__':
    sys.path.insert(0, D)
    import validate
    bad = [f for f in sorted(glob.glob(D + 'lessons/*.json')) if not validate.check(f)]
    if bad and '--force' not in sys.argv:
        sys.exit('Сборка остановлена: исправь ошибки в файлах выше.')
    g = page()
    with open(OUT + 'index.html', 'w', encoding='utf-8') as f:
        f.write(g)
    print('OK: index.html собран,', len(g) // 1024, 'KB')
