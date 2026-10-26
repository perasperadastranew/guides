# Сборка короткой версии «Как начать в AI-индустрии»
# База — orig.html (короткая версия из репозитория), поверх — новая структура.
import re, os
D = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(D, 'orig.html'), encoding='utf-8').read()
OUT = os.path.join(D, '..', 'index-short.html')

def cut(a, b):
    return s[s.index(a):s.index(b)]
def sec_body(id_):
    """Тело секции после .head"""
    a = s.index('<section class="step" id="%s">' % id_)
    b = s.index('</section>', a)
    t = s[a:b]
    i = t.index('</div></div>', t.index('<div class="head">')) + len('</div></div>')
    return t[i:].strip()
def sec_txt(id_):
    a = s.index('<section class="step" id="%s">' % id_)
    t = s[a:s.index('</section>', a)]
    m = re.search(r'<div class="txt"><h2>.*?</h2>(.*?)</div></div>', t, re.S)
    return m.group(1).strip()
def head(n, small, title, txt=''):
    return '<div class="head"><div class="num">%s<small>%s</small></div><div class="txt"><h2>%s</h2>%s</div></div>' % (n, small, title, txt)
def section(id_, n, small, title, txt, body):
    return '<section class="step" id="pg-%s">%s\n%s\n</section>\n\n' % (id_, head(n, small, title, txt), body)
def part(id_, roman, title, txt):
    return '<div class="part" id="pg-%s"><h2>Часть %s. <span class="s">%s</span></h2><p>%s</p></div>\n\n' % (id_, roman, title, txt)
def nofn(t):
    return re.sub(r'<p class="fn">.*?</p>', '', t, flags=re.S)

out = []
# ---------- шапка
hdr = s[s.index('<header>'):s.index('<div class="part" id="pg-p1">')]
hdr = re.sub(r'<figure class="dio".*?</figure>', '', hdr, flags=re.S)
hdr = re.sub(r'<p class="lead">.*?</p>', '<p class="lead">Гайд для старта в AI-креативе: что на самом деле происходит на рынке, какие проекты заказывают и сколько они стоят, как пройти путь до первого заказа, чем текстовые нейросети отличаются от визуальных и за какие подписки платить.</p>', hdr, flags=re.S)
hdr = re.sub(r'<nav class="need".*?</nav>', '''<nav class="need" aria-label="Разделы">
<a href="#pg-p1"><b><i>I</i>Рынок</b><span>Что происходит, мифы, заказы и цены</span></a>
<a href="#pg-p2"><b><i>II</i>Пошагово</b><span>От цели до первого заказа</span></a>
<a href="#pg-p3"><b><i>III</i>Нейросети</b><span>Текстовые и визуальные</span></a>
<a href="#pg-p4"><b><i>IV</i>Подписки</b><span>За что платить и сколько</span></a>
<a href="#pg-end"><b><i>→</i>Итог</b><span>Выводы, эфир и гайды</span></a>
</nav>''', hdr, flags=re.S)
out.append(hdr)

# ================= ЧАСТЬ I. РЫНОК
out.append(part('p1', 'I', 'Рынок', 'Что происходит на самом деле, какие мифы мешают, какие проекты заказывают и что изменили нейросети.'))

# --- I.01 Что происходит: башня по годам + тезисы
YEARS = [
 ('2020', 'GPT-3', 'Нейросеть пишет связный текст по запросу'),
 ('2021', 'DALL·E', 'Первые картинки по текстовому описанию'),
 ('2022', 'Midjourney и ChatGPT', 'Нейросети становятся доступны всем'),
 ('2023', 'GPT-4, Firefly', 'Нейросети встраивают в рабочие программы'),
 ('2024', 'Sora, Kling', 'Видео по описанию и по картинке'),
 ('2025', 'Nano Banana, Veo 3', 'Правка по фото, видео сразу со звуком'),
 ('2026', 'Агенты', 'ИИ сам выполняет задачи на несколько часов'),
]
blocks = ''.join('<li style="--i:%d"><i></i><b>%s</b><span><em>%s</em>%s</span></li>' % (i, y, n, d) for i, (y, n, d) in enumerate(YEARS))
tower = '<figure class="yt" aria-label="Башня по годам: с 2020 по 2026 год нейросети надстраивают новые этажи"><ol>%s</ol><figcaption class="micro">Каждый год — новый этаж</figcaption></figure>' % blocks

