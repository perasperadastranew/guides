/**
 * Moodboard: a framed cork board leaning on an A-frame easel, resting on its
 * ledge, with six pinned tiles of different sizes: two photos, a swatch strip,
 * a type sample, a shape and a texture. The tile under the pointer comes off
 * the board toward the viewer; the tiles near it follow a little, staggered by
 * distance. The slider is the stagger, in ms.
 */
const {
  Cam, clamp, facing, fit, hull, open, poly, prism, proj, rad, rings, rrect,
  tdone, tset, tval, tween, mk, place, pointer, put, register, disposer, solid,
} = HL;

const BW = 124, BH = 88, TH = -9, Z0 = 34, YB = 0, LIFT = 24, NEAR = 5;
const s = Math.sin(rad(TH)), c = Math.cos(rad(TH));
// tiles in board coordinates: [u0, v0, u1, v1, turn in degrees, kind]
const TILES = [
  [10, 40, 54, 78, -3, "photo"], [60, 30, 75, 78, 2, "swatch"], [81, 52, 114, 77, 3, "type"],
  [10, 9, 34, 33, 4, "dots"], [40, 8, 74, 25, -2, "photo2"], [81, 11, 108, 45, -4, "shape"],
];
const pts = (r) => r.map((q) => [q.u, q.v]);
const ring = (cx, cy, R, n = 14) => Array.from({ length: n }, (_, k) => [cx + R * Math.cos((k / n) * 2 * Math.PI), cy + R * Math.sin((k / n) * 2 * Math.PI)]);

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let stag = value;
  const SC = 1.6, C = Cam(45, 0.5, SC);
  /** A point on the board: u across, v up its face, d out of it toward the viewer. */
  const wb = (u, v, d = 0) => [u, YB + v * s + d * c, Z0 + v * c - d * s];
  const GND = -Z0 / c, TOP = BH + 16;
  fit(C, [wb(-6, GND), wb(BW + 6, GND), wb(60, TOP), wb(0, 0, 10), wb(BW, 0, 10), wb(30, 78, LIFT + 4), wb(60, TOP, -40)], 200, 164);
  const P = proj(C), B3 = (p) => P(p[0], p[1], p[2]);
  const at = (u, v, d) => B3(wb(u, v, d));
  /** A rod between two world points: the hull of two screen discs. */
  const rod = (a, b, r) => {
    const pa = B3(a), pb = B3(b), R = r * SC, out = [];
    for (let k = 0; k < 12; k++) { const t = (k / 12) * 2 * Math.PI; for (const p of [pa, pb]) out.push([p[0] + R * Math.cos(t), p[1] + R * Math.sin(t) * 0.8]); }
    return poly(hull(out));
  };

  const g = mk("g", {}, svg);
  // the easel: a back leg, two front legs meeting at the top, behind the board
  const apex = wb(BW / 2, TOP, -4);
  mk("path", { d: rod(apex, wb(BW / 2, GND, -46), 1.6), class: "sil" }, g);
  mk("path", { d: rod(wb(-4, GND, -4), apex, 2), class: "sil" }, g);
  mk("path", { d: rod(wb(BW + 4, GND, -4), apex, 2), class: "sil" }, g);
  // the board: its back edge, its face, the frame's inner edge
  const outer = pts(rrect(0, 0, BW, BH, 5, 4)), inner = pts(rrect(6, 6, BW - 6, BH - 6, 2, 4));
  mk("path", { d: poly(outer.map(([u, v]) => at(u, v, -3))), class: "lo" }, g);
  mk("path", { d: poly(outer.map(([u, v]) => at(u, v, 0))), class: "sil" }, g);
  mk("path", { d: poly(inner.map(([u, v]) => at(u, v, 0))), class: "nf" }, g);
  // the ledge it rests on
  const [lr, li] = rings(-6, YB - 5, BW + 6, YB + 9, 3, 1.2);
  put(solid(g), prism(P, facing(C), lr, li, Z0 - 5, Z0));

  const tiles = TILES.map(([u0, v0, u1, v1, turn, kind], i) => {
    const cu = (u0 + u1) / 2, cv = (v0 + v1) / 2, cs = Math.cos(rad(turn)), sn = Math.sin(rad(turn));
    const tf = (u, v) => [cu + (u - cu) * cs - (v - cv) * sn, cv + (u - cu) * sn + (v - cv) * cs];
    const shape = pts(rrect(u0, v0, u1, v1, 1.6, 3)).map(([u, v]) => tf(u, v));
    const lines = [], marks = [];
    const L = (arr) => lines.push(arr.map(([u, v]) => tf(u, v)));
    if (kind === "photo") { L([[u0 + 3, v0 + 4], [u0 + 14, v0 + 18], [u0 + 21, v0 + 11], [u0 + 31, v0 + 24], [u1 - 3, v0 + 4]]); marks.push(ring(u1 - 10, v1 - 10, 4.5).map(([u, v]) => tf(u, v))); }
    if (kind === "photo2") L([[u0 + 3, v0 + 6], [u0 + 12, v0 + 10], [u0 + 22, v0 + 7], [u1 - 3, v0 + 11]]);
    if (kind === "swatch") for (let k = 1; k < 4; k++) L([[u0, v0 + k * 12], [u1, v0 + k * 12]]);
    if (kind === "type") { marks.push(pts(rrect(u0 + 4, v1 - 11, u1 - 8, v1 - 4, 2, 3)).map(([u, v]) => tf(u, v))); L([[u0 + 4, v0 + 9], [u1 - 4, v0 + 9]]); L([[u0 + 4, v0 + 5], [u1 - 13, v0 + 5]]); }
    if (kind === "shape") marks.push(ring(cu, cv - 1, 9, 18).map(([u, v]) => tf(u, v)));
    if (kind === "dots") for (let k = 0; k < 9; k++) marks.push(ring(u0 + 6 + (k % 3) * 6, v0 + 6 + Math.floor(k / 3) * 6, 1.3, 8).map(([u, v]) => tf(u, v)));
    const grp = mk("g", {}, g);
    const back = mk("path", { class: "lo" }, grp), face = mk("path", { class: "sil" + (i === 0 ? " hi" : "") }, grp);
    const ln = mk("path", { class: "nf lo" }, grp), mk2 = mk("path", { class: "nf" }, grp);
    const pin = mk("circle", { r: 1.6, class: "dot m" }, grp);
    const hitPoly = shape.map(([u, v]) => at(u, v, 1.5));
    return { i, cu, cv, shape, lines, marks, pinAt: tf(cu, v1 - 3), back, face, ln, mk2, pin, grp, hitPoly, z: tween(i === 0 ? 3 : 0), drawn: NaN };
  });

  function draw(t, d) {
    if (d === t.drawn) return;
    t.drawn = d;
    t.back.setAttribute("d", poly(t.shape.map(([u, v]) => at(u, v, d + 0.4))));
    t.face.setAttribute("d", poly(t.shape.map(([u, v]) => at(u, v, d + 2))));
    t.ln.setAttribute("d", t.lines.map((l) => open(l.map(([u, v]) => at(u, v, d + 2)))).join(""));
    t.mk2.setAttribute("d", t.marks.map((l) => poly(l.map(([u, v]) => at(u, v, d + 2)))).join(""));
    place(t.pin, at(t.pinAt[0], t.pinAt[1], d + 2.4));
  }

  const B = register(stage, (_dt, now) => {
    let m = false;
    for (const t of tiles) { draw(t, tval(t.z, now)); if (!tdone(t.z, now)) m = true; }
    return m;
  });
  bag.add(B.unregister);

  /** Point in a screen polygon: the tile's REST outline, which never moves. */
  const inside = (q, pl) => {
    let r = false;
    for (let a = 0, b = pl.length - 1; a < pl.length; b = a++) {
      const [xa, ya] = pl[a], [xb, yb] = pl[b];
      if ((ya > q[1]) !== (yb > q[1]) && q[0] < ((xb - xa) * (q[1] - ya)) / (yb - ya) + xa) r = !r;
    }
    return r;
  };
  const hit = (q) => { for (const t of tiles) if (inside(q, t.hitPoly)) return t.i; return -1; };

  let act = -2;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = tiles[a >= 0 ? a : Math.max(act, 0)];
    act = a;
    for (const t of tiles) {
      const dist = Math.hypot(t.cu - from.cu, t.cv - from.cv);
      const lift = a < 0 ? (t.i === 0 ? 3 : 0) : t.i === a ? LIFT : dist < 48 ? NEAR : 0;
      tset(t.z, lift, now, (dist / 30) * stag);
      t.face.classList.toggle("hi", a < 0 ? t.i === 0 : t.i === a);
      t.pin.setAttribute("class", "dot " + (t.i === a ? "" : "m"));
    }
    if (a >= 0) tiles[a].grp.parentNode.appendChild(tiles[a].grp);
    read.textContent = a < 0 ? "rest" : "образ " + (a + 1);
    B.wake();
  }
  setActive(-1);

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());

  return { set: (v) => { stag = clamp(v, 0, 120); }, destroy: bag.dispose };
}

hairline({
  name: "v1-moodboard",
  means: "Мудборд на мольберте: плитка под курсором отходит от доски к зрителю, соседние чуть следом.",
  rules: [1, 2, 5, 10],
  range: [0, 40, 80],
  tour: [[183, 98], [263, 115], [163, 158], null],
  mount,
});
