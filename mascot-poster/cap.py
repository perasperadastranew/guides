# Покадровый рендер: python3 cap.py starter.html out/ 24 [fps] [jobs]
# Потом: python3 sfx.py out/events.json 24  и  ffmpeg -framerate 30 -i out/%05d.jpg -i sfx.wav -c:v libx264 -crf 19 -pix_fmt yuv420p reel.mp4
import sys, asyncio, json, os, pathlib
from playwright.async_api import async_playwright
page, out, dur = sys.argv[1], sys.argv[2], float(sys.argv[3])
fps = int(sys.argv[4]) if len(sys.argv) > 4 else 30
jobs = int(sys.argv[5]) if len(sys.argv) > 5 else 4
url = pathlib.Path(page).resolve().as_uri() + '?render'
os.makedirs(out, exist_ok=True)
N = int(dur * fps)
async def worker(p, a, b):
    br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1080, 'height': 1920})
    pg.on('pageerror', lambda e: print('ERR', e))
    await pg.goto(url); await pg.wait_for_function('window.FIT===1')
    await pg.evaluate(f'window.renderAt({a/fps})')  # прогон симуляции до начала куска
    for f in range(a, b):
        await pg.evaluate(f'window.renderAt({f/fps})')
        await pg.screenshot(path=f'{out}/{f:05d}.jpg', type='jpeg', quality=92)
    if b == N:
        await pg.evaluate(f'window.renderAt({dur})')
        json.dump(await pg.evaluate('MASCOT.events()'), open(f'{out}/events.json', 'w'))
    await br.close()
async def main():
    async with async_playwright() as p:
        C = -(-N // jobs)
        await asyncio.gather(*[worker(p, i*C, min(N, (i+1)*C)) for i in range(jobs) if i*C < N])
asyncio.run(main())