TH = [
 ('5 дней', 'Скорость', 'понадобилось ChatGPT, чтобы набрать первый миллион пользователей. Сейчас у него около 900 млн человек в неделю. А длина задач, которые ИИ выполняет сам, удваивается примерно каждые 4 месяца.'),
 ('102 000', 'Сокращения', 'человек потеряли работу в 130 технологических компаниях к середине мая 2026 года. В апреле ИИ назвали причиной четверти всех увольнений — в 2025-м было около 5%.'),
 ('9%', 'Но', 'компаний говорят, что ИИ действительно полностью заменил какие-то роли. При этом почти 6 из 10 называют ИИ причиной сокращений, хотя причина финансовая. Сэм Альтман называет это AI washing: на ИИ сваливают увольнения, которые всё равно бы случились.'),
 ('700', 'Klarna', 'В 2024 году компания хвасталась, что чат-бот делает работу 700 операторов. В 2025-м снова начала нанимать людей: качество поддержки упало.'),
 ('16%', 'Спрос', 'вакансий дизайнеров и художников на hh.ru в 2026 году требуют навыков работы с нейросетями — больше, чем в любой другой профессии.'),
]
th = ''.join('<li><b>%s</b><span class="micro">%s</span><p>%s</p></li>' % t for t in TH)
out.append(section(1, '01', 'Что происходит', 'Что происходит <span class="s">на рынке</span>',
  '<p>Нейросети за шесть лет пришли в каждую профессию. Разберём по шагам: как быстро это случилось, что на самом деле с увольнениями и кто сейчас нужен рынку.</p>',
  tower + '\n<ol class="th">' + th + '</ol>\n<p class="tip"><b>Вывод.</b> «Всех сокращают из-за ИИ» — часто отговорка. Нейросети не отменяют дизайнеров, они отменяют средний результат. Людей, которые умеют с ними работать, ищут активнее остальных.</p>'))

# --- I.02 Перепись населения
ST = [
 ('Отрицание', 'Homo Skepticus', '«Я всё рисую руками, ИИ — это баловство»'),
 ('Гнев', 'Homo Haterus', 'Пишет в комментариях, что нейросети — воровство и конец искусства'),
 ('Торг', 'Homo Figmaticus', '«Ладно, баннеры пусть делает, но в моей Figma — только я»'),
 ('Депрессия', 'Homo Panicus', 'Увидел рилс «нейросеть заменит дизайнеров» и уже обновляет резюме'),
 ('Принятие', 'Homo Claudius', 'Работает с нейросетями как с командой: идея и решения на нём, рутина — на ИИ'),
]
st = ''.join('<li style="--i:%d"><img src="img/hc-%d.webp" alt="" loading="lazy"><span class="micro">%02d · %s</span><b>%s</b><p>%s</p></li>' % (i, i + 1, i + 1, a, b, c) for i, (a, b, c) in enumerate(ST))
PL = ['Рутину забирает ИИ: ресайзы, заглушки, документация. Время остаётся на идею', 'Один дизайнер с нейросетями закрывает работу небольшой студии', '3D, моушн и видео доступны без отдельной команды', 'Живое и авторское ценится как премиум на фоне одинакового', 'Выделиться через блог проще, чем когда-либо']
MI = ['Молодых нанимают меньше: занятость 22–25-летних в профессиях с ИИ ниже на 15%', 'Клиент ждёт «сайт за 5 секунд» и спрашивает, почему так долго', 'Простые задачи уходят к сервисам и самим клиентам', 'Средний уровень больше ничего не стоит', 'Инструменты устаревают за полгода — учиться приходится постоянно']
pm = '<div class="pm"><div class="pp"><h3>Плюсы <span>достаются растущим</span></h3><ol>%s</ol></div><div class="mn"><h3>Минусы <span>бьют по средним</span></h3><ol>%s</ol></div></div>' % (''.join('<li>%s</li>' % x for x in PL), ''.join('<li>%s</li>' % x for x in MI))
out.append(section(2, '02', 'Перепись', 'Пять стадий <span class="s">принятия</span>',
  '<p>Дизайнеры по-разному встречают нейросети. Почти все проходят одни и те же стадии — вопрос только в том, на какой задержаться.</p>',
  '<ol class="cen">' + st + '</ol>\n' + pm + '\n<p class="tip"><b>Почти каждый минус бьёт по тем, кто делает средне и не учится.</b> Почти каждый плюс достаётся тем, кто растёт и показывает себя.</p>'))

