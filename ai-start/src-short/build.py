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
hdr = re.sub(r'<p class="lead">.*?</p>', '<p class="lead">Гайд для старта в нейросетях: что на самом деле происходит на рынке, какие проекты заказывают и сколько они стоят, как пройти путь до первого заказа, чем текстовые нейросети отличаются от визуальных и за какие подписки платить.</p>', hdr, flags=re.S)
hdr = re.sub(r'<nav class="need".*?</nav>', '''<nav class="need" aria-label="Разделы">
<a href="#pg-p1"><b><i>I</i>Рынок</b><span>Что происходит, мифы, заказы и цены</span></a>
<a href="#pg-p2"><b><i>II</i>Пошаговый план</b><span>От цели до первого заказа</span></a>
<a href="#pg-p3"><b><i>III</i>Нейросети</b><span>Самые актуальные текстовые и визуальные модели</span></a>
<a href="#pg-p4"><b><i>IV</i>Подписки</b><span>За что платить и сколько</span></a>
<a href="#pg-end"><b><i>→</i>Итог</b><span>Пять выводов, эфир и гайды</span></a>
</nav>''', hdr, flags=re.S)
out.append(hdr)
out.append('<a class="lvb" href="https://t.me/perasperagram" target="_blank" rel="noopener"><span class="dot" aria-hidden="true"></span><span class="micro">Прямой эфир</span><b>Среда, 28 октября, 19:00</b><span class="tx">Разберём рынок, навыки и нейросети вживую</span><i aria-hidden="true">→</i></a>\n')

# ================= ЧАСТЬ I. РЫНОК
out.append(part('p1', 'I', 'Рынок', 'Что происходит на самом деле, какие мифы мешают, какие проекты заказывают и что изменили нейросети.'))

# --- I.01 Что происходит: тезисы
TH = [
 ('Нейросети пришли в каждую профессию', '5 дней', 'Столько понадобилось ChatGPT, чтобы набрать первый миллион пользователей. Сейчас у него около 900 млн человек в неделю. А длина задач, которые ИИ выполняет сам, удваивается примерно каждые 4 месяца.'),
 ('Сокращения — часто отговорка', '9%', 'Только 9% компаний говорят, что ИИ действительно заменил какие-то роли. При этом к маю 2026 года 102 000 человек потеряли работу в технологических компаниях, и почти 6 из 10 компаний называют причиной ИИ, хотя причина финансовая. Сэм Альтман называет это AI washing. А Klarna, которая хвасталась, что бот заменил 700 операторов, снова нанимает людей: качество упало.'),
 ('Проекты стали сложнее', 'всё сразу', 'Раньше заказывали одну картинку или один формат. Теперь в одном проекте фото, графика, 3D, моушн и видео: клиент ждёт серию, адаптации под площадки и ролик — и всё это в одном стиле.'),
 ('Ценятся Т‑специалисты', 'Т', 'Глубоко в одном — дизайне, моушне, монтаже — и широко в смежном. Нейросети дают доступ к 3D, видео и звуку без отдельной команды, но собрать это в сильный проект может только тот, у кого есть база.'),
 ('Рынок ищет тех, кто умеет', '16%', '16% вакансий дизайнеров и художников на hh.ru в 2026 году требуют навыков работы с нейросетями — больше, чем в любой другой профессии.'),
]
# график «крутости»: длина задачи, которую модель выполняет сама (METR, 50% успеха), лог-шкала
import math
MOD = [(2019.13, 2/60, 'GPT-2'), (2020.45, 8/60, 'GPT-3'), (2022.2, 0.6, 'GPT-3.5'), (2023.2, 5, 'GPT-4'), (2024.8, 28, 'Claude 3.5'), (2025.15, 59, 'Claude 3.7'), (2025.6, 137, 'GPT-5'), (2026.1, 720, 'Opus 4.6')]
EV = [(2020, 'GPT-3', 'текст по запросу'), (2021, 'DALL·E', 'картинки по описанию'), (2022, 'Midjourney, ChatGPT', 'нейросети для всех'), (2023, 'GPT-4, Firefly', 'ИИ в рабочих программах'),
      (2024, 'Sora, Kling', 'видео по описанию'), (2025, 'Nano Banana, Veo 3', 'правка по фото, видео со звуком'), (2026, 'Агенты', 'ИИ сам ведёт задачу часами')]
