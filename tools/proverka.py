#!/usr/bin/env python3
"""Автопроверка методичек PERASPERADASTRA перед публикацией.

  python3 tools/proverka.py                 # все страницы: только ошибки
  python3 tools/proverka.py --changed BASE  # + предупреждения и мобильная ширина для страниц, изменённых после BASE
  python3 tools/proverka.py --mobile        # проверить ширину 390 px у всех изменённых (нужен playwright)

Ошибки (проверка не проходит) — на всех страницах:
  · нет <!doctype html>, lang="ru", charset, viewport;
  · нет <meta name="robots" content="noindex"> — методички закрыты от поисковиков;
  · название школы не как PERASPERADASTRA («Per Aspera Ad Astra» и т. п.).
Предупреждения — только на изменённых страницах (не блокируют, но их надо посмотреть):
  · обращение на «вы» (правило 11.11: публично всё на «ты»);
  · цены в долларах и рублях (цены не пишем — устаревают);
  · сервисы, которые решили убрать (Readom, Grok);
  · горизонтальный скролл на ширине 390 px (с --mobile или в GitHub).
Страницы — файлы index*.html; папки src/, _claude_tmp и служебные пропускаем.
"""
import argparse, html, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKIP_DIRS = {".git", ".github", "src", "src-short", "tools", "node_modules"}

ERR_HEAD = [
    (r"<!doctype html", "нет <!doctype html>"),
    (r"<html[^>]*\blang=\"?ru", "нет lang=\"ru\" в <html>"),
    (r"<meta[^>]*charset", "нет <meta charset>"),
    (r"<meta[^>]*name=\"?viewport", "нет <meta name=\"viewport\">"),
    (r"<meta[^>]*name=\"?robots\"?[^>]*noindex", "нет <meta name=\"robots\" content=\"noindex\"> — страница открыта поисковикам"),
]
NAME_BAD = re.compile(r"per[\s\-]+aspera[\s\-]+ad[\s\-]+astra", re.I)
VY = re.compile(r"(?<![\w-])(вы|вас|вам|вами|ваш|ваша|ваше|ваши|вашего|вашей|вашу|вашим|ваших|вашими|вашем)(?![\w-])", re.I)
MONEY = re.compile(r"(\$\s?\d|\d\s?\$|\bUSD\b|\d[\d\s]*\s?(₽|руб\.?(?!рик))|доллар)", re.I)
BANNED = re.compile(r"\b(Readom|Grok)\b", re.I)


def pages():
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith("_claude")]
        for f in files:
            if re.fullmatch(r"index[\w-]*\.html", f):
                yield os.path.relpath(os.path.join(d, f), ROOT)


def text_of(src):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", src, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return html.unescape(t)


def changed_since(base):
    out = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], cwd=ROOT, capture_output=True, text=True)
    if out.returncode:
        out = subprocess.run(["git", "diff", "--name-only", base], cwd=ROOT, capture_output=True, text=True)
    files = set(out.stdout.split())
    files |= set(subprocess.run(["git", "ls-files", "-mo", "--exclude-standard"], cwd=ROOT,
                                capture_output=True, text=True).stdout.split())
    return files


def gh(kind, path, msg):
    """Сообщение в консоль и аннотация в GitHub Actions."""
    print(f"{'ОШИБКА' if kind == 'error' else 'внимание'} · {path} · {msg}")
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::{kind} file={path}::{msg}")


def snippet(text, m):
    s = text[max(0, m.start() - 30): m.end() + 30]
    return "«…" + re.sub(r"\s+", " ", s).strip() + "…»"


def mobile_check(paths):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Мобильная проверка пропущена: нет playwright (pip install playwright && playwright install chromium).")
        return []
    bad = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 390, "height": 844})
        for path in paths:
            pg.goto("file://" + os.path.join(ROOT, path), wait_until="load")
            pg.wait_for_timeout(500)
            sw = pg.evaluate("Math.max(document.documentElement.scrollWidth, document.body ? document.body.scrollWidth : 0)")
            if sw > 391:
                bad.append(path)
                gh("warning", path, f"горизонтальный скролл на ширине 390 px: ширина страницы {sw} px")
        b.close()
    return bad


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--changed", metavar="BASE", help="ветка или коммит, с которым сравнивать (например origin/main)")
    a.add_argument("--mobile", action="store_true", help="проверить ширину 390 px у изменённых страниц")
    o = a.parse_args()
    all_pages = sorted(pages())
    changed = changed_since(o.changed) if o.changed else set()
    errors = warnings = 0
    for path in all_pages:
        src = open(os.path.join(ROOT, path), encoding="utf-8", errors="ignore").read()
        head = src[:20000].lower()
        for rx, msg in ERR_HEAD:
            if not re.search(rx, head, re.I):
                gh("error", path, msg); errors += 1
        txt = text_of(src)
        for m in NAME_BAD.finditer(txt):
            gh("error", path, f"название школы — пишем PERASPERADASTRA: {snippet(txt, m)}"); errors += 1
        if path not in changed:
            continue
        for rx, what in [(VY, "обращение на «вы» — публично пишем на «ты»"),
                         (MONEY, "цена или валюта — цены не пишем, они устаревают"),
                         (BANNED, "сервис, который решили убрать")]:
            hits = list(rx.finditer(txt))
            if hits:
                gh("warning", path, f"{what}: {len(hits)} шт., например {snippet(txt, hits[0])}"); warnings += len(hits)
    if o.mobile and changed:
        warnings += len(mobile_check([p for p in all_pages if p in changed]))
    print(f"\nПроверено страниц: {len(all_pages)} · изменённых: {len([p for p in all_pages if p in changed])} · "
          f"ошибок: {errors} · предупреждений: {warnings}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
