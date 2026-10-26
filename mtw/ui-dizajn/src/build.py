"""Сборка вводной методички к модулю UI (Mission to Web) на движке методичек Mission to UX/UI.

Запуск из корня репозитория:  python3 mtw/ui-dizajn/src/build.py
Результат: mtw/ui-dizajn/index.html. Руками его не правим: тексты — в ui-start.json,
курс и ссылки — в meta.json, интерактив «Рентген экрана» — в xray.html / xray.css / xray.js.
Вёрстка, стили и блоки берутся из uxui-metodichki/src, чтобы дизайн совпадал с методичками UX/UI.
"""
import json, os, re

D = os.path.dirname(os.path.abspath(__file__)) + '/'
OUT = os.path.abspath(D + '../index.html')
UX = os.path.abspath(D + '../../../uxui-metodichki/src') + '/'


def rd(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


SHORT = r'(?:[вВиИаАкКсСуУоОяЯ]|не|Не|на|На|по|По|за|За|из|Из|от|От|до|До|для|Для|но|Но|ни|же|ли|бы|без|Без|при|что|как|под|над)'


def typo(s):
    """Неразрывные пробелы после коротких слов, перед тире и между числом и словом."""
    s = re.sub(r'(?<![\w\-])' + SHORT + r' (?=\S)', lambda m: m.group(0)[:-1] + '\u00a0', s)
    s = re.sub(r' (?=—)', '\u00a0', s)
    return re.sub(r'(\d) (?=[А-Яа-яЁёa-z×%₽])', '\\1\u00a0', s)


def typo_html(h):
    out, pos = [], 0
    for m in re.finditer(r'<[^>]+>', h):
        out.append(typo(h[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(typo(h[pos:]))
    return ''.join(out)


def patch(js, old, new):
    assert js.count(old) == 1, 'не нашёл в app.js: ' + old[:60]
    return js.replace(old, new)


def page():
    meta = json.loads(rd(D + 'meta.json'))
    lesson = json.loads(rd(D + 'ui-start.json'))
    meta['lessons'] = {lesson['id']: lesson}
    meta['html'] = {'xray': typo_html(rd(D + 'xray.html'))}
    meta['figs'] = {}

    js = rd(UX + 'app.js')
    js = patch(js, 'var R={', "var R={\n html:function(b){return (D.html||{})[b.id]||''},")
    # курс и подписи — Mission to Web
    js = patch(js, "PERASPERADASTRA\\nUX/UI-DESIGNER", "PERASPERADASTRA\\nMISSION TO WEB")
    js = patch(js, "<footer>Perasperadastra · Mission to UX/UI · примеры приложений приведены как наблюдение со стороны</footer>",
               "<footer>Perasperadastra · Mission to Web · Модуль «UI-дизайн»</footer>")
    # уроки, которых нет на этой странице, открываются как отдельные методички
    js = patch(js, "h+='<a class=\"pill '+c+'\" href=\"#/'+id+'\">'",
               "var X=(D.ext||{})[id];h+='<a class=\"pill '+c+'\" href=\"'+(X||'#/'+id)+'\"'+(X?' target=\"_blank\" rel=\"noopener\"':'')+'>'")
    js = patch(js, "'<a href=\"#/'+prev+'\">← Предыдущий урок<b>'",
               "'<a href=\"'+((D.ext||{})[prev]||'#/'+prev)+'\" target=\"_blank\" rel=\"noopener\">← Предыдущий урок<b>'")
    js = patch(js, "(next&&D.lessons[next]?'<a class=\"next\" href=\"#/'+next+'\">",
               "(next&&(D.lessons[next]||(D.ext||{})[next])?'<a class=\"next\" href=\"'+((D.ext||{})[next]||'#/'+next)+'\" target=\"_blank\" rel=\"noopener\">")
    js = patch(js, "<a href=\"#/\">← Все методички</a>", "<a href=\"'+D.hub+'\" target=\"_blank\" rel=\"noopener\">← Все методички</a>")
    # крупный номер в шапке — номер модуля, а не урока: номера уроков в учебных текстах не пишем
    js = patch(js, "<span class=\"lnum\" aria-hidden=\"true\">'+('0'+(ORDER.indexOf(id)+(ORDER[0]==='s0'?0:1))).slice(-2)+'</span>",
               "<span class=\"lnum\" aria-hidden=\"true\">'+(D.lnum||'')+'</span>")
    # оглавления курса на этой странице нет: всегда показываем урок
    js = patch(js, "else{last='';home();window.scrollTo(0,0)}",
               "else{if(last!==D['default']){lesson(D['default']);window.scrollTo(0,0)}last=D['default']}")
    js = (js.replace('__DATA__', json.dumps(meta, ensure_ascii=False).replace('</', '<\\/'))
            .replace('__IMG__', '{}').replace('__CODE__', '{}'))
    js = patch(js, "var app=document.getElementById('app');", "var app=document.getElementById('app');if(window.PAAA_SHELL)return;")

    xjs = rd(D + 'xray.js')
    xjs = re.sub(r"'([^'\n]*[а-яё][^'\n]*)'", lambda m: "'" + typo(m.group(1)) + "'", xjs)

    snip = rd(UX + 'shell_snip.html').strip().replace("background:#1c1c1c';f.src", "background:transparent;color-scheme:normal';f.src")
    css = (rd(UX + 'base.css') + rd(UX + 'extra.css') + rd(D + 'xray.css') +
           '\n.embed .top,.embed .pager{display:none}.embed .where a.pill{pointer-events:none}html,body{margin:0}\n'
           ':root.embed-root{color-scheme:normal;background:transparent}body.embed{background:transparent;padding:0}\n')
    fonts = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">'
    body = (snip + '''
<script>if(/embed/.test(location.search)){document.body.className='embed';document.documentElement.className='embed-root'}</script>
<script>if(/embed/.test(location.search)&&parent!==window){(function(){var last=0;function send(){var h=Math.ceil(document.body.getBoundingClientRect().height);if(h!==last){last=h;parent.postMessage({type:'paaa-h',h:h,hash:location.hash},'*')}}addEventListener('load',send);addEventListener('hashchange',function(){last=0;setTimeout(send,50)});setInterval(send,700)})()}</script>
<div class="wrap" id="app"></div>
<script>''' + js + '</script>\n<script>\n' + xjs + '</script>\n')
    return ('<!doctype html>\n<html lang="ru"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<title>UI-дизайн: методичка</title><meta name="robots" content="noindex">\n'
            + fonts + '<style>' + css + '</style></head><body>\n' + body + '</body></html>\n')


if __name__ == '__main__':
    g = page()
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(g)
    print('OK:', os.path.relpath(OUT), len(g) // 1024, 'KB')