W, H, L, R, T, B = 760, 330, 92, 24, 24, 34
x0, x1 = 2019.8, 2026.4
def X(y): return L + (W - L - R) * (y - x0) / (x1 - x0)
lo, hi = math.log10(0.1), math.log10(1440)
def Y(m): return T + (H - T - B) * (1 - (math.log10(m) - lo) / (hi - lo))
g = ['<svg viewBox="0 0 %d %d" role="img" aria-label="График: длина задачи, которую нейросеть выполняет сама, выросла с нескольких секунд в 2020 году до примерно 12 часов в 2026">' % (W, H)]
for m, lab in [(0.1, '6 сек'), (1, '1 мин'), (10, '10 мин'), (60, '1 час'), (600, '10 часов')]:
    g.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" class="gl"/><text x="%d" y="%.1f" class="ax" text-anchor="end">%s</text>' % (L, Y(m), W - R, Y(m), L - 8, Y(m) + 4, lab))
for y in range(2020, 2027):
    g.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" class="gl v"/><text x="%.1f" y="%d" class="ax yr" text-anchor="middle">%d</text>' % (X(y), T, X(y), H - B, X(y), H - 10, y))
pts = [(X(a), Y(max(b, 0.1))) for a, b, _ in MOD if a >= x0]
d = 'M' + ' L'.join('%.1f %.1f' % pt for pt in pts)
g.append('<path d="%s" class="cv" pathLength="1"/>' % d)
for k, (a, b, n) in enumerate([m for m in MOD if m[0] >= x0]):
    last = k == len(pts) - 1
    lx, ly = X(a), Y(b)
    g.append('<g class="mp%s" style="--k:%d"><circle cx="%.1f" cy="%.1f" r="%d"/><text x="%.1f" y="%.1f" text-anchor="%s">%s</text></g>' % (' a' if last else '', k, lx, ly, 6 if last else 4.5, lx + (-10 if last else 8), ly + (-12 if last else 16), 'end' if last else 'start', n + (' ≈ 12 часов' if last else '')))
g.append('</svg>')
ev = ''.join('<li style="--k:%d"><b>%d</b><em>%s</em><span>%s</span></li>' % (k, y, a_, d_) for k, (y, a_, d_) in enumerate(EV))
growth = '<figure class="gw"><span class="micro">Насколько нейросети стали сильнее</span><div class="hsc">%s</div><figcaption>Длина задачи, которую нейросеть выполняет сама без человека: от нескольких секунд у GPT-3 до примерно 12 часов работы эксперта у Opus 4.6. Шкала логарифмическая — каждое деление в 10 раз больше. Удвоение примерно каждые 4 месяца. По данным METR.</figcaption><ol class="ev">%s</ol></figure>' % (''.join(g), ev)
th = ''.join('<li><div class="tl"><span class="micro">%02d</span><h3>%s</h3><b>%s</b></div><p>%s</p></li>' % (i + 1, t, b, d) for i, (t, b, d) in enumerate(TH))

towers = """<figure class="tw3" id="pg-tw"><div class="abh"><span class="micro">Насколько сложнее стал проект</span><button type="button" class="ab-re">↻ Ещё раз</button></div>
<div class="twv"><div class="twp"><canvas width="170" height="270" data-x="78" role="img" aria-label="Маленькая башенка из трёх блоков — проект раньше"></canvas><div class="twc"><b>Раньше</b><span>Одна картинка, один формат</span></div></div><div class="twp r"><canvas width="170" height="270" data-x="214" role="img" aria-label="Большая башня в семь ярусов — проект сейчас"></canvas><div class="twc"><b>Сейчас</b><span>Фото, графика, 3D, моушн, видео и адаптации — в одном проекте</span></div></div><i class="twd" data-src="d/towers.png" data-n="62" hidden></i></div></figure>"""

tshape = """<figure class="tsp" id="pg-tsp"><span class="micro">Кто сейчас ценится</span><p class="tlead">Дизайнер с глубокой экспертизой в одной сфере и широким кругозором в смежных</p>
<div class="tsg"><div class="tc deep"><div class="tl2"><span class="micro">Вертикаль</span><b>Глубокая экспертиза</b></div><div class="tfx"><i class="tax v" aria-hidden="true"></i><i class="m" style="--w:223;--h:440;-webkit-mask-image:url(img/t-deep.png);mask-image:url(img/t-deep.png)"></i></div><p>Одна сфера, в которой ты сильнее большинства: дизайн, моушн, монтаж или иллюстрация. За это тебя и выбирают.</p></div>
<div class="tc wide"><div class="tl2"><span class="micro">Горизонталь</span><b>Широкий кругозор</b></div><div class="tfx"><i class="tax h" aria-hidden="true"></i><i class="m" style="--w:424;--h:440;-webkit-mask-image:url(img/t-wide.png);mask-image:url(img/t-wide.png)"></i></div><p>Понимание смежных областей: 3D, видео, звук, текст. Нейросети дают эту ширину без отдельной команды.</p></div></div>
<p class="tsum"><b>Вместе это и есть Т-специалист.</b> Одной ширины мало: без глубины получается средний результат.</p></figure>"""

