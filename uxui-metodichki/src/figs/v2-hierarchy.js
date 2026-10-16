/**
 * Hierarchy: a phone lying flat, its screen built of blocks standing at three
 * heights: a tall headline, a card of medium height with a picture, a low list
 * of three rows, and the one main button. The block under the pointer rises
 * and the others sink a little, staggered outwards from it. The slider is the
 * stagger, in ms.
 */
const {
  Cam, fit, open, poly, prism, proj, ringAt, rings, rrect, unproj, facing,
  tdone, tset, tval, tween, mk, pointer, put, register, disposer, solid,
} = HL;

const W = 74, L = 152, R = 13, ZB = 8, IN = 4.5, LIFT = 12, SINK = 0.55;
// [x0, y0, x1, y1, corner, height, block]: headline, card, three list rows, button
const PARTS = [
  [10, 18, 64, 40, 3, 20, 0], [10, 46, 64, 92, 4, 11, 1],
  [10, 98, 64, 107, 2.5, 4, 2], [10, 110, 64, 119, 2.5, 4, 2], [10, 122, 64, 131, 2.5, 4, 2],
  [19, 134, 55, 146, 6, 8, 3],
];
const NAMES = ["первое", "второе", "третье", "действие"];

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let stag = value;
  const C = Cam(45, 0.5, 1.84);
  fit(C, [[0, 0, 0], [W, L, 0], [W, 0, 0], [0, L, 0], [10, 18, ZB + 20 + LIFT]], 200, 168);
  const P = proj(C), front = facing(C);
  const flat = (x0, y0, x1, y1, r, z) => poly(ringAt(P, rrect(x0, y0, x1, y1, r, 5), z));

  const g = mk("g", {}, svg);
  const [pr, pi] = rings(0, 0, W, L, R, 1.6);
  put(solid(g), prism(P, front, pr, pi, 0, ZB));
  mk("path", { d: flat(IN, IN, W - IN, L - IN, R - IN, ZB), class: "nf" }, g);
  mk("path", { d: flat(W / 2 - 10, 7.5, W / 2 + 10, 12.5, 2.5, ZB), class: "nf" }, g);
  mk("path", { d: open([P(W, 34, ZB * 0.5), P(W, 52, ZB * 0.5)]), class: "nf lo" }, g);

  const parts = PARTS.map(([x0, y0, x1, y1, r, h, b]) => {
    const [ring, inner] = rings(x0, y0, x1, y1, r, 1.3);
    const el = solid(g), top = mk("path", { class: "nf lo" }, g);
    return { x0, y0, x1, y1, h, b, ring, inner, el, top, z: tween(h), drawn: NaN };
  });

  /** What each part carries on its top: lines a headline has, a card's picture, a row's avatar, a button's label bar. */
  function marks(p, z) {
    const { x0, y0, x1, y1 } = p;
    if (p.b === 0) return flat(x0 + 5, y0 + 5, x1 - 14, y0 + 11, 1.5, z) + flat(x0 + 5, y0 + 14, x1 - 26, y0 + 17, 1, z);
    if (p.b === 1) return flat(x0 + 4, y0 + 4, x1 - 4, y1 - 12, 2.5, z) +
      open([P(x0 + 8, y1 - 16, z), P(x0 + 20, y0 + 16, z), P(x0 + 30, y1 - 22, z), P(x0 + 36, y0 + 18, z), P(x1 - 8, y1 - 16, z)]) +
      flat(x1 - 15, y0 + 8, x1 - 9, y0 + 14, 3, z) + flat(x0 + 4, y1 - 8, x1 - 18, y1 - 5, 1, z);
    if (p.b === 2) return flat(x0 + 2.5, y0 + 2, x0 + 7.5, y1 - 2, 2.5, z) + flat(x0 + 11, y0 + 3.5, x1 - 12, y1 - 3.5, 1, z);
    return flat(x0 + 9, y0 + 4, x1 - 9, y1 - 4, 2, z);
  }

  function draw(p, h) {
    if (h === p.drawn) return;
    p.drawn = h;
    put(p.el, prism(P, front, p.ring, p.inner, ZB, ZB + h));
    p.top.setAttribute("d", marks(p, ZB + h));
  }

  const B = register(stage, (_dt, now) => {
    let m = false;
    for (const p of parts) { draw(p, tval(p.z, now)); if (!tdone(p.z, now)) m = true; }
    return m;
  });
  bag.add(B.unregister);

  /** Each part's REST top: unproj onto it, keep the part that puts the pointer nearest its middle. */
  function hit([sx, sy]) {
    let best = -1, bd = 1.25;
    for (const p of parts) {
      const [x, y] = unproj(C, sx, sy, ZB + p.h);
      const d = Math.max(Math.abs(x - (p.x0 + p.x1) / 2) / ((p.x1 - p.x0) / 2 + 4), Math.abs(y - (p.y0 + p.y1) / 2) / ((p.y1 - p.y0) / 2 + 2));
      if (d < bd) { bd = d; best = p.b; }
    }
    return best;
  }

  let act = -2;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = a >= 0 ? a : Math.max(act, 0);
    act = a;
    for (const p of parts) {
      const h = a < 0 ? p.h : p.b === a ? p.h + LIFT : p.h * SINK;
      tset(p.z, h, now, Math.abs(p.b - from) * stag);
      p.el.sil.classList.toggle("hi", p.b === (a < 0 ? 0 : a));
    }
    read.textContent = a < 0 ? "rest" : NAMES[a];
    B.wake();
  }
  setActive(-1);

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());

  return { set: (v) => { stag = v; }, destroy: bag.dispose };
}

hairline({
  name: "v2-hierarchy",
  means: "Экран из блоков разной высоты: блок под курсором поднимается, остальные чуть оседают, и видно, что читается первым.",
  rules: [1, 2, 5, 9],
  range: [0, 45, 90],
  tour: [[261, 116], [209, 156], [117, 208], null],
  mount,
});
