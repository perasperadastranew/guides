/**
 * Type case: a printer's shallow tray cut into five compartments, big ones at
 * the back left, small ones at the front right, each holding a sort sized to
 * it: a type-high body, a raised face on top and a nick across its front. The
 * sort under the pointer rises out of its compartment; the ones near it lift a
 * little, staggered by distance. The slider is the stagger, in ms.
 */
const {
  Cam, facing, fit, open, poly, prism, proj, ringAt, rings, rrect, run, unproj,
  tdone, tset, tval, tween, mk, pointer, put, register, disposer, solid,
} = HL;

const TX = 132, TY = 98, TOP = 12, FLOOR = 3, TH = 16, FACE = 2.2, LIFT = 24, NEAR = 4;
// compartments [x0, y0, x1, y1], and the sort's footprint inside each [w, d]
const CELLS = [
  [[5, 5, 74, 49], [46, 30]], [[78, 5, 127, 49], [32, 26]], [[5, 53, 56, 93], [30, 24]],
  [[60, 53, 96, 93], [21, 18]], [[100, 53, 127, 93], [14, 13]],
];
const NAMES = ["заголовок", "подзаголовок", "текст", "подпись", "кнопка"];
const REST = [5, 0, 1.5, 0, 2.5];
const LR = (pts) => (pts[0][0] <= pts[pts.length - 1][0] ? pts : pts.slice().reverse());

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let stag = value;
  const C = Cam(45, 0.5, 1.72);
  fit(C, [[0, 0, 0], [TX, TY, 0], [TX, 0, 0], [0, TY, 0], [16, 12, FLOOR + TH + FACE + LIFT]], 200, 170);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  const [outer, oin] = rings(0, 0, TX, TY, 6, 1.6);
  put(solid(g), prism(P, front, outer, oin, 0, TOP));

  // back to front by x + y: each compartment's hole, its sort, then the slab's lip that hides the sort's foot
  const order = CELLS.map((c, i) => i).sort((a, b) => CELLS[a][0][0] + CELLS[a][0][1] - (CELLS[b][0][0] + CELLS[b][0][1]));
  const sorts = [];
  for (const i of order) {
    const [[x0, y0, x1, y1], [w, d]] = CELLS[i];
    const hole = rrect(x0, y0, x1, y1, 2.5, 4);
    mk("path", { d: poly(ringAt(P, hole, TOP)), class: "nf" }, g);
    mk("path", { d: open(ringAt(P, run(hole, (q) => !front(q)), FLOOR)), class: "nf lo" }, g);
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    const [br, bi] = rings(cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2, 2, 1.1);
    const [fr, fi] = rings(cx - w * 0.32, cy - d * 0.3, cx + w * 0.32, cy + d * 0.3, 1.6, 0.8);
    const body = solid(g), face = solid(g), nick = mk("path", { class: "nf lo" }, g);
    const nearTop = LR(ringAt(P, run(hole, front), TOP)), drop = P(0, 0, TOP)[1] - P(0, 0, FLOOR)[1];
    mk("path", { d: poly([...nearTop, ...nearTop.slice().reverse().map(([sx, sy]) => [sx, sy - drop])]), class: "fo" }, g);
    mk("path", { d: open(nearTop), class: "nf" }, g);
    sorts.push({ i, cx, cy, w, d, br, bi, fr, fi, body, face, nick, z: tween(REST[i]), drawn: NaN });
  }
  sorts.sort((a, b) => a.i - b.i);

  // the slab's near faces, stroked again over the lips
  const oT = LR(ringAt(P, run(outer, front), TOP)), oB = LR(ringAt(P, run(outer, front), 0));
  mk("path", { d: open([oT[0], ...oB, oT[oT.length - 1]]), class: "nf sil" }, g);
  mk("path", { d: open(ringAt(P, run(oin, front), TOP)), class: "nf lo" }, g);

  function draw(s, z) {
    if (z === s.drawn) return;
    s.drawn = z;
    const z0 = FLOOR + z, z1 = z0 + TH;
    put(s.body, prism(P, front, s.br, s.bi, z0, z1));
    put(s.face, prism(P, front, s.fr, s.fi, z1, z1 + FACE));
    const yn = s.cy + s.d / 2, zn = z0 + TH * 0.42;
    s.nick.setAttribute("d", open([P(s.cx - s.w / 2 + 2, yn, zn), P(s.cx + s.w / 2 - 2, yn, zn)]) + open([P(s.cx + s.w / 2, s.cy - s.d / 2 + 2, zn), P(s.cx + s.w / 2, yn - 2, zn)]));
  }

  const B = register(stage, (_dt, now) => {
    let m = false;
    for (const s of sorts) { draw(s, tval(s.z, now)); if (!tdone(s.z, now)) m = true; }
    return m;
  });
  bag.add(B.unregister);

  /** The compartment under the pointer, on the tray's top plane, which never moves. */
  function hit([sx, sy]) {
    const [x, y] = unproj(C, sx, sy, TOP);
    return CELLS.findIndex(([[x0, y0, x1, y1]]) => x > x0 - 2 && x < x1 + 2 && y > y0 - 2 && y < y1 + 2);
  }

  let act = -2;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = sorts[a >= 0 ? a : Math.max(act, 0)];
    act = a;
    for (const s of sorts) {
      const dist = Math.hypot(s.cx - from.cx, s.cy - from.cy);
      tset(s.z, a < 0 ? REST[s.i] : s.i === a ? LIFT : dist < 62 ? NEAR : 0, now, (dist / 30) * stag);
      const on = s.i === (a < 0 ? 0 : a);
      s.body.sil.classList.toggle("hi", on); s.face.sil.classList.toggle("hi", on);
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
  name: "v4-typecase",
  means: "Наборная касса: литера под курсором поднимается из своей ячейки, и видно, какой стиль крупнее, а какой мельче.",
  rules: [1, 2, 6, 9],
  range: [0, 40, 80],
  tour: [[195, 148], [127, 170], [228, 220], null],
  mount,
});