birds = """<figure class="ab" id="pg-birds"><div class="abh"><span class="micro">Почему одних нейросетей мало</span><button type="button" class="ab-re">↻ Ещё раз</button></div><q class="abq">Успех не в силе натяжения, а в том, куда приложить усилие</q>
<div class="abg"><div class="ab-a"><span class="micro">Только нейросети</span><div class="abv"><canvas width="480" height="270" data-src="d/birds-a.png" role="img" aria-label="Одна и та же птица трижды отскакивает от крепости — проект стоит"></canvas><span class="cap"></span></div><p>Новичок умеет только генерировать — и бьёт этим раз за разом. Тот же удар, тот же результат.</p></div>
<div class="ab-b"><span class="micro">Набор навыков</span><div class="abv"><canvas width="480" height="270" data-src="d/birds-b.png" role="img" aria-label="Четыре птицы-навыка по очереди: насмотренность, база дизайна, работа с заказчиком и нейросети — крепость падает"></canvas><span class="cap"></span></div><p>У профи каждый навык бьёт по-своему, а нейросети — один из них. Вместе они берут любой проект.</p></div></div>
<ol class="abl"><li><i class="k s"></i><b>Насмотренность</b><span>Видит, куда бить: референсы, идея, понимание, что сработает</span></li><li><i class="k r"></i><b>База дизайна</b><span>Композиция, цвет, типографика, визуальный ритм — бьёт сразу по нескольким фронтам</span></li><li><i class="k d"></i><b>Работа с заказчиком</b><span>Понимает задачу, договаривается и попадает точно в то, что нужно бизнесу</span></li><li><i class="k h"></i><b>Нейросети</b><span>Производство: быстро делают картинки и видео и добивают проект</span></li></ol></figure>"""
out.append(section(1, '01', 'Что происходит', 'Что происходит <span class="s">на рынке</span>',
  '<p>Пять тезисов о том, что сейчас на самом деле происходит с профессией: как быстро пришли нейросети, что с увольнениями, какими стали проекты и кто нужен рынку.</p>',
  growth + '\n<ol class="th">' + th + '</ol>\n' + towers + '\n' + tshape + '\n' + birds + '\n<p class="tip"><b>Вывод.</b> «Всех сокращают из-за ИИ» — часто отговорка. Нейросети не отменяют дизайнеров, они отменяют средний результат. Людей, которые умеют с ними работать, ищут активнее остальных.</p>'))

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

# --- I.04 Проекты и цены — по типу работы
CASE = {
 'knives': ('https://dprofile.ru/case/178358/simple-knives-kollekciia-nozei', 'Simple Knives · Анастасия Грачева'),
 'mako': ('https://www.behance.net/gallery/255746473/MAKO-AI-Mascot', 'МАКО · Диана Херман'),
 'lappi': ('https://dprofile.ru/case/194719/maskot-lappi', 'Лаппи · Лиза Жильцова'),
 'hronos': ('https://dprofile.ru/case/197705/hronos-servis-kruglosutocnoi-dostavki-edy', 'Хронос · Анастасия Семёнова'),
 'eaglips': ('https://dprofile.ru/case/173955/eaglips', 'Eaglips · Милана Гавриченко'),
 'lumera': ('https://dprofile.ru/case/174067/lumera', 'Lumera · Лейла Исхакова'),
 'mofu': ('https://dprofile.ru/case/179802/mofu-mofu-pusistye-obvesy', 'mofu-mofu · Арина Галимова'),
 'husky': ('https://dprofile.ru/case/197117/tancy-na-snegu-koncept-klipa-bez-kamery-i-akterov', 'Хаски «Танцы на снегу»'),
 'godov': ('https://perasperadastranew.github.io/guides/rolik-po-foto/', 'Годовщина родителей'),
}
def fig(src, cap, key=None, vid=None):
    if key:
        u, who = CASE[key]
        if vid:
            med = '<video muted loop playsinline preload="%s"%s data-src="%s"></video>' % ('none' if src else 'metadata', (' poster="%s"' % src) if src else '', vid)
        else:
            med = '<img src="%s" alt="%s" loading="lazy">' % (src, who)
        return '<figure class="lk%s"><a href="%s" target="_blank" rel="noopener">%s</a><figcaption><b>%s</b><a href="%s" target="_blank" rel="noopener">%s ↗</a></figcaption></figure>' % ('' if src else ' nv', u, med, cap, u, who)
    return '<figure><img src="%s" alt="%s" loading="lazy"><figcaption><b>%s</b></figcaption></figure>' % (src, cap, cap)
