"""Собирает отдельные страницы этапов гайда «Кейс: от готового макета до Behance и Dprofile».

Источник один — mtw/upakovka-kejsov/index.html. Скрипт кладёт копию в etap-1/ … etap-7/
и включает в ней режим одного этапа (window.KEJS_STAGE).
Внутри урока ZenClass страница сама включает fit to page, ?fit=1 добавлять не нужно.
Руками etap-*/index.html не правим: после изменения index.html запусти скрипт ещё раз.

Запуск из корня репозитория: python3 mtw/upakovka-kejsov/build_stages.py
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
TITLES = {1: 'Контент', 2: 'Мокапы и фото', 3: 'Стиль кейса', 4: 'Оформление слайдов',
          5: 'Обложка и название', 6: 'Анимация', 7: 'Публикация'}

src = open(os.path.join(HERE, 'index.html'), encoding='utf-8').read()
assert 'window.KEJS_STAGE' in src, 'в index.html нет поддержки window.KEJS_STAGE'
assert src.count('<title>') == 1 and src.count('<head>') == 1

for n, title in TITLES.items():
    auto_fit = ("<script>try{if(window.self!==window.top&&!/(fit|embed)=/.test(location.search))"
                "history.replaceState(null,'',location.pathname+(location.search?location.search+'&':'?')+'fit=1'+location.hash)}catch(e){}</script>")
    page = src.replace('<head>', f'<head><script>window.KEJS_STAGE="{n}"</script>' + auto_fit, 1)
    page = re.sub(r'<title>[^<]*</title>', f'<title>Кейс. {title}</title>', page)
    # страница лежит на уровень глубже: поправить относительные ссылки и картинки
    page = page.replace('href="../', 'href="../../').replace('src="../', 'src="../../').replace('"../../mtw-diary/', '"../../../mtw-diary/')
    page = page.replace('src="img/', 'src="../img/')
    page = page.replace('base=el.dataset.base||"../../mtw-diary/cases/"', 'base=el.dataset.base||"../../../mtw-diary/cases/"')
    page = page.replace('href="../../mtw-diary/#case=${id}"', 'href="../../../mtw-diary/#case=${id}"')
    out = os.path.join(HERE, f'etap-{n}')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(page)
    print(f'OK: etap-{n}/index.html — {title}')
