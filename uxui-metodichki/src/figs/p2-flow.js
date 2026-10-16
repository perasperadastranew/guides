/**
 * Flow: five phone plates in a row, climbing a little toward the goal, joined
 * by a dashed route; at step 3 a branch drops to a sixth plate lower and to
 * the side, the error screen. The plate under the pointer lifts and takes the
 * bright edge; its neighbours follow less, staggered outwards from it. The
 * slider is the stagger, in ms.
 */
const {
  Cam, fit, open, poly, prism, proj, facing, rings, ringAt, rrect, seg, unproj,
  tween, tset, tval, tdone, disposer, mk, pointer, put, register, solid,
} = HL;

const PW = 26, PH = 46, GAP = 16, T = 3, LIFT = 24, FOLLOW = [1, 0.34, 0.12, 0, 0, 0];

// Plates: five steps along x, rising toward the goal, and the error screen
// below step 3, offset toward the viewer. Each has its own screen content.
const PLATES = [
  { x: 0, y: 0, z: 2, name: "шаг 1", marks: [[9, 13, 17, 21, 4], [6, 30, 20, 33, 1.5]] },
  { x: PW + GAP, y: 0, z: 6, name: "шаг 2", marks: [[6, 10, 20, 13, 1.5], [6, 17, 20, 20, 1.5], [6, 24, 20, 27, 1.5], [6, 31, 15, 34, 1.5]] },
  { x: 2 * (PW + GAP), y: 0, z: 11, name: "шаг 3", marks: [[6, 10, 20, 16, 2], [6, 19, 20, 25, 2], [8, 32, 18, 37, 2.5]] },
  { x: 3 * (PW + GAP), y: 0, z: 16, name: "шаг 4", marks: [[6, 10, 20, 24, 2.5], [6, 27, 17, 29.5, 1.2], [8, 33, 18, 37, 2.5]] },
  { x: 4 * (PW + GAP), y: 0, z: 22, name: "шаг 5", marks: [[8, 11, 18, 21, 5], [7, 29, 19, 32, 1.5], [9, 35, 17, 37.5, 1.2]] },
  { x: 2 * (PW + GAP) + 18, y: PH + 22, z: 0, name: "ошибка", marks: [[6, 11, 20, 19, 2], [6, 23, 20, 25.5, 1.2], [8, 32, 18, 37, 2.5]] },
];
const ERR = 5, BRANCH = 2, GOAL = 4;
// Distance in steps between two plates; the error plate hangs one step off step 3.
const dist = (a, i) => {
  const pos = (k) => (k === ERR ? BRANCH : k), off = (a === ERR) !== (i === ERR) ? 1 : 0;
  return Math.abs(pos(a) - pos(i)) + off;
};

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let stag = value;

  const C = Cam(45, 0.5, 1.72);
  const ext = [];
  PLATES.forEach((p) => { for (const [u, v] of [[0, 0], [PW, 0], [0, PH], [PW, PH]]) ext.push([p.x + u, p.y + v, p.z], [p.x + u, p.y + v, p.z + T + LIFT]); });
  fit(C, ext, 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  // Paint back to front: by the plate's centre x + y. The dashed route between
  // two plates sits in the gap, painted after the farther plate and before the nearer.
  const order = PLATES.map((p, i) => i).sort((a, b) => (PLATES[a].x + PLATES[a].y) - (PLATES[b].x + PLATES[b].y));
  const routes = [[0, 1], [1, 2], [2, 3], [3, 4], [BRANCH, ERR]].map(([a, b]) => ({ a, b, el: null }));

  const items = PLATES.map((p) => {
    const [ring, inner] = rings(p.x, p.y, p.x + PW, p.y + PH, 5, 1.1);
    const scr = rrect(p.x + 2.6, p.y + 5, p.x + PW - 2.6, p.y + PH - 4.5, 2.6, 4);
    const marks = p.marks.map(([u0, v0, u1, v1, r]) => rrect(p.x + u0, p.y + v0, p.x + u1, p.y + v1, r, 4));
    return { ...p, ring, inner, scr, marks, tw: tween(0), drawn: NaN };
  });

  for (const i of order) {
    for (const r of routes) if (r.b === i) r.el = mk("path", { class: "nf dash" }, g);
    const it = items[i];
    it.el = solid(g);
    it.scrEl = mk("path", { class: "nf lo" }, it.el.g);
    it.slit = mk("path", { class: "nf" }, it.el.g);
    it.mk = mk("path", { class: "nf lo" }, it.el.g);
  }

  /** The point where a route meets plate k: the middle of the edge facing the other plate. */
  function edge(k, other, z) {
    const p = PLATES[k], q = PLATES[other];
    if (q.y > p.y + PH) return P(p.x + PW / 2, p.y + PH, z);
    if (p.y > q.y + PH) return P(p.x + PW / 2, p.y, z);
    return q.x > p.x ? P(p.x + PW, p.y + PH / 2, z) : P(p.x, p.y + PH / 2, z);
  }

  function draw(it, lift) {
    if (lift === it.drawn) return false;
    it.drawn = lift;
    const z = it.z + lift, top = z + T;
    put(it.el, prism(P, front, it.ring, it.inner, z, top));
    it.scrEl.setAttribute("d", poly(ringAt(P, it.scr, top)));
    it.slit.setAttribute("d", seg(P(it.x + PW / 2 - 4, it.y + 2.6, top), P(it.x + PW / 2 + 4, it.y + 2.6, top)));
    it.mk.setAttribute("d", it.marks.map((m) => poly(ringAt(P, m, top))).join(""));
    return true;
  }

  const B = register(stage, (_dt, now) => {
    let moving = false, changed = false;
    items.forEach((it) => { if (draw(it, tval(it.tw, now))) changed = true; if (!tdone(it.tw, now)) moving = true; });
    if (changed) routes.forEach((r) => {
      const A = items[r.a], Bp = items[r.b];
      r.el.setAttribute("d", open([edge(r.a, r.b, A.drawn + A.z + T / 2), edge(r.b, r.a, Bp.drawn + Bp.z + T / 2)]));
    });
    return moving;
  });
  bag.add(B.unregister);

  // Hit test on each plate's REST top: unproject onto its own height and take
  // the plate that puts the pointer nearest its middle.
  function hit([sx, sy]) {
    let best = -1, bd = 1.15;
    PLATES.forEach((p, i) => {
      const w = unproj(C, sx, sy, p.z + T);
      const d = Math.max(Math.abs(w[0] - p.x - PW / 2) / (PW / 2 + GAP / 2), Math.abs(w[1] - p.y - PH / 2) / (PH / 2 + 4));
      if (d < bd) { bd = d; best = i; }
    });
    return best;
  }

  let act = -2;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = a >= 0 ? a : act >= 0 ? act : GOAL;
    act = a;
    items.forEach((it, i) => {
      const lift = a < 0 ? 0 : LIFT * FOLLOW[Math.min(dist(a, i), 5)];
      tset(it.tw, lift, now, dist(from, i) * stag);
      it.el.sil.classList.toggle("hi", a < 0 ? i === GOAL : i === a);
    });
    read.textContent = a < 0 ? "rest" : PLATES[a].name;
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
  name: "p2-flow",
  means: "Пять экранов на пути к цели и ветка к экрану ошибки: экран под курсором поднимается, соседи следом.",
  rules: [1, 2, 5, 6],
  range: [0, 45, 90],
  tour: [[97, 130], [200, 166], [139, 236], [300, 203], null],
  mount,
});