DP2 = 'https://dprofile.ru/case/'
# (картинка или 'video:файл|постер' или None, ссылка, подпись под картинкой, проект, задача, что сдаёшь, цена)
CATS = [
 ('foto', 'Фотореализм', 'Маркетплейсы, e-com, бренды одежды и косметики. Нужно много реалистичных кадров — быстрее и дешевле съёмки.', [
   ('cases/knives-2.webp', DP2 + '178358/simple-knives-kollekciia-nozei', 'Simple Knives · Анастасия Грачева', 'Предметная фотосессия', 'Продукт в нескольких сетах без студии', 'Карточка продукта, 3 hero и 3 lifestyle', '5–25 тыс ₽'),
   ('cases/dp-goingallin.webp', DP2 + '176218/were-going-all-in-detskii-saxmatnyi-lager', 'We’re Going All In · Лейла Исхакова', 'Фотосессия с AI-моделью', 'Модели бренда в разных образах и с продуктом', 'Карточки моделей и серия кадров', '5–20 тыс ₽'),
   ('cases/dp-exclusaro.webp', DP2 + '179557/exclusaro-borba-so-stixiei', 'Exclusaro · Ева-София Шульце', 'Рекламная фотосессия', 'Продукт в сюжетной сцене для кампании', 'Серия рекламных кадров', '10–30 тыс ₽'),
   ('cases/dp-boreal.webp', DP2 + '174167/boreal', 'Boréal · Мария Тетерина', 'Фотостиль бренда', 'Единый стиль кадров для сайта и соцсетей', 'Серия кадров и правила стиля', '5–25 тыс ₽'),
   ('cases/dp-form.webp', DP2 + '172259/form-101', 'FORM — 1.01 · Яна Саввина', 'Концепт продукта', 'Показать продукт, которого ещё нет: форма, материалы, ракурсы', 'Серия реалистичных ракурсов и деталей', '10–40 тыс ₽')]),
 ('graf', '2D и 3D-графика', 'Бренды, агентства и продуктовые команды: кампании, запуски, айдентика, цифровые продукты. Нужен узнаваемый стиль на всех материалах, а не одна картинка.', [
   ('cases/dp-margarita.webp', DP2 + '180564/master-i-margarita-koncept-kineticeskoi-novelly', 'Мастер и Маргарита · Елизавета Демидова', 'Иллюстрации', 'Графический язык и серия иллюстраций в одном стиле', 'Серия из 5–15 кадров', '5–30 тыс ₽'),
   ('cases/dp-lappi.webp', DP2 + '194719/maskot-lappi', 'Лаппи · Лиза Жильцова', 'Маскот', 'Персонаж бренда в разных позах и ситуациях', 'Карточка персонажа и серия сцен', '15–50 тыс ₽'),
   ('cases/dp-hronos.webp', DP2 + '197705/hronos-servis-kruglosutocnoi-dostavki-edy', 'Хронос · Анастасия Семёнова', 'Упаковка', 'Концепт упаковки и её подача', 'Концепт, мокапы, носители', '15–40 тыс ₽'),
   ('cases/dp-kvas.webp', DP2 + '179478/kvas-drinks-collection', 'Drinks Collection · Вероника Саттарова', 'Айдентика и упаковка серии', 'Графика бренда и линейка продуктов с общей историей', 'Набор графики, упаковка и примеры применения', '20–60 тыс ₽'),
   ('cases/dp-yapay.webp', DP2 + '190803/key-visual-dlia-iandeks-pei', 'Яндекс Пэй · Мария Даль', 'Графика для цифрового продукта', 'Key visual, 3D-ассеты и иллюстрации для приложения и промо', 'Система графики в стиле продукта', '30–100 тыс ₽')]),
 ('vid', 'Видео', 'Бренды, медиа и артисты: ролики для рекламы, соцсетей и музыкантов.', [
   ('video:https://static.tildacdn.com/vide3137-3335-4439-b138-373930326161/klip-hero-final.mp4|', 'https://dprofile.ru/case/197117/tancy-na-snegu-koncept-klipa-bez-kamery-i-akterov', 'Хаски «Танцы на снегу»', 'Клип', 'Визуальный ряд под трек артиста', 'Клип или визуалайзер', '30–100 тыс ₽'),
   (None, 'https://t.me/perasperagram/2173', 'Ведьмак · кураторы школы', 'Мультфильм', 'Короткая история с персонажем', 'Ролик со звуком', '30–100 тыс ₽'),
   (None, None, 'Пример подбираем', 'Объясняющий или тематический ролик', 'Как работает продукт, или художественный ролик на 20–90 секунд', 'Ролик с графикой, звуком и титрами', '10–60 тыс ₽'),
   ('cases/godovshina-2.webp', 'https://perasperadastranew.github.io/guides/rolik-po-foto/', 'Годовщина родителей', 'AI-фильм', 'История с реальными героями и локациями', 'Фильм со звуком и титрами', '30–80 тыс ₽')]),
]
def media(src, credit):
    if src is None:
        return '<span class="phx"><span>%s</span></span>' % credit
    if src.startswith('video:'):
        u, poster = src[6:].split('|')
        return '<video muted loop playsinline preload="%s"%s data-src="%s"></video>' % ('none' if poster else 'metadata', (' poster="%s"' % poster) if poster else '', u)
    return '<img src="%s" alt="%s" loading="lazy">' % (src, credit)
