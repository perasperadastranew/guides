/**
 * Elevation: an Android phone lying flat, and on its screen the surfaces of a
 * Material layout standing at their own elevations: the top app bar, two
 * cards, the round FAB in the corner (highest, bright at rest) and the bottom
 * navigation. The surface under the pointer rises higher; the others settle a
 * little, staggered outwards from it. The slider is the stagger, in ms.
 */
const {
  Cam, circ, facing, fit, poly, prism, proj, rings, ringAt, rrect, seg, unproj,
  tween, tset, tval, tdone, disposer, mk, pointer, put, register, solid,
} = HL;

const L = 100, W = 50, BT = 5, RISE = 9, SINK = 0.5;
const shiftRing = (ring, cx, cy) => ring.map((q) => ({ ...q, u: q.u + cx, v: q.v + cy }));

// Surfaces in paint order: name, footprint [x0, y0, x1, y1] (or a round one), rest elevation, marks on the top.
const SURF = [
  { name: "панель", f: [9, 4, 21, 46], h: 6, marks: [[13, 20, 17, 42, 1.6], [13, 7, 17, 11, 2]] },
  { name: "карточка", f: [25, 5, 47, 45], h: 2.5, marks: [[28, 22, 44, 42, 2.4], [29, 8, 32, 19, 1.3], [35, 8, 38, 15, 1.3]] },
  { name: "карточка", f: [51, 5, 73, 33], h: 3.5, marks: [[54, 17, 70, 30, 2.4], [55, 8, 58, 14, 1.3], [61, 8, 64, 12, 1.3]] },
  { name: "FAB", c: [65, 41, 5.6], h: 10, marks: [] },
  { name: "навигация", f: [80, 4, 93, 46], h: 5, marks: [[84.5, 9, 88.5, 13, 2], [84.5, 23, 88.5, 27, 2], [84.5, 37, 88.5, 41, 2]] },
];
const FAB = 3;

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let stag = value;

  const C = Cam(45, 0.5, 2.75);
  fit(C, [[0, 0, 0], [L, W, 0], [L, 0, 0], [0, W, 0], [65, 41, BT + 10 + RISE], [9, 4, BT + 6 + RISE], [9, 46, BT + 6 + RISE]], 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  // The phone: a slab, its screen edge, a punch-hole camera, and the side keys as short ridges.
  const [br, bi] = rings(0, 0, L, W, 7, 1.5);
  put(solid(g), prism(P, front, br, bi, 0, BT));
  mk("path", { class: "nf lo", d: poly(ringAt(P, rrect(2.4, 2.4, L - 2.4, W - 2.4, 5, 5), BT)) }, g);
  mk("path", { class: "nf", d: poly(ringAt(P, shiftRing(circ(1.5, 12), 5.2, W / 2), BT)) }, g);
  mk("path", { class: "nf", d: seg(P(24, W, 1.6), P(36, W, 1.6)) + seg(P(40, W, 1.6), P(46, W, 1.6)) }, g);

  const items = SURF.map((s) => {
    let ring, inner, cx, cy, rx, ry;
    if (s.c) {
      [cx, cy] = s.c; rx = ry = s.c[2];
      ring = shiftRing(circ(s.c[2], 28), cx, cy); inner = shiftRing(circ(s.c[2] - 0.9, 28), cx, cy);
    } else {
      const [x0, y0, x1, y1] = s.f;
      [ring, inner] = rings(x0, y0, x1, y1, 2.6, 0.9);
      cx = (x0 + x1) / 2; cy = (y0 + y1) / 2; rx = (x1 - x0) / 2; ry = (y1 - y0) / 2;
    }
    const el = solid(g), mEl = mk("path", { class: "nf lo" }, el.g);
    const marks = s.marks.map(([a, b, c, d, r]) => rrect(a, b, c, d, r, 4));
    return { ...s, ring, inner, cx, cy, rx, ry, el, mEl, marks, tw: tween(s.h), drawn: NaN };
  });

  function draw(it, h) {
    if (h === it.drawn) return;
    it.drawn = h;
    put(it.el, prism(P, front, it.ring, it.inner, BT, BT + h));
    it.mEl.setAttribute("d", it.marks.map((m) => poly(ringAt(P, m, BT + h))).join(""));
  }

  const B = register(stage, (_dt, now) => {
    let moving = false;
    items.forEach((it) => { draw(it, tval(it.tw, now)); if (!tdone(it.tw, now)) moving = true; });
    return moving;
  });
  bag.add(B.unregister);

  // Hit test on each surface's REST top: unproject onto its own rest height, take the nearest middle.
  function hit([sx, sy]) {
    let best = -1, bd = 1.25;
    items.forEach((it, i) => {
      const w = unproj(C, sx, sy, BT + it.h);
      const d = it.c
        ? Math.hypot(w[0] - it.cx, w[1] - it.cy) / (it.rx + 2)
        : Math.max(Math.abs(w[0] - it.cx) / (it.rx + 2), Math.abs(w[1] - it.cy) / (it.ry + 3));
      if (d < bd) { bd = d; best = i; }
    });
    return best;
  }

  let act = -2;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = a >= 0 ? a : act >= 0 ? act : FAB;
    act = a;
    items.forEach((it, i) => {
      const h = a < 0 ? it.h : i === a ? it.h + RISE : Math.max(1.2, it.h * SINK);
      tset(it.tw, h, now, Math.abs(i - from) * stag);
      it.el.sil.classList.toggle("hi", i === (a < 0 ? FAB : a));
    });
    read.textContent = a < 0 ? "rest" : SURF[a].name;
    B.wake();
  }
  setActive(-1);

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());

  return {
    set: (v) => { stag = v; },
    destroy: bag.dispose,
  };
}

hairline({
  name: "g2-elevation",
  means: "Поверхности Material на экране Android стоят на разной высоте: та, что под курсором, поднимается выше остальных.",
  rules: [1, 2, 4, 5],
  range: [0, 40, 80],
  tour: [[130, 133], [173, 152], [197, 182], [284, 201], null],
  mount,
});