# --- I.03 Мифы и реальность + 20/80
MY = [
 ('«AI-креаторов уже слишком много»', 'Креаторов много, хороших мало. Большинство — выпускники быстрых курсов, которые делают средний результат. А среднее ничего не стоит: нейросеть подтягивает до среднего всех. Поэтому сильная идея и вкус ценятся ещё больше, чем раньше.'),
 ('«Нейросеть делает всё за 5 минут»', 'Генерация — малая часть работы. Бриф, идея, отбор, доводка руками и согласования остаются за тобой. Клиент платит за решение задачи, а не за минуты генерации.'),
 ('«Освою нейросети — и заказы пойдут»', 'Тех, кто «что-то умеет в нейросетях», много. Тех, кому можно доверить проект целиком, мало: кто понимает задачу, договаривается о сроках и правках и сдаёт результат вовремя. Умение вести проект и работать с заказчиком — то, на что почти никто не делает ставку.'),
]
my = ''.join('<li><div class="pr"><b>%s</b></div><i aria-hidden="true">→</i><div class="so">%s</div></li>' % m for m in MY)
cells = ''.join('<i%s></i>' % (' class="a"' if k < 20 else '') for k in range(100))
split = '''<div class="split"><div class="cells" aria-hidden="true">%s</div><div class="sk"><div><b class="a">20%%</b><span>Технические навыки в нейросетях: промпты, модели, настройки. Обычно на курсах дают только их</span></div><div><b>80%%</b><span>Визуальный опыт, дизайн-процесс, графдизайн, понимание кино и работа с клиентом — то, что по-настоящему даёт результат</span></div></div></div>''' % cells
out.append(section(3, '03', 'Мифы', 'Мифы <span class="s">и реальность</span>',
  '<p>Три убеждения, с которыми многие заходят в AI-креатив, и как всё устроено на самом деле.</p>',
  '<div class="ps my"><div class="psh"><span class="micro">Миф</span><span class="micro">Реальность</span></div><ol>' + my + '</ol></div>\n<p class="micro" style="margin:56px 0 14px">Из чего складывается результат</p>\n' + split +
  '\n<p class="tip"><b>Не гоняйся за каждой новой нейросетью.</b> Выдели на обновления час в неделю, а остальное время вкладывай в насмотренность, дизайн и работу с людьми.</p>'))

# --- I.04 Проекты и цены (бывшая 03): без ссылок без картинок + график «часы × цена»
b3 = sec_body('pg-3')
b3 = re.sub(r'<div class="exs">.*?</div></div>', '', b3, flags=re.S)
# в слайдере оставляем только карточки с картинкой или видео
b3 = re.sub(r'<a class="cs t"[^>]*>(?:(?!</a>).)*?<span class="ty"[^>]*>[^<]*</span><span class="cn">.*?</a>', '', b3, flags=re.S)
CASE = {
 'cases/v-knives.jpg': ('https://dprofile.ru/case/178358/simple-knives-kollekciia-nozei', 'Simple Knives · Анастасия Грачева'),
 'cases/mako.webp': ('https://www.behance.net/gallery/255746473/MAKO-AI-Mascot', 'МАКО · Диана Херман'),
 'cases/v-lappi.jpg': ('https://perasperadastra.ru/sreda-lappi', 'Лаппи'),
 'cases/hronos-box.webp': ('https://perasperadastra.ru/sreda-hronos', 'Хронос'),
 'cases/eaglips.webp': ('https://dprofile.ru/case/173955/eaglips', 'Eaglips · Милана Гавриченко'),
 'img/case-lumera-1.webp': ('https://dprofile.ru/case/174067/lumera', 'Lumera · Лейла Исхакова'),
 'cases/mofu.webp': ('https://dprofile.ru/case/179802/mofu-mofu-pusistye-obvesy', 'mofu-mofu · Арина Галимова'),
}
def _fig(m):
    src = m.group(1)
    if src not in CASE: return m.group(0)
    u, who = CASE[src]
    return '<figure class="lk"><a href="%s" target="_blank" rel="noopener"><img src="%s" alt="%s" loading="lazy"></a><figcaption><b>%s</b><a href="%s" target="_blank" rel="noopener">%s ↗</a></figcaption></figure>' % (u, src, who, m.group(2), u, who)
b3 = re.sub(r'<figure><img src="([^"]+)" alt="[^"]*" loading="lazy"><figcaption><b>([^<]*)</b></figcaption></figure>', _fig, b3)
VG = [('https://perasperadastra.ru/klip', None, 'https://static.tildacdn.com/vide3137-3335-4439-b138-373930326161/klip-hero-final.mp4', 'AI-клип', 'Хаски'),
      ('https://perasperadastranew.github.io/guides/rolik-po-foto/', 'cases/godovshina.webp', None, 'Фильм по фото', 'Годовщина родителей'),
      ('https://perasperadastra.ru/sreda-lappi', 'cases/v-lappi.jpg', 'cases/v-lappi.mp4', 'Анимация персонажа', 'Лаппи'),
      ('https://dprofile.ru/case/178358/simple-knives-kollekciia-nozei', 'cases/v-knives.jpg', 'cases/v-knives.mp4', 'Рекламный ролик продукта', 'Simple Knives · Анастасия Грачева')]