pans = ''
for i, (k, n, who, rows) in enumerate(CATS):
    rr = ''
    for src, link, credit, name, task, give, price in rows:
        m = media(src, credit)
        if link:
            ex = '<a class="exm" href="%s" target="_blank" rel="noopener"><span class="th3">%s<i class="go" aria-hidden="true">↗</i></span><span class="cap2">%s <em>↗</em></span></a>' % (link, m, credit)
        else:
            ex = '<div class="exm"><span class="th3">%s</span><span class="cap2 soon">%s</span></div>' % (m, credit)
        rr += '<tr><th scope="row"><b>%s</b></th><td class="pd"><p>%s</p><p class="gv"><span>Сдаёшь:</span> %s</p><div class="pc">%s</div></td><td class="t2">%s</td></tr>' % (name, task, give, price, ex)
    pans += '<div class="cat" id="cp-%s"><div class="cath"><span class="cn2">%02d</span><h3>%s</h3><p>%s</p></div><div class="tw"><table class="prt"><thead><tr><th>Проект</th><th>Задача и цена</th><th>Пример</th></tr></thead><tbody>%s</tbody></table></div></div>' % (k, i + 1, n, who, rr)
b3 = pans
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
t3 = '<p>Удобнее делить проекты по типу работы: фотореализм, графика и видео. Для каждого — кто заказывает, что ты сдаёшь и вилка цен на 2026 год. Внизу вилки — один кадр, один круг правок и один формат, вверху — набор кадров, адаптации и передача прав.</p>'
out.append(section(4, '04', 'Заказы и цены', 'Какие проекты заказывают <span class="s">и сколько они стоят</span>', t3, b3 + '\n<p class="micro" style="margin:56px 0 14px">Сколько стоит час в разных проектах</p>\n' + chart))

# --- I.05 Что изменили нейросети — по категориям
b2 = sec_body('pg-2')
R = dict((re.sub('<[^>]+>', '', m.group(1)).strip(), m.group(0)) for m in re.finditer(r'<tr><td><b>(.*?)</b>.*?</tr>', b2, re.S))
def BR(name, sub, was, wasd, now, nowd, pct, x):
    return '<tr><td><b>%s</b><small>%s</small></td><td class="n"><span class="t">%s</span>%s</td><td class="nn"><span class="t a">%s</span>%s</td><td><div class="bb"><i style="--w:100%%"></i><i class="a" style="--w:%d%%"></i></div><span class="x">%s</span></td></tr>' % (name, sub, was, wasd, now, nowd, pct, x)
G = lambda t, d: '<tr class="grp"><td colspan="4"><span>%s</span></td></tr>' % t
body_rows = (G('Фотореализм', 'предметка, модели, фотостиль') + R['Предметная фотосессия'] +
  BR('Фотосессия с моделью', 'серия образов для бренда', '1–2 недели', 'Кастинг, модель, стилист, фотограф, студия и ретушь', '1–2 дня', 'Карточка модели и генерация образов', 15, '≈ в 7 раз быстрее') +
  G('2D и 3D-графика', 'KV, иллюстрации, маскоты, продукт') +
  BR('Key visual и адаптации', 'главный образ и 5–10 форматов', '1–2 недели', 'Съёмка или 3D, дизайнер на адаптации', '2–3 дня', 'Генерация образа, вёрстка в Figma', 25, '≈ в 4 раза быстрее') +
  BR('Серия иллюстраций', '5–10 кадров в одном стиле', '2–3 недели', 'Иллюстратор рисует серию вручную: эскизы, чистовик, правки', '2–4 дня', 'Один креатор: стиль, генерация, отбор и доводка', 24, '≈ в 4 раза быстрее') +
  BR('Маскот', 'персонаж и серия сцен', '3–4 недели', 'Иллюстратор, потом 3D-моделлер и визуализатор', '3–5 дней', 'Карточка персонажа и сцены в нейросетях', 23, '≈ в 4 раза быстрее') +
  R['Один кадр продукта'] +
  G('Видео', 'реклама, клипы, мультики, объясняющие ролики') + R['Рекламный ролик'] +
  BR('Клип', 'под трек артиста', '4–8 недель', 'Режиссёр, съёмочная группа, локации, монтаж и цветокор', '1–2 недели', 'Шоты в нейросетях, монтаж и цвет', 25, '≈ в 4 раза быстрее') +
  BR('Мультфильм', '1 минута с персонажем', '2–3 месяца', 'Сценарий, раскадровка, художники и аниматоры', '1–2 недели', 'Персонаж, сцены и анимация в нейросетях', 14, '≈ в 7 раз быстрее') +
  BR('Объясняющий ролик', '60 секунд о продукте', '3–4 недели', 'Сценарист, иллюстратор, моушн-дизайнер, диктор', '3–5 дней', 'Графика, анимация и голос с нейросетями', 23, '≈ в 4 раза быстрее'))
