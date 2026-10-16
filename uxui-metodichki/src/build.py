"""Сборка методичек Mission to UX/UI.

Запуск из корня репозитория:  python3 uxui-metodichki/src/build.py
Результат: index.html в корне репозитория (его показывает GitHub Pages и ZenClass).
Руками index.html не правим: все правки только в папке src.
"""
import json, glob, os, base64, sys

D = os.path.dirname(os.path.abspath(__file__)) + '/'
ROOT = os.path.abspath(D + '../../') + '/'


def rd(p, mode='r'):
    with open(p, mode, **({} if 'b' in mode else {'encoding': 'utf-8'})) as f:
        return f.read()


def figs_meta():
    return json.loads(rd(D + 'figmeta.json'))


def hl_bundle():
    out = ['<script>\n/* Hairline kernel. Copyright (c) Lucas Marques, MIT License. */\n' + rd(D + 'hairline-kernel.js') + '\n</script>',
           '<script>\n' + rd(D + 'hl_host.js') + '\n</script>']
    for lid, (name, _, _) in figs_meta().items():
        src = rd(D + 'figs/' + name + '.js')
        assert '</script' not in src
        out.append('<script>\n(() => {\n' + src + '\n})();\n</script>')
    return '\n'.join(out)


def data():
    man = json.loads(rd(D + 'img_manifest.json'))
    meta = json.loads(rd(D + 'meta.json'))
    meta['figs'] = figs_meta()
    L = {}
    for f in sorted(glob.glob(D + 'lessons/*.json')):
        x = json.loads(rd(f))
        for s in x['sections']:
            if s['id'] != 'real':
                continue
            bl = []
            for b in s['blocks']:
                if b.get('type') == 'shots' and any(man.get(i['img'], {}).get('kind') == 'stud' for i in b['items']):
                    continue  # работы выпускников не публикуем
                for i in b.get('items', []):
                    m = man.get(i['img'])
                    if m and m['kind'] == 'scrn':
                        i['src'] = m['src']
                bl.append(b)
            s['blocks'] = bl
        x['sections'] = [s for s in x['sections'] if s['id'] != 'real' or s['blocks']]
        L[x['id']] = x
    meta['lessons'] = L
    return meta


def page():
    meta = data()
    IMG = {'lovis_main': 'data:image/jpeg;base64,' + base64.b64encode(rd(D + 'img/lovis_main.jpg', 'rb')).decode()}
    SNIP = rd(D + 'shell_snip.html').strip().replace("background:#1c1c1c';f.src", "background:transparent;color-scheme:normal';f.src")
    css = rd(D + 'base.css') + rd(D + 'extra.css') + '\n.embed .top,.embed .pager{display:none}.embed .where a.pill{pointer-events:none}html,body{margin:0}\n:root.embed-root{color-scheme:normal;background:transparent}body.embed{background:transparent;padding:0}\n'
    js = rd(D + 'app.js')
    js = (js.replace('__DATA__', json.dumps(meta, ensure_ascii=False).replace('</', '<\\/'))
            .replace('__IMG__', json.dumps(IMG)).replace('__CODE__', '{}')
            .replace("var app=document.getElementById('app');", "var app=document.getElementById('app');if(window.PAAA_SHELL)return;"))
    fonts = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&family=Caveat:wght@500&display=swap">'
    body = ('<script>window.IMGBASE="uxui-metodichki/img/"</script>\n' + SNIP + '''
<script>if(/embed/.test(location.search)){document.body.className='embed';document.documentElement.className='embed-root'}</script>
<script>if(/embed/.test(location.search)&&parent!==window){(function(){var last=0;function send(){var h=Math.ceil(document.body.getBoundingClientRect().height);if(h!==last){last=h;parent.postMessage({type:'paaa-h',h:h,hash:location.hash},'*')}}addEventListener('load',send);addEventListener('hashchange',function(){last=0;setTimeout(send,50)});setInterval(send,700)})()}</script>
<div class="wrap" id="app"></div>
''' + hl_bundle() + '\n<script>' + js + '</script>\n')
    return ('''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Методички курса Mission to UX/UI</title><meta name="robots" content="noindex">
''' + fonts + '<style>' + css + '</style></head><body>\n' + body + '</body></html>\n')


if __name__ == '__main__':
    sys.path.insert(0, D)
    import validate
    bad = [f for f in sorted(glob.glob(D + 'lessons/*.json')) if not validate.check(f)]
    if bad:
        sys.exit('Сборка остановлена: исправь ошибки в файлах выше.')
    g = page()
    with open(ROOT + 'index.html', 'w', encoding='utf-8') as f:
        f.write(g)
    print('OK: index.html собран,', len(g) // 1024, 'KB')