def _vf(u, img, vid, cap, who):
    if vid:
        med = '<video muted loop playsinline preload="%s"%s data-src="%s"></video>' % ('none' if img else 'metadata', (' poster="%s"' % img) if img else '', vid)
    else:
        med = '<img src="%s" alt="%s" loading="lazy">' % (img, who)
    return '<figure class="lk%s"><a href="%s" target="_blank" rel="noopener">%s</a><figcaption><b>%s</b><a href="%s" target="_blank" rel="noopener">%s ↗</a></figcaption></figure>' % ('' if img else ' nv', u, med, cap, u, who)
vgal = '<div class="grid4 gal sq">' + ''.join(_vf(*v) for v in VG) + '</div>'
i = b3.index('<div class="gp" role="tabpanel" id="gp-4"')
j = b3.index('</p></div>', i) + len('</p></div>')
b3 = b3[:j] + vgal + b3[j:]
# Хаски: карточка с видео без постера — оставляем. Перенумеровать карточки и счётчики вкладок
_n = [0]
def _cn(m):
    _n[0] += 1; return '<span class="cn">%02d</span>' % _n[0]
b3 = re.sub(r'<span class="cn">\d+</span>', _cn, b3)
cats = re.findall(r'<a class="cs[^"]*" data-c="(\w+)"', b3)
def _sup(m):
    f = m.group(1); n = len(cats) if f == 'all' else cats.count(f)
    return m.group(0)[:m.group(0).index('<sup>')] + '<sup>%d</sup>' % n
b3 = re.sub(r'<button type="button" class="ct" data-f="(\w+)"[^>]*>[^<]*<sup>\d+</sup>', _sup, b3)
b3 = re.sub(r'(<span class="slc"><b>01</b> / )\d+', lambda m: m.group(1) + '%02d' % len(cats), b3)
PJ = [  # название, часы от-до, цена от-до (тыс ₽), подпись: dx, dy, якорь
 ('Мокапы', 2, 6, 1, 5, 10, 4, 'start'),
 ('Фотосессия', 10, 20, 5, 25, -12, 4, 'end'),
 ('Key visual', 8, 24, 5, 30, 10, -6, 'start'),
 ('Иллюстрации', 15, 30, 5, 30, 10, 14, 'start'),
 ('Тематический ролик', 10, 30, 5, 50, 10, -6, 'start'),
 ('Рекламный ролик', 20, 40, 30, 100, -12, -8, 'end'),
 ('AI-продукт', 30, 60, 30, 100, 0, 26, 'middle'),
]
W, H, L, B, R, T = 720, 420, 56, 44, 20, 16
def X(h): return L + (W - L - R) * h / 64
def Y(p): return H - B - (H - B - T) * p / 105
g = ['<svg viewBox="0 0 %d %d" role="img" aria-label="График: по горизонтали часы работы, по вертикали цена проекта. Точки выше линии 2000 рублей в час — проекты, где час стоит дороже всего: рекламный ролик">' % (W, H)]
for h in range(0, 61, 10):
    g.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" class="gl"/><text x="%.1f" y="%d" class="ax" text-anchor="middle">%d</text>' % (X(h), T, X(h), H - B, X(h), H - B + 20, h))
for p in range(0, 101, 25):
    g.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" class="gl"/><text x="%d" y="%.1f" class="ax" text-anchor="end">%s</text>' % (L, Y(p), W - R, Y(p), L - 8, Y(p) + 4, (str(p) + 'к') if p else '0'))
for rate, hmax in [(1000, 64), (2000, 52.5)]:
    g.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="rl%s"/><text x="%.1f" y="%.1f" class="rt%s" text-anchor="end">%s ₽/ч</text>' % (X(0), Y(0), X(hmax), Y(rate * hmax / 1000), ' a' if rate == 2000 else '', X(hmax) - 4, Y(rate * hmax / 1000) + (16 if rate == 1000 else -8), ' a' if rate == 2000 else '', format(rate, ',').replace(',', ' ')))
g.append('<text x="%d" y="%d" class="ax t" text-anchor="end">часы работы →</text><text x="%d" y="%d" class="ax t">↑ цена, ₽</text>' % (W - R, H - 6, L - 48, T - 4))
for i, (n, h1, h2, p1, p2, dx, dy, an) in enumerate(PJ):
    hm, pm_ = (h1 + h2) / 2, (p1 + p2) / 2
    rate = pm_ * 1000 / hm
    hot = rate >= 1800
    g.append('<g class="pj%s" style="--i:%d"><circle cx="%.1f" cy="%.1f" r="7"/><text x="%.1f" y="%.1f" text-anchor="%s">%s<tspan> ≈ %s ₽/ч</tspan></text></g>' % (
        ' hot' if hot else '', i, X(hm), Y(pm_), X(hm) + dx, Y(pm_) + dy, an, n, format(int(round(rate, -2)), ',').replace(',', ' ')))
