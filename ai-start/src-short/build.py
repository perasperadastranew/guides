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
<a href="#pg-p2"><b><i>II</i>Пошагово</b><span>От цели до первого заказа</span></a>
<a href="#pg-p3"><b><i>III</i>Нейросети</b><span>Текстовые и визуальные</span></a>
<a href="#pg-p4"><b><i>IV</i>Подписки</b><span>За что платить и сколько</span></a>
<a href="#pg-end"><b><i>→</i>Итог</b><span>Пять выводов, эфир и гайды</span></a>
</nav>''', hdr, flags=re.S)
out.append(hdr)

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
th = ''.join('<li><div class="tl"><span class="micro">%02d</span><h3>%s</h3><b>%s</b></div><p>%s</p></li>' % (i + 1, t, b, d) for i, (t, b, d) in enumerate(TH))
out.append(section(1, '01', 'Что происходит', 'Что происходит <span class="s">на рынке</span>',
  '<p>Пять тезисов о том, что сейчас на самом деле происходит с профессией: как быстро пришли нейросети, что с увольнениями, какими стали проекты и кто нужен рынку.</p>',
  '<ol class="th">' + th + '</ol>\n<p class="tip"><b>Вывод.</b> «Всех сокращают из-за ИИ» — часто отговорка. Нейросети не отменяют дизайнеров, они отменяют средний результат. Людей, которые умеют с ними работать, ищут активнее остальных.</p>'))

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
 'lappi': ('https://perasperadastra.ru/sreda-lappi', 'Лаппи'),
 'hronos': ('https://perasperadastra.ru/sreda-hronos', 'Хронос'),
 'eaglips': ('https://dprofile.ru/case/173955/eaglips', 'Eaglips · Милана Гавриченко'),
 'lumera': ('https://dprofile.ru/case/174067/lumera', 'Lumera · Лейла Исхакова'),
 'mofu': ('https://dprofile.ru/case/179802/mofu-mofu-pusistye-obvesy', 'mofu-mofu · Арина Галимова'),
 'husky': ('https://perasperadastra.ru/klip', 'Хаски'),
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
CATS = [
 ('foto', 'Фото и реализм', 'Маркетплейсы, e-com, бренды одежды и косметики. Нужно много реалистичных кадров — быстрее и дешевле съёмки.',
  [fig('img/c-t-prodshoot.webp', 'Предметка'), fig('img/c-t-aimodel.webp', 'AI-модель'), fig('img/c-t-outfit.webp', 'Замена одежды'), fig('img/c-t-interior.webp', 'Интерьер')],
  [('Предметная фотосессия', 'Продукт в нескольких сетах без студии', 'Карточка продукта, 3 hero и 3 lifestyle', '5–25 тыс ₽'),
   ('Фотосессия с AI-моделью', 'Модель бренда в разных образах и с продуктом', 'Карточка модели и серия кадров', '5–20 тыс ₽'),
   ('Фотостиль бренда', 'Единый стиль кадров для сайта и соцсетей', 'Серия кадров и правила стиля', '5–25 тыс ₽'),
   ('Визуализация интерьера', 'Пространство до ремонта или стройки', 'Серия ракурсов', 'по объёму')]),
 ('graf', '2D и 3D-графика', 'Бренды и агентства: кампании, запуски, айдентика. Нужен узнаваемый стиль на всех материалах, а не одна картинка.',
  [fig('cases/v-knives.jpg', 'Key visual', 'knives'), fig('cases/mako.webp', 'Маскот', 'mako'), fig('cases/hronos-box.webp', 'Упаковка', 'hronos'), fig('img/c-t-ident.webp', 'Айдентика')],
  [('Key visual и адаптации', 'Главный образ кампании для баннеров и наружки', 'KV и адаптации под форматы', '5–30 тыс ₽'),
   ('Иллюстрации для бренда', 'Графический язык, набор иллюстраций', 'Серия из 5–15 кадров в одном стиле', '5–30 тыс ₽'),
   ('Маскот', 'Персонаж бренда в разных позах и ситуациях', 'Карточка персонажа и серия сцен', 'по объёму'),
   ('Упаковка и айдентика', 'Концепт упаковки, графика бренда', 'Концепт, мокапы, носители', 'по объёму'),
   ('Генерация концептов', 'Варианты визуального направления до запуска', '2–3 направления с мудбордами', '5–15 тыс ₽')]),
 ('prod', 'Продукты и digital', 'Стартапы, продуктовые команды, сайты и сервисы. Нужно показать то, чего ещё нет, или красиво упаковать продукт на экране.',
  [fig('cases/eaglips.webp', 'AI-продукт', 'eaglips'), fig('img/case-lumera-1.webp', 'Концепт гаджета', 'lumera'), fig('cases/mofu.webp', 'Продукт и персонажи', 'mofu'), fig('img/c-t-concept3d.webp', '3D-концепт')],
  [('AI-продукт', 'Придумать и показать продукт, которого нет', 'Метафора, карточка продукта, KV, мокапы', '30–100 тыс ₽'),
   ('3D-визуализация и концепты', 'Форма, материалы, ракурсы', 'Серия ракурсов и деталей', '5–30 тыс ₽'),
   ('Фотоконтент для сайта', 'Фото для лендинга без съёмки', 'Серия кадров в одном стиле', '5–25 тыс ₽'),
   ('Мокапы интерфейсов', 'Экраны в живой сцене для презентации', '1–5 сцен', '1–5 тыс ₽')]),
 ('vid', 'Видео', 'Бренды, медиа и артисты: ролики для рекламы, соцсетей и музыкантов.',
  [fig(None, 'AI-клип', 'husky', 'https://static.tildacdn.com/vide3137-3335-4439-b138-373930326161/klip-hero-final.mp4'), fig('cases/godovshina.webp', 'Фильм по фото', 'godov'), fig('cases/v-lappi.jpg', 'Анимация персонажа', 'lappi', 'cases/v-lappi.mp4'), fig('cases/v-knives.jpg', 'Рекламный ролик', 'knives', 'cases/v-knives.mp4')],
  [('Рекламный ролик', 'Продукт через рекламный приём, пэкшот в финале', 'Ролик и нарезки под площадки', '30–100 тыс ₽'),
   ('Клип и визуалайзер', 'Визуальный ряд под трек артиста', 'Клип или визуалайзер', 'по объёму'),
   ('Мультфильм и анимация персонажа', 'Короткая история с маскотом или героем', 'Ролик со звуком', 'по объёму'),
   ('Объясняющий ролик', 'Как работает продукт или сервис, за 30–90 секунд', 'Ролик с графикой и озвучкой', 'по объёму'),
   ('Тематический ролик', 'Исторический, художественный или мемный ролик на 20–60 секунд', 'Ролик со звуком и титрами', '5–50 тыс ₽')]),
]
tabsc = '<div class="tabs" role="tablist" aria-label="Тип работы" style="margin:0 0 18px">' + ''.join('<button role="tab" aria-selected="%s" aria-controls="cp-%s" id="ct-%s">%s</button>' % ('true' if i == 0 else 'false', k, k, n) for i, (k, n, _, _, _) in enumerate(CATS)) + '</div>'
pans = ''
for i, (k, n, who, figs, rows) in enumerate(CATS):
    rr = ''.join('<tr><td><b>%s</b></td><td class="n">%s</td><td class="n">%s</td><td>%s</td></tr>' % r for r in rows)
    pans += '<div class="gp%s" role="tabpanel" id="cp-%s" aria-labelledby="ct-%s"><div class="grp2"><div class="gh"><h3>%s</h3><p><span class="micro">Кто заказывает</span> %s</p></div><div class="grid4 gal sq">%s</div><div class="tw"><table class="pt"><thead><tr><th>Проект</th><th>Пример задачи</th><th>Что сдаёшь</th><th>Вилка</th></tr></thead><tbody>%s</tbody></table></div></div></div>' % (' on' if i == 0 else '', k, k, n, who, ''.join(figs), rr)
b3 = tabsc + pans
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
t3 = '<p>Удобнее делить проекты по типу работы: фото, графика, продукты и видео. В каждой вкладке — кто заказывает, что ты сдаёшь и вилка цен на 2026 год. Внизу вилки — один кадр, один круг правок и один формат, вверху — набор кадров, адаптации и передача прав.</p>'
out.append(section(4, '04', 'Заказы и цены', 'Какие проекты заказывают <span class="s">и сколько они стоят</span>', t3, b3 + '\n<p class="micro" style="margin:56px 0 14px">Сколько стоит час в разных проектах</p>\n' + chart))

# --- I.05 Что изменили нейросети — по категориям
b2 = sec_body('pg-2')
R = dict((re.sub('<[^>]+>', '', m.group(1)).strip(), m.group(0)) for m in re.finditer(r'<tr><td><b>(.*?)</b>.*?</tr>', b2, re.S))
ILL = '<tr><td><b>Серия иллюстраций</b><small>5–10 кадров в одном стиле</small></td><td class="n"><span class="t">2–3 недели</span>Иллюстратор рисует серию вручную: эскизы, чистовик, правки</td><td class="nn"><span class="t a">2–4 дня</span>Один креатор: стиль, генерация, отбор и доводка</td><td><div class="bb"><i style="--w:100%"></i><i class="a" style="--w:24%"></i></div><span class="x">≈ в 4 раза быстрее</span></td></tr>'
G = lambda t: '<tr class="grp"><td colspan="4">%s</td></tr>' % t
body_rows = G('Фото') + R['Предметная фотосессия'] + G('Графика и 3D') + ILL + R['Один кадр продукта'] + G('Видео') + R['Рекламный ролик']
b2 = re.sub(r'<tbody>.*?</tbody>', '<tbody>' + body_rows + '</tbody>', b2, flags=re.S)
b2 = re.sub(r'<p class="fn">.*?</p>', '<p class="fn">Разница посчитана по серединам вилок, рабочий день — 8 часов.</p>', b2, flags=re.S)
big = '<div class="b31"><div class="nums" aria-hidden="true"><b>3</b><i>→</i><b class="a">1</b></div><div><span class="micro">Главный итог</span><p>То, что раньше делала команда из трёх человек — фотограф, дизайнер и монтажёр, — теперь делает один специалист с нейросетями.</p></div></div>'
out.append(section(5, '05', 'Было и стало', 'Что изменили <span class="s">нейросети</span>',
  '<p>Одни и те же задачи по категориям — раньше с командой и съёмкой, теперь с нейросетями. Серая полоса — сколько уходило раньше, красная — сколько сейчас.</p>', b2 + '\n' + big))

# --- I.06 Клиенты
out.append(section(6, '06', 'Клиенты', 'Чего хотят клиенты <span class="s">и где работать</span>', sec_txt('pg-5'), nofn(sec_body('pg-5'))))

# ================= ЧАСТЬ II. ПОШАГОВО
out.append(part('p2', 'II', 'Пошагово', 'Семь шагов от цели до первого оплаченного заказа.'))
def step(id_src, n, title, txt=None, body=None):
    return section(id_src.replace('pg-', 'st'), '%02d' % n, 'Шаг %d' % n, title, txt if txt is not None else sec_txt(id_src), body if body is not None else nofn(sec_body(id_src)))
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
out.append(section('learn', '02', 'Шаг 2', 'Прокачай <span class="s">базу</span>',
  '<p>Нейросеть усиливает то, что уже есть внутри: есть вкус и идея — будет сильный результат, нет — будет среднее. Поэтому сначала база, потом сервисы.</p>',
  learn + '\n<p class="micro" style="margin:36px 0 12px">Где учиться</p>\n' + GUIDES_SHORT))
out.append(step('pg-7', 3, 'Опиши <span class="s">свои услуги</span>'))
out.append(step('pg-8', 4, 'Собери минимальный <span class="s">стек</span>'))
def exg(items, cap):
    return '<p class="micro" style="margin:40px 0 12px">%s</p><div class="grid4 gal sq ex3">%s</div>' % (cap, ''.join(fig(*it) for it in items))
first = exg([('cases/eaglips.webp', 'Продукт с нуля', 'eaglips'), ('img/case-lumera-1.webp', 'Выдуманный гаджет', 'lumera'), ('cases/mako.webp', 'Маскот', 'mako')], 'Так начинали ученики')
first += '<p class="tip"><b>Больше 50 наград на Dprofile</b> собрали ученики школы — многие с первых учебных проектов, сделанных с нуля. Посмотри их кейсы, чтобы понять планку.</p>'
out.append(step('pg-9', 5, 'Сделай первый <span class="s">проект</span>', body=nofn(sec_body('pg-9')) + first))
out.append(section('st10', '06', 'Шаг 6', 'Оформи кейс <span class="s">и покажи работы</span>', sec_txt('pg-10'),
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
    out.append(t + '\n\n')

# ================= ИТОГ
CON = [('Рынок новый — и это возможность', 'Правила ещё пишутся, а большинство специалистов только разбираются, как работать с нейросетями. Сильных людей мало, и рынок их активно ищет.'),
       ('Будь Т‑специалистом', 'Глубоко в своём — дизайне, моушне, монтаже — и широко в смежном. Нейросети дают ширину, база даёт глубину.'),
       ('Делай креативные проекты', 'Среднее ничего не стоит: нейросеть подтягивает до среднего всех. Платят за идею, вкус и смелое решение.'),
       ('Учись вести проект', 'Понимать задачу, договариваться о сроках и правках, сдавать вовремя. На это почти никто не делает ставку — и зря.'),
       ('Развивай личный бренд', 'Показывай работы и процесс. Заказчик выбирает того, кого видит и кому доверяет, а выделиться через блог сейчас проще, чем когда-либо.')]
con = '<ol class="con">' + ''.join('<li><span class="cnum">%02d</span><b>%s</b><p>%s</p></li>' % (k + 1, c[0], c[1]) for k, c in enumerate(CON)) + '</ol>'
GD = [('https://perasperadastra.ru/klip', None, 'https://static.tildacdn.com/vide3137-3335-4439-b138-373930326161/klip-hero-final.mp4', 'Гайд', 'AI-клип', 'Клип с персонажем без съёмки: от идеи до монтажа'),
      ('https://perasperadastranew.github.io/guides/rolik-po-foto/', 'img/g-rolik.webp', None, 'Гайд', 'AI-фильм с реальными героями', 'Фильм по семейным фото: реальные люди и локации')]
def gcard(u, img, vid, k, t, d):
    med = ('<img src="%s" alt="" loading="lazy">' % img) if img else ('<span class="ty" aria-hidden="true">%s</span><video muted loop playsinline preload="metadata" data-src="%s"></video>' % (t[0], vid))
    return '<a class="gd%s" href="%s" target="_blank" rel="noopener"><div class="cm">%s</div><div class="cb"><span class="micro">%s</span><b>%s <i aria-hidden="true">↗</i></b><span>%s</span></div></a>' % ('' if img else ' t', u, med, k, t, d)
gd = '<div class="gds">' + ''.join(gcard(*g) for g in GD) + '</div>'
out.append('''<section class="step fin" id="pg-end">%s
%s
<div class="live"><span class="micro">Прямой эфир</span><h3>Разберём всё это вживую</h3><p>На прямом эфире покажем, как мы работаем с нейросетями: идеи и решения на нас, рутина на ИИ. Ответим на вопросы и разберём, что дизайнеру нужно уметь в 2027 году. Анонс — в нашем Telegram-канале.</p><a class="btn" href="https://t.me/perasperagram" target="_blank" rel="noopener">Telegram-канал ↗</a></div>
<p class="micro" style="margin:56px 0 14px">Бесплатные гайды школы</p>
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
body = re.sub(r'<h([12])([^>]*)>(.*?)</h\1>', lambda m: '<h%s%s>%s</h%s>' % (m.group(1), m.group(2), m.group(3).replace('\u00a0', ' '), m.group(1)), body, flags=re.S)
a = s.index('<header>'); b = s.index('<footer')
res = s[:a] + body + s[b:]
res = res.replace('<title>Как начать в AI-индустрии, короткая версия</title>', '<title>Как начать в AI-индустрии</title>')

css = open(os.path.join(D, 'add.css'), encoding='utf-8').read()
js = open(os.path.join(D, 'add.js'), encoding='utf-8').read()
i = res.index('</style>'); res = res[:i] + css + res[i:]
i = res.rindex('</body>'); res = res[:i] + '<script>' + js + '</script>\n' + res[i:]
open(OUT, 'w', encoding='utf-8').write(res)
print('ok', len(res))