b2 = re.sub(r'<tbody>.*?</tbody>', '<tbody>' + body_rows + '</tbody>', b2, flags=re.S)
b2 = re.sub(r'<p class="fn">.*?</p>', '<p class="fn">Разница посчитана по серединам вилок, рабочий день — 8 часов.</p>', b2, flags=re.S)
big = '<div class="b31"><div class="walk" aria-hidden="true"><img class="w1" src="img/hc-5.webp" alt=""><img class="w2" src="img/hc-5.webp" alt=""><img class="w3" src="img/hc-5.webp" alt=""><img class="w0" src="img/hc-5.webp" alt=""><span class="n3">3</span><span class="n1">1</span></div><div><span class="micro">Главный итог</span><p>То, что раньше делала команда из трёх человек — фотограф, дизайнер и монтажёр, — теперь делает один специалист с нейросетями.</p></div></div>'
out.append(section(5, '05', 'Было и стало', 'Что изменили <span class="s">нейросети</span>',
  '<p>Одни и те же задачи по категориям — раньше с командой и съёмкой, теперь с нейросетями. Серая полоса — сколько уходило раньше, красная — сколько сейчас.</p>', b2 + '\n' + big))

# --- I.06 Клиенты
out.append(section(6, '06', 'Клиенты', 'Чего хотят клиенты <span class="s">и где работать</span>', sec_txt('pg-5'), nofn(sec_body('pg-5'))))

# ================= ЧАСТЬ II. ПОШАГОВО
out.append(part('p2', 'II', 'Пошаговый план', 'Семь шагов от цели до первого оплаченного заказа.'))
def step(id_src, n, title, txt=None, body=None):
    return section(id_src.replace('pg-', 'st'), '%02d' % n, '', title, txt if txt is not None else sec_txt(id_src), body if body is not None else nofn(sec_body(id_src)))
def _dir(m):
    t = m.group(0)
    h = re.search(r'<h3>(.*?) → <span class="s">(.*?)</span></h3>', t)
    ks = re.findall(r'<div class="k"><span class="micro">(.*?)</span>(.*?)</div>', t, re.S)
    wide = re.search(r'<div class="wide">.*?</div>', t, re.S).group(0)
    head_ = re.match(r'<div class="dir[^"]*"[^>]*>', t).group(0)
    frm = ks[0]
    rest = ''.join('<div class="k"><span class="micro">%s</span>%s</div>' % k for k in ks[1:])
    return head_ + '<div class="fromto"><div class="fr"><span class="micro">Откуда</span><h3>%s</h3><span class="micro">%s</span>%s</div><div class="to"><span class="micro">Куда расти</span><h3>%s</h3><div class="ks">%s</div>%s</div></div></div>' % (h.group(1), frm[0], frm[1], h.group(2), rest, wide)