g.append('</svg>')
chart = '<figure class="hp"><div class="hsc">%s</div><figcaption><span class="micro">Часы × цена</span><span>Точка — середина вилки по часам и цене. Чем выше точка над линиями, тем дороже час. <b>Красным</b> — где час стоит дороже всего: в рекламе платят за идею и ответственность, а не за генерацию.</span></figcaption></figure>' % ''.join(g)
t3 = sec_txt('pg-3')
t3 = re.sub(r'Вилки взяты с сайта.*?ценами\.', 'Вилки — ориентир на 2026 год: внизу один кадр, один круг правок и один формат, вверху набор кадров, адаптации и передача прав.', t3, flags=re.S)
out.append(section(4, '04', 'Заказы и цены', 'Какие проекты заказывают <span class="s">и сколько они стоят</span>', t3, b3 + '\n<p class="micro" style="margin:56px 0 14px">Сколько стоит час в разных проектах</p>\n' + chart))

# --- I.05 Что изменили нейросети (бывшая 02)
b2 = sec_body('pg-2')
b2 = re.sub(r'<p class="fn">.*?</p>', '<p class="fn">Разница посчитана по серединам вилок, рабочий день — 8 часов.</p>', b2, flags=re.S)
out.append(section(5, '05', 'Было и стало', 'Что изменили <span class="s">нейросети</span>',
  '<p>Одни и те же задачи — раньше с командой и съёмкой, теперь с нейросетями. Синяя полоса — сколько уходило раньше, красная — сколько сейчас.</p>'.replace('Синяя', 'Серая'), b2))

# --- I.06 Клиенты
out.append(section(6, '06', 'Клиенты', 'Чего хотят клиенты <span class="s">и где работать</span>', sec_txt('pg-5'), nofn(sec_body('pg-5'))))

# ================= ЧАСТЬ II. ПОШАГОВО
out.append(part('p2', 'II', 'Пошагово', 'Семь шагов от цели до первого оплаченного заказа.'))
def step(id_src, n, title, txt=None, body=None):
    return section(id_src.replace('pg-', 'st'), '%02d' % n, 'Шаг %d' % n, title, txt if txt is not None else sec_txt(id_src), body if body is not None else nofn(sec_body(id_src)))
out.append(step('pg-6', 1, 'Определи цель и <span class="s">откуда заходишь</span>'))
LEARN = [
 ('Насмотренность', 'Собирай референсы, разбирай рекламу, клипы и кино: что в кадре работает и почему. Это то, что нейросеть за тебя не сделает.'),
 ('Основы дизайна', 'Композиция, цвет, свет, типографика. Без них генерация остаётся «просто картинкой».'),
 ('Процесс', 'Бриф → идея → эскиз → производство → отбор → сдача. Научись проходить его целиком, а не только этап генерации.'),
 ('Инструменты', 'Одна текстовая нейросеть, одна-две визуальные и Figma для сборки. Больше на старте не нужно.'),
 ('Обратная связь', 'Показывай работы тем, кто сильнее тебя. Так растёшь быстрее всего — и быстрее всего замечаешь собственные ошибки.'),
]
learn = '<ol class="check">' + ''.join('<li><b>%s.</b> %s</li>' % x for x in LEARN) + '</ol>'
GUIDES_SHORT = '<div class="lrn"><a href="https://perasperadastra.ru/mission-to-ai" target="_blank" rel="noopener"><span class="micro">Курс</span><b>Mission to AI ↗</b><span>Генерация графики и видео с обратной связью от кураторов</span></a><a href="#pg-end"><span class="micro">Бесплатно</span><b>Гайды школы ↓</b><span>AI-клип, AI-фильм с реальными героями, лендинг с нейросетями</span></a></div>'
out.append(section('learn', '02', 'Шаг 2', 'Прокачай <span class="s">базу</span>',
  '<p>Нейросеть усиливает то, что уже есть внутри: есть вкус и идея — будет сильный результат, нет — будет среднее. Поэтому сначала база, потом сервисы.</p>',
  learn + '\n<p class="micro" style="margin:36px 0 12px">Где учиться</p>\n' + GUIDES_SHORT))
out.append(step('pg-7', 3, 'Опиши <span class="s">свои услуги</span>'))
out.append(step('pg-8', 4, 'Собери минимальный <span class="s">стек</span>'))
out.append(step('pg-9', 5, 'Сделай первый <span class="s">проект</span>'))
out.append(section('st10', '06', 'Шаг 6', 'Оформи кейс <span class="s">и покажи работы</span>', sec_txt('pg-10'),
  nofn(sec_body('pg-10')) + '\n<p class="micro" style="margin:48px 0 12px">Где показывать</p>\n' + nofn(sec_body('pg-11'))))
