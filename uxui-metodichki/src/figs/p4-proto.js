/**
 * Proto: three grey wireframe phones lying in a loose row, joined by a dashed
 * tap path that arcs from a tap dot on one screen to the next. The phone under
 * the pointer lifts and its tap dot goes bright; the others follow a little,
 * staggered outwards. At rest the first tap dot is bright: where the walk
 * starts. The slider is the stagger, in ms.
 */
const {
  Cam, fit, open, poly, prism, proj, facing, rings, ringAt, rrect, seg, unproj,
  tween, tset, tval, tdone, disposer, flatDot, mk, place, pointer, put, register, solid,
} = HL;

const PW = 36, PH = 64, GAP = 24, T = 4, LIFT = 22, FOLLOW = [1, 0.3, 0.1], ARC = 16;

// Each phone: where it lies, its rest height, its wireframe blocks [u0, v0, u1, v1, r], and its tap dot [u, v].
const PHONES = [
  { x: 0, y: 0, z: 0, blocks: [[6, 10, 30, 30, 3], [6, 34, 24, 37, 1.5], [6, 40, 28, 43, 1.5], [8, 49, 28, 55, 3]], tap: [18, 52] },
  { x: PW + GAP, y: 16, z: 6, blocks: [[6, 10, 30, 16, 2], [6, 20, 12, 26, 3], [14, 21.5, 30, 24.5, 1.5], [6, 30, 12, 36, 3], [14, 31.5, 30, 34.5, 1.5], [6, 40, 12, 46, 3], [14, 41.5, 30, 44.5, 1.5]], tap: [22, 33] },
  { x: 2 * (PW + GAP), y: 4, z: 2, blocks: [[6, 10, 30, 36, 3], [6, 40, 22, 43, 1.5], [6, 46, 30, 48.5, 1.2], [6, 51, 30, 53.5, 1.2]], tap: [12, 23] },
];
const N = PHONES.length;

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let stag = value;

  const C = Cam(45, 0.5, 1.9);
  const ext = [];
  PHONES.forEach((p) => { for (const [u, v] of [[0, 0], [PW, 0], [0, PH], [PW, PH]]) ext.push([p.x + u, p.y + v, p.z], [p.x + u, p.y + v, p.z + T + LIFT + ARC]); });
  fit(C, ext, 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  const items = PHONES.map((p, i) => {
    const [ring, inner] = rings(p.x, p.y, p.x + PW, p.y + PH, 6, 1.2);
    const face = rrect(p.x + 3, p.y + 6, p.x + PW - 3, p.y + PH - 6, 3, 4);
    const blocks = p.blocks.map(([u0, v0, u1, v1, r]) => rrect(p.x + u0, p.y + v0, p.x + u1, p.y + v1, r, 4));
    // the path from the phone before this one arcs in behind this phone
    const path = i > 0 ? mk("path", { class: "nf dash" }, g) : null;
    const el = solid(g);
    const fEl = mk("path", { class: "nf lo" }, el.g), dEl = mk("path", { class: "nf" }, el.g), bEl = mk("path", { class: "nf lo" }, el.g);
    const dot = flatDot(el.g, C, 1.9, i === 0 ? "dot" : "dot m");
    return { ...p, ring, inner, face, blocks, path, el, fEl, dEl, bEl, dot, tw: tween(0), drawn: NaN };
  });

  const top = (it) => it.z + it.drawn + T;
  function drawPhone(it) {
    const z = it.z + it.drawn, t = z + T, { x, y } = it;
    put(it.el, prism(P, front, it.ring, it.inner, z, t));
    it.fEl.setAttribute("d", poly(ringAt(P, it.face, t)));
    it.dEl.setAttribute("d", seg(P(x + PW / 2 - 5, y + 3, t), P(x + PW / 2 + 5, y + 3, t)) + seg(P(x + PW / 2 - 6, y + PH - 3, t), P(x + PW / 2 + 6, y + PH - 3, t)));
    it.bEl.setAttribute("d", it.blocks.map((m) => poly(ringAt(P, m, t))).join(""));
    place(it.dot, P(x + it.tap[0], y + it.tap[1], t));
  }
  /** The tap path: from the tap dot on phone a, arcing up, to the middle of phone b's far short edge. */
  function drawPath(a, b) {
    const A = items[a], Bp = items[b];
    const p0 = [A.x + A.tap[0], A.y + A.tap[1], top(A)], p1 = [Bp.x, Bp.y + PH / 2, top(Bp) - T / 2];
    const pts = [];
    for (let k = 0; k <= 16; k++) {
      const s = k / 16, lift = ARC * 4 * s * (1 - s);
      pts.push(P(p0[0] + (p1[0] - p0[0]) * s, p0[1] + (p1[1] - p0[1]) * s, p0[2] + (p1[2] - p0[2]) * s + lift));
    }
    Bp.path.setAttribute("d", open(pts));
  }

  const B = register(stage, (_dt, now) => {
    let moving = false, changed = false;
    items.forEach((it) => {
      const v = tval(it.tw, now);
      if (!tdone(it.tw, now)) moving = true;
      if (v !== it.drawn) { it.drawn = v; drawPhone(it); changed = true; }
    });
    if (changed) for (let i = 1; i < N; i++) drawPath(i - 1, i);
    return moving;
  });
  bag.add(B.unregister);

  // Hit test on each phone's REST top: unproject onto its own height, take the nearest middle.
  function hit([sx, sy]) {
    let best = -1, bd = 1.2;
    PHONES.forEach((p, i) => {
      const w = unproj(C, sx, sy, p.z + T);
      const d = Math.max(Math.abs(w[0] - p.x - PW / 2) / (PW / 2 + GAP / 2), Math.abs(w[1] - p.y - PH / 2) / (PH / 2 + 6));
      if (d < bd) { bd = d; best = i; }
    });
    return best;
  }

  let act = -2;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = a >= 0 ? a : act >= 0 ? act : 0;
    act = a;
    items.forEach((it, i) => {
      tset(it.tw, a < 0 ? 0 : LIFT * FOLLOW[Math.abs(i - a)], now, Math.abs(i - from) * stag);
      it.el.sil.classList.toggle("hi", i === a);
      it.dot.setAttribute("class", "dot" + ((a < 0 ? i === 0 : i === a) ? "" : " m"));
    });
    read.textContent = a < 0 ? "rest" : "экран " + (a + 1);
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
  name: "p4-proto",
  means: "Три серых экрана связаны пунктиром нажатий: экран под курсором поднимается, и его точка нажатия загорается.",
  rules: [1, 2, 4, 6],
  range: [0, 50, 100],
  tour: [[121, 156], [181, 195], [277, 236], null],
  mount,
});