b6 = nofn(sec_body('pg-6'))
b6 = re.sub(r'<div class="dir[ "][^>]*>.*?<div class="wide">.*?</div></div>', _dir, b6, flags=re.S)
b6 = b6.replace('</div>\n<div class="dir', '</div>\n<div class="dir', 1)
out.append(step('pg-6', 1, 'Определи цель и <span class="s">откуда заходишь</span>', body=b6))
LEARN = [
 ('Насмотренность', 'Собирай референсы, разбирай рекламу, клипы и кино: что в кадре работает и почему. Это то, что нейросеть за тебя не сделает.'),
 ('Основы дизайна', 'Композиция, цвет, свет, типографика. Без них генерация остаётся «просто картинкой».'),
 ('Процесс', 'Бриф → идея → эскиз → производство → отбор → сдача. Научись проходить его целиком, а не только этап генерации.'),
 ('Инструменты', 'Одна текстовая нейросеть, одна-две визуальные и Figma для сборки. Больше на старте не нужно.'),
 ('Обратная связь', 'Показывай работы тем, кто сильнее тебя. Так растёшь быстрее всего — и быстрее всего замечаешь собственные ошибки.'),
]
learn = '<ol class="check">' + ''.join('<li><b>%s.</b> %s</li>' % x for x in LEARN) + '</ol>'
GUIDES_SHORT = '<div class="lrn"><a href="https://perasperadastra.ru/mission-to-ai" target="_blank" rel="noopener"><span class="micro">Курс</span><b>Mission to AI ↗</b><span>Генерация графики и видео с обратной связью от кураторов</span></a><a href="https://t.me/perasperagram" target="_blank" rel="noopener"><span class="micro">Бесплатно</span><b>Наш Telegram-канал ↗</b><span>Разборы проектов, новые нейросети, эфиры и гайды</span></a><a href="#pg-end"><span class="micro">Бесплатно</span><b>Гайды школы ↓</b><span>AI-клип и AI-фильм с реальными героями</span></a></div>'
out.append(section('learn', '02', '', 'Прокачай <span class="s">базу</span>',
  '<p>Нейросеть усиливает то, что уже есть внутри: есть вкус и идея — будет сильный результат, нет — будет среднее. Поэтому сначала база, потом сервисы.</p>',
  learn + '\n<p class="micro" style="margin:36px 0 12px">Где учиться</p>\n' + GUIDES_SHORT))
out.append(step('pg-7', 3, 'Опиши <span class="s">свои услуги</span>'))
out.append(step('pg-8', 4, 'Собери минимальный <span class="s">стек</span>'))
def exg(items, cap):
    return '<p class="micro" style="margin:40px 0 12px">%s</p><div class="grid4 gal sq ex3">%s</div>' % (cap, ''.join(fig(*it) for it in items))
feat = '<a class="feat" href="%s" target="_blank" rel="noopener"><span class="fim"><video muted loop playsinline preload="none" poster="cases/knives-2.webp" data-src="cases/v-knives.mp4"></video></span><span class="ftx"><span class="micro">Пример проекта</span><b>Simple Knives</b><span class="fau">Анастасия Грачева · студентка Mission to AI</span><span class="fds">Коллекция ножей для выдуманного бренда, сделанная с нуля: идея, продукт, key visual, серия кадров и рекламный ролик в одном стиле. Хороший ориентир, как должен выглядеть первый проект целиком.</span><span class="flk">Смотреть кейс на Dprofile ↗</span></span></a>' % CASE['knives'][0]
first = feat + exg([('cases/eaglips.webp', 'Продукт с нуля', 'eaglips'), ('img/case-lumera-1.webp', 'Выдуманный гаджет', 'lumera'), ('cases/mako.webp', 'Маскот', 'mako')], 'Так начинали ученики')
first += '<p class="tip"><b>Больше 50 наград на Dprofile</b> собрали ученики школы — многие с первых учебных проектов, сделанных с нуля. Посмотри их кейсы, чтобы понять планку.</p>'
out.append(step('pg-9', 5, 'Сделай первый <span class="s">проект</span>', body=nofn(sec_body('pg-9')) + first))
out.append(section('st10', '06', '', 'Оформи кейс <span class="s">и покажи работы</span>', sec_txt('pg-10'),
  nofn(sec_body('pg-10')) + exg([('cases/hronos-box.webp', 'Кейс на сайте', 'hronos'), ('cases/v-lappi.jpg', 'Кейс на сайте', 'lappi'), ('cases/v-knives.jpg', 'Кейс на Dprofile', 'knives')], 'Как оформляют кейсы у нас') + '\n<p class="micro" style="margin:48px 0 12px">Где показывать</p>\n' + nofn(sec_body('pg-11'))))
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
    if sid == 'pg-s7':
        t = t[:t.rindex('</section>')] + '<p class="note"><b>Как мы считали.</b> Таблицы и калькулятор собраны только по открытой информации с сайтов платформ: цены, пакеты и лимиты. Сервисы часто меняют тарифы, поэтому данные могут быть неточными или устареть — перед оплатой сверься с сайтом. Мы с уважением относимся к каждому сервису и сравниваем их просто математически, без рекламы и оценок «лучше-хуже».</p>\n</section>'
    out.append(t + '\n\n')

# ================= ИТОГ
CON = [('Рынок новый — и это возможность', 'Правила ещё пишутся, а большинство специалистов только разбираются, как работать с нейросетями. Сильных людей мало, и рынок их активно ищет.'),
       ('Будь Т‑специалистом', 'Глубоко в своём — дизайне, моушне, монтаже — и широко в смежном. Нейросети дают ширину, база даёт глубину.'),
       ('Делай креативные проекты', 'Среднее ничего не стоит: нейросеть подтягивает до среднего всех. Платят за идею, вкус и смелое решение.'),
       ('Учись вести проект', 'Понимать задачу, договариваться о сроках и правках, сдавать вовремя. На это почти никто не делает ставку — и зря.'),
       ('Развивай личный бренд', 'Показывай работы и процесс. Заказчик выбирает того, кого видит и кому доверяет, а выделиться через блог сейчас проще, чем когда-либо.')]