out.append(step('pg-12', 7, 'Возьми первый <span class="s">заказ</span>'))

# ================= ЧАСТЬ III. НЕЙРОСЕТИ
out.append(part('p3', 'III', 'Нейросети', 'Нейросети бывают текстовые и визуальные. Одни думают и пишут, другие рисуют и оживляют — и лучше всего работают в паре.'))
two = '''<div class="two-m">
<div class="tm"><span class="micro">Голова</span><h3>Текстовые</h3><p>Думают и пишут. Помогают придумать идею, разобрать бриф, организовать работу и написать промпт для визуальной нейросети.</p><ul><li>Идеи и концепции</li><li>Бриф, сценарий, раскадровка</li><li>Промпты для других нейросетей</li><li>Тексты для кейса, письма клиенту, вёрстка сайта</li></ul><small>Claude, ChatGPT, Gemini, Grok, DeepSeek, Perplexity</small></div>
<div class="tm v"><span class="micro">Руки</span><h3>Визуальные</h3><p>Рисуют и оживляют. Делают то, что им описали: картинку, видео, звук. Сами задачу не придумывают.</p><ul><li>Картинки и key visual</li><li>Правка по фото и мокапы</li><li>Видео из кадра</li><li>Музыка и голос</li></ul><small>Midjourney, Nano Banana, Seedance, Kling, Veo, Suno</small></div>
</div>
<div class="flow" aria-label="Как они работают вместе"><span>Бриф</span><i>→</i><span class="t">Текстовая нейросеть</span><i>→</i><span>Промпт</span><i>→</i><span class="v">Визуальная нейросеть</span><i>→</i><span>Кадр</span><i>→</i><span class="y">Ты: отбор и доводка</span></div>'''
out.append(section('m1', '01', 'Два типа', 'Текстовые и визуальные: <span class="s">в чём разница</span>',
  '<p>Новички часто ждут от ChatGPT готовый key visual, а от Midjourney — идею кампании. Это разные инструменты: текстовая нейросеть — голова, визуальная — руки.</p>',
  two + '\n<p class="tip"><b>Главная связка.</b> Текстовая нейросеть пишет точный промпт по брифу и стилю, визуальная его исполняет, а ты выбираешь лучшее и доводишь руками.</p>'))

TM = [
 ('Claude', 'от Anthropic', 'Длинные тексты и брифы, логика концепции, структура презентации, код и вёрстка лендинга, разбор документов и скриншотов макета', 'Генерации картинок — Claude не рисует', 'Бесплатно<small>Pro $20 ≈ 1 900–2 400 ₽</small>', 'no'),
 ('ChatGPT', 'от OpenAI', 'Универсал: тексты, промпты, картинки и правки прямо в чате, голосовой режим', 'Финальной эстетики бренда', 'Бесплатно<small>Go $8 ≈ 800 ₽, Plus $20 ≈ 1 900–2 400 ₽</small>', 'no'),
 ('Gemini', 'от Google', 'Разбор видео и ссылок на YouTube, большие файлы, связка с Google Docs; внутри — Nano Banana для картинок', 'Текстов с характером и авторской интонацией', 'Бесплатно<small>AI Pro $20 ≈ 1 900–2 400 ₽</small>', 'no'),
 ('Grok', 'от xAI', 'Свежие тренды и обсуждения из X, смелые формулировки; внутри — Grok Imagine для картинок и видео', 'Точных фактов без проверки', 'Бесплатно<small>SuperGrok Lite $10, SuperGrok $30</small>', 'no'),
 ('DeepSeek', 'китайская модель', 'Черновики текстов и идей, работает из России без VPN и бесплатно', 'Работы с картинками и данных клиента', 'Бесплатно', 'ok'),
 ('Perplexity', 'поиск с ИИ', 'Поиск с источниками: рынок, конкуренты, референсы, цены', 'Креатива и длинных текстов', 'Бесплатно<small>Pro $20 ≈ 1 900–2 400 ₽</small>', 'no'),
]
pay = {'no': '<span class="warn">через посредника</span>', 'ok': '<span class="ok">не нужна</span>'}
tm = ''.join('<tr><td><b>%s</b><small>%s</small></td><td>%s</td><td class="n">%s</td><td>%s</td><td>%s</td></tr>' % (a, b, c, d, e, pay[f]) for a, b, c, d, e, f in TM)
TASK = [('Придумать концепцию и разобрать бриф', 'Claude или ChatGPT'), ('Написать промпт для картинки или видео', 'ChatGPT или Claude'), ('Изучить рынок, конкурентов, цены', 'Perplexity'), ('Разобрать видео-референс', 'Gemini'), ('Найти, что сейчас в тренде', 'Grok')]
task = '<div class="tk">' + ''.join('<div><span>%s</span><b>%s</b></div>' % t for t in TASK) + '</div>'
out.append(section('m2', '02', 'Текстовые', 'Текстовые <span class="s">нейросети</span>',
  '<p>У всех есть бесплатный режим — для старта его хватает. Платная подписка даёт лимиты побольше и модели поумнее. Цены официальные, в рублях — по курсу около 83 ₽ за доллар с комиссией посредника.</p>',
  '<div class="tw"><table style="min-width:860px"><thead><tr><th>Нейросеть</th><th>В чём сильна для дизайнера</th><th>Не бери для</th><th>Сколько стоит</th><th>Карта РФ</th></tr></thead><tbody>' + tm + '</tbody></table></div>\n<p class="micro" style="margin:40px 0 12px">Какую брать под задачу</p>\n' + task +
  '\n<p class="tip"><b>Если нужно без VPN и иностранной карты</b> — Алиса AI от Яндекса и GigaChat от Сбера. Для черновиков подойдут, для дизайнерских задач заметно слабее. GigaChat бесплатный, Алиса — в подписке Яндекс Плюс.</p>'))

