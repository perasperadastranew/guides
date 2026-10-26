"""Собирает отдельные страницы этапов гайда «Лендинг с нейросетями».

Источник один — mtw/lending/index.html. Скрипт кладёт копию в etap-1/ … etap-6/
и включает в ней режим одного этапа (window.LEND_STAGE).
Руками etap-*/index.html не правим: GitHub Actions пересобирает их
после каждого изменения index.html.

Запуск из корня репозитория: python3 mtw/lending/build_stages.py
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
TITLES = {1: 'Тема и концепция', 2: 'Смысловой прототип', 3: 'Стайлборд', 4: 'Вайрфрейм', 5: 'Дизайн', 6: 'Кейс и публикация'}

src = open(os.path.join(HERE, 'index.html'), encoding='utf-8').read()
assert 'window.LEND_STAGE' in src, 'в index.html нет поддержки window.LEND_STAGE'
assert src.count('<title>') == 1 and src.count('<head>') == 1

for n, title in TITLES.items():
    page = src.replace('<head>', f'<head><script>window.LEND_STAGE="{n}"</script>', 1)
    page = re.sub(r'<title>[^<]*</title>', f'<title>Этап {n}. {title} — Лендинг с нейросетями</title>', page)
    # страница лежит на уровень глубже: поправить относительные ссылки на методички
    page = page.replace('href="../../mtw-metodichki/', 'href="../../../mtw-metodichki/')
    out = os.path.join(HERE, f'etap-{n}')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(page)
    print(f'OK: etap-{n}/index.html — {title}')