con = '<ol class="con">' + ''.join('<li><span class="cnum">%02d</span><b>%s</b><p>%s</p></li>' % (k + 1, c[0], c[1]) for k, c in enumerate(CON)) + '</ol>'
CLOSED = 'https://t.me/perasperagram'  # TODO: ссылка на закрытый канал
GD = [(CLOSED, None, 'https://static.tildacdn.com/vide3137-3335-4439-b138-373930326161/klip-hero-final.mp4', 'Гайд · в закрытом канале', 'AI-клип', 'Клип с персонажем без съёмки: от идеи до монтажа'),
      (CLOSED, 'img/g-rolik.webp', None, 'Гайд · в закрытом канале', 'AI-фильм с реальными героями', 'Фильм по семейным фото: реальные люди и локации')]
def gcard(u, img, vid, k, t, d):
    med = ('<img src="%s" alt="" loading="lazy">' % img) if img else ('<span class="ty" aria-hidden="true">%s</span><video muted loop playsinline preload="metadata" data-src="%s"></video>' % (t[0], vid))
    return '<a class="gd%s" href="%s" target="_blank" rel="noopener"><div class="cm">%s</div><div class="cb"><span class="micro">%s</span><b>%s <i aria-hidden="true">↗</i></b><span>%s</span></div></a>' % ('' if img else ' t', u, med, k, t, d)
gd = '<div class="gds">' + ''.join(gcard(*g) for g in GD) + '</div>'
out.append('''<section class="step fin" id="pg-end">%s
%s
<div class="live"><span class="micro">Прямой эфир · 28 октября, 19:00 по Москве</span><h3>Разберём всё это вживую</h3><p>Покажем, как мы работаем с нейросетями: идеи и решения на нас, рутина на ИИ. Ответим на вопросы и разберём, что дизайнеру нужно уметь в 2027 году. Ссылка на эфир, вся информация и другие методички — в нашем закрытом канале.</p><a class="btn" href="https://t.me/perasperagram" target="_blank" rel="noopener">Вступить в закрытый канал ↗</a></div>
<p class="micro" style="margin:56px 0 14px">Гайды школы — в закрытом Telegram-канале</p>
%s
</section>

''' % (head('→', 'Итог', 'Что унести <span class="s">из гайда</span>', '<p>Пять выводов, на которых держится всё остальное.</p>'), con, gd))

body = ''.join(out)
# типографика: неразрывный пробел после коротких слов, чтобы предлоги не висели в конце строки
SHORT = r'(?:[вксуояиаВКСУОЯИА]|на|по|за|из|от|до|не|но|же|для|без|что|как|или|при|об|во|со|ко|под|над|про|это|их|его|её|и\.)'
def _nb(m):
    t = m.group(0)
    return re.sub(r'(?<![\w-])(' + SHORT + r') (?=[\w«(0-9—])', '\\1\u00a0', t)
parts = re.split(r'(<script.*?</script>|<style.*?</style>|<[^>]+>)', body, flags=re.S)
body = ''.join(x if (x.startswith('<')) else _nb(re.match(r'.*', x, re.S)) for x in parts)
body = body.replace(' —', '\u00a0—')
def _hfix(m):
    t = m.group(3)
    t = re.sub(r'([^\s<>]+)\u00a0([^\s<>]+)', r'<span class="nw">\1 \2</span>', t)
    return '<h%s%s>%s</h%s>' % (m.group(1), m.group(2), t, m.group(1))
body = re.sub(r'<h([12])([^>]*)>(.*?)</h\1>', _hfix, body, flags=re.S)
a = s.index('<header>'); b = s.index('<footer')
res = s[:a] + body + s[b:]
res = res.replace('<title>Как начать в AI-индустрии, короткая версия</title>', '<title>Как начать в AI-индустрии</title>')

css = open(os.path.join(D, 'add.css'), encoding='utf-8').read()
js = open(os.path.join(D, 'add.js'), encoding='utf-8').read() + '\n' + open(os.path.join(D, 'birds3d.js'), encoding='utf-8').read() + '\n' + open(os.path.join(D, 'towers.js'), encoding='utf-8').read()
i = res.index('</style>'); res = res[:i] + css + res[i:]
i = res.rindex('</body>'); res = res[:i] + '<script>' + js + '</script>\n' + res[i:]
open(OUT, 'w', encoding='utf-8').write(res)
print('ok', len(res))