# визуальные: строки из старой таблицы + новые, по вкладкам
b14 = sec_body('pg-14')
rows = dict((re.sub('<[^>]+>', '', m.group(1)).strip(), m.group(0)) for m in re.finditer(r'<tr><td><b>(.*?)</b>.*?</tr>', b14, re.S))
def row(name, html=None): return html or rows[name]
def mk(n, sub, task, strong, no, price, payk):
    return '<tr><td><b>%s</b>%s</td><td class="n">%s</td><td>%s</td><td class="n">%s</td><td>%s</td><td>%s</td></tr>' % (n, ('<small>%s</small>' % sub) if sub else '', task, strong, no, price, payk)
P = {'no': '<span class="no">нет</span>', 'agg': '<span class="warn">через агрегатор</span>', 'mid': '<span class="warn">через посредника</span>', 'free': '<span class="ok">не нужна</span>'}
IMG = [row('Midjourney'), row('Nano Banana'), row('Картинки в ChatGPT'),
       mk('Seedream', 'от ByteDance', 'Реализм', 'Фотореалистичные кадры, точные детали и текст', 'Поиска необычного стиля', 'В агрегаторе<small>Syntx, Higgsfield</small>', P['agg'])]
VID = [row('Seedance'), row('Kling'),
       mk('Veo', 'от Google', 'Оживить: кино', 'Кинематографичное видео сразу со звуком и речью', 'Длинных серий кадров', 'В Google AI Pro<small>$20 ≈ 1 900–2 400 ₽ или в агрегаторе</small>', P['mid'])]
SND = [row('Suno'),
       mk('ElevenLabs', '', 'Голос', 'Озвучка, дикторский голос, перевод речи', 'Музыки', 'Бесплатно<small>Starter $5 ≈ 500 ₽</small>', P['mid'])]
ASM = [row('CapCut, Figma')]
th_ = '<thead><tr><th>Нейросеть</th><th>Задача</th><th>Сильная сторона</th><th>Не бери для</th><th>Сколько стоит</th><th>Карта РФ</th></tr></thead>'
tabs = [('vi', 'Картинки', IMG), ('vv', 'Видео', VID), ('vs', 'Звук', SND), ('va', 'Сборка', ASM)]
tb = '<div class="tabs" role="tablist" aria-label="Тип визуальной нейросети" style="margin:0 0 18px">' + ''.join('<button role="tab" aria-selected="%s" aria-controls="%s-p" id="%s-t">%s</button>' % ('true' if i == 0 else 'false', k, k, n) for i, (k, n, _) in enumerate(tabs)) + '</div>'
tp = ''.join('<div class="gp%s" role="tabpanel" id="%s-p" aria-labelledby="%s-t"><div class="tw"><table style="min-width:900px">%s<tbody>%s</tbody></table></div></div>' % (' on' if i == 0 else '', k, k, th_, '\n'.join(r)) for i, (k, n, r) in enumerate(tabs))
pipe = b14[b14.index('<p class="micro" style="margin:36px 0 12px">Как связать в конвейер</p>'):]
out.append(section('m3', '03', 'Визуальные', 'Визуальные <span class="s">нейросети</span>',
  '<p>Здесь важна роль: одна нейросеть придумывает стиль, другая держит продукт и лицо, третья оживляет кадр. Спорить, какая лучшая, — всё равно что спорить, что лучше: кисть или молоток.</p>',
  tb + tp + '\n' + pipe))

