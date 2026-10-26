# Дизеринг кадров сцены с птицами: Bayer 4×4 + контуры → палитра (прозрачный / светлый / красный), спрайт 12×9 кадров 480×270
import sys, glob, numpy as np
from PIL import Image, ImageFilter
src, out = sys.argv[1], sys.argv[2]  # папка с кадрами, префикс (a_ или b_)
W, H, COLS = 480, 270, 12
B4 = (np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]) + .5) / 16
fs = sorted(glob.glob('%s/%s*.png' % (src, out)))
rows = (len(fs) + COLS - 1) // COLS
sheet = np.zeros((rows * H, COLS * W), np.uint8)
thr = np.tile(B4, (H // 4 + 1, W // 4 + 1))[:H, :W]
for k, f in enumerate(fs):
    im = Image.open(f).convert('RGBA').resize((W, H), Image.LANCZOS)
    a = np.asarray(im).astype(float) / 255
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    lum = .3 * r + .59 * g + .11 * b
    red = (al > .5) & (r > .45) & (r - g > .25)
    obj = (al > .9) & ~red
    shadow = (al > .04) & (al <= .9) & (lum < .2)
    # контуры по альфе и яркости
    L = Image.fromarray((np.clip(lum * al, 0, 1) * 255).astype(np.uint8))
    A = Image.fromarray(((al > .9) * 255).astype(np.uint8))
    e1 = np.asarray(L.filter(ImageFilter.FIND_EDGES)).astype(float) / 255
    e2 = np.asarray(A.filter(ImageFilter.FIND_EDGES)).astype(float) / 255
    edge = ((e1 > .18) | (e2 > .5)) & (al > .5)
    o = np.zeros((H, W), np.uint8)
    dens = np.where(lum < .2, 1.0, .18 + .55 * lum)  # тёмные детали — сплошные, светлые грани — гуще
    o[obj & (thr < dens)] = 1
    o[shadow & (thr < al * .45)] = 1
    rd = .55 + .45 * (1 - np.clip(lum * 1.4, 0, 1))
    o[red & (thr < np.maximum(rd, .5))] = 2
    o[edge & ~red] = 1
    o[edge & red] = 2
    # глаза/белые части на красных птицах — светлые
    eye = (al > .5) & (r > .85) & (g > .85) & (b > .85) & ~obj
    o[eye] = 1
    # зрачки и брови птиц — дырки в красном
    from PIL import ImageFilter as F
    rdil = np.asarray(Image.fromarray((red * 255).astype(np.uint8)).filter(F.MaxFilter(7))) > 0
    o[(al > .9) & (lum < .12) & rdil] = 0
    # линия земли
    GY = int(sys.argv[3]) if len(sys.argv) > 3 else 205
    row = o[GY]; row[(row == 0) & (np.arange(W) % 3 == 0)] = 1
    rr, cc = divmod(k, COLS)
    sheet[rr * H:(rr + 1) * H, cc * W:(cc + 1) * W] = o
img = Image.fromarray(sheet, 'P')
img.putpalette([0, 0, 0, 242, 242, 240, 240, 48, 59] + [0] * 759)
img.info['transparency'] = 0
img.save(out.rstrip('_') + '.png', optimize=True, transparency=0)
print(len(fs), img.size)