# ================= ЧАСТЬ IV. ПОДПИСКИ
out.append('''<div class="part" id="pg-p4"><h2>Часть IV. <span class="s">Подписки</span></h2><p>Бесплатных режимов хватает, чтобы попробовать. Для работы на заказ — нет: водяные знаки, низкое разрешение, лимиты и часто нет прав на коммерческое использование. Клиент видит только результат, поэтому подписка — такой же рабочий инструмент, как Figma. Хорошая новость: для старта хватает одного агрегатора и одной текстовой нейросети.</p><a class="pbtn" href="#pg-s7">К калькулятору ↓</a></div>

''')
for i, (sid, n) in enumerate([('pg-s1', 1), ('pg-s2', 2), ('pg-s7', 3)]):
    a = s.index('<section class="step" id="%s">' % sid); b = s.index('</section>', a) + len('</section>')
    t = s[a:b]
    t = re.sub(r'<div class="num">П\d', '<div class="num">%02d' % n, t)
    out.append(t + '\n\n')

# ================= ИТОГ
CON = [('Рынок новый', 'Правила ещё пишутся, а большинство специалистов только разбираются, как работать с нейросетями. Порог входа низкий, инструменты доступны.'),
       ('Среднее ничего не стоит', 'Специалистов много, хороших мало. Выигрывают вкус, идея и умение вести проект от брифа до сдачи.'),
       ('Сейчас — лучшее время зайти', 'С одной стороны, конкуренция растёт. С другой — сильных людей мало, и рынок их активно ищет. Это отличная возможность.')]
con = '<ol class="con">' + ''.join('<li><b>%s</b><p>%s</p></li>' % c for c in CON) + '</ol>'
GD = [('https://perasperadastra.ru/klip', None, 'https://static.tildacdn.com/vide3137-3335-4439-b138-373930326161/klip-hero-final.mp4', 'Гайд', 'AI-клип', 'Клип с персонажем без съёмки: от идеи до монтажа'),
      ('https://perasperadastranew.github.io/guides/rolik-po-foto/', 'img/g-rolik.webp', None, 'Гайд', 'AI-фильм с реальными героями', 'Фильм по семейным фото: реальные люди и локации'),
      ('https://perasperadastranew.github.io/guides/mtw/lending/', 'img/g-lending.webp', None, 'Гайд', 'Лендинг с нейросетями', 'Сайт от идеи до публикации с помощью нейросетей')]
def gcard(u, img, vid, k, t, d):
    med = ('<img src="%s" alt="" loading="lazy">' % img) if img else ('<span class="ty" aria-hidden="true">%s</span><video muted loop playsinline preload="metadata" data-src="%s"></video>' % (t[0], vid))
    return '<a class="gd%s" href="%s" target="_blank" rel="noopener"><div class="cm">%s</div><div class="cb"><span class="micro">%s</span><b>%s <i aria-hidden="true">↗</i></b><span>%s</span></div></a>' % ('' if img else ' t', u, med, k, t, d)
gd = '<div class="gds">' + ''.join(gcard(*g) for g in GD) + '</div>'
out.append('''<section class="step fin" id="pg-end">%s
%s
<div class="live"><span class="micro">Прямой эфир</span><h3>Разберём всё это вживую</h3><p>На прямом эфире покажем, как мы работаем с нейросетями: идеи и решения на нас, рутина на ИИ. Ответим на вопросы и разберём, что дизайнеру нужно уметь в 2027 году. Анонс — в нашем Telegram-канале.</p><a class="btn" href="https://t.me/perasperagram" target="_blank" rel="noopener">Telegram-канал ↗</a></div>
<p class="micro" style="margin:56px 0 14px">Ещё гайды в нашем канале</p>
%s
</section>

''' % (head('→', 'Итог', 'Три <span class="s">вывода</span>', '<p>Коротко о том, что важно унести из гайда.</p>'), con, gd))

body = ''.join(out)
a = s.index('<header>'); b = s.index('<footer')
res = s[:a] + body + s[b:]
res = res.replace('<title>Как начать в AI-индустрии, короткая версия</title>', '<title>Как начать в AI-индустрии</title>')

css = open(os.path.join(D, 'add.css'), encoding='utf-8').read()
js = open(os.path.join(D, 'add.js'), encoding='utf-8').read()
i = res.index('</style>'); res = res[:i] + css + res[i:]
i = res.rindex('</body>'); res = res[:i] + '<script>' + js + '</script>\n' + res[i:]
open(OUT, 'w', encoding='utf-8').write(res)
print('ok', len(res))
