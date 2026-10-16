/**
 * Loupe: five reference screens lying flat in a row, and a magnifier (a thick
 * ring on a handle) hovering above them. The loupe follows the pointer along
 * the row on a spring; the screens rise under it, falling off with distance,
 * each on its own spring. The screen nearest the loupe takes the bright edge
 * and shows through the ring. The slider is the loupe's reach, in screens.
 */
const {
  Cam, clamp, circ, facing, fit, open, poly, prism, proj, rings, ringAt, rrect, run, seg, unproj,
  spring, stepS, disposer, mk, pointer, put, register, solid,
} = HL;

const N = 5, SW = 30, SH = 50, GAP = 10, PITCH = SW + GAP, T = 3, HMAX = 20, H0 = 1.5;
const RL = 17, RW = 4, ZL = HMAX + H0 + T + 3, RT = 3, HL_ = 30, CY = SH / 2, REST_X = PITCH * 1.25 + SW / 2;
const cx = (i) => i * PITCH + SW / 2;

/** The share of full height u radii away: 1 → .31 at 42% → .09 beyond. */
const falloff = (u) =>
  u <= 0 ? 1 : u <= 0.417 ? 1 - (u / 0.417) * 0.6875 : u <= 1 ? 0.3125 - ((u - 0.417) / 0.583) * 0.2185 : 0.094;

// What each reference shows, as rounded marks on its screen: [u0, v0, u1, v1, r] in screen-local units.
const CONTENT = [
  [[5, 9, 25, 27, 3], [5, 31, 20, 33.5, 1.2], [5, 37, 25, 39.5, 1.2]],
  [[5, 9, 11, 15, 3], [13, 10.5, 25, 13.5, 1.5], [5, 19, 11, 25, 3], [13, 20.5, 25, 23.5, 1.5], [5, 29, 11, 35, 3], [13, 30.5, 25, 33.5, 1.5]],
  [[5, 9, 14, 19, 2.5], [16, 9, 25, 19, 2.5], [5, 22, 14, 32, 2.5], [16, 22, 25, 32, 2.5], [8, 36, 22, 40, 2]],
  [[5, 9, 25, 15, 2], [5, 18, 25, 32, 3], [9, 36, 21, 40.5, 2.2]],
  [[10, 10, 20, 20, 5], [6, 25, 24, 28, 1.5], [6, 31, 24, 34, 1.5], [9, 37, 21, 41, 2]],
];

/** Signed area of a screen polygon, to wind the ring's hole against its outline. */
const area = (pts) => pts.reduce((s, p, i) => { const q = pts[(i + 1) % pts.length]; return s + p[0] * q[1] - q[0] * p[1]; }, 0);

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let R = value * PITCH, over = null;

  const C = Cam(45, 0.5, 1.68);
  const ext = [[0, 0, 0], [N * PITCH - GAP, 0, 0], [0, SH, 0], [N * PITCH - GAP, SH, 0], [N * PITCH - GAP, 0, HMAX + T]];
  for (const x of [cx(0), cx(N - 1)]) ext.push([x - RL, CY, ZL + RT], [x + RL, CY, ZL + RT], [x, CY - RL - HL_, ZL + RT], [x, CY + RL, ZL]);
  fit(C, ext, 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  const scr = [];
  for (let i = 0; i < N; i++) {
    const x0 = i * PITCH;
    const [ring, inner] = rings(x0, 0, x0 + SW, SH, 5, 1.1);
    const face = rrect(x0 + 2.6, 5, x0 + SW - 2.6, SH - 4.5, 2.6, 4);
    const marks = CONTENT[i].map(([u0, v0, u1, v1, r]) => rrect(x0 + u0, v0, x0 + u1, v1, r, 4));
    const el = solid(g);
    const fEl = mk("path", { class: "nf lo" }, el.g), sEl = mk("path", { class: "nf" }, el.g), mEl = mk("path", { class: "nf lo" }, el.g);
    const h0 = H0 + HMAX * falloff(Math.abs(cx(i) - REST_X) / (1.2 * PITCH));
    scr.push({ i, x0, ring, inner, face, marks, el, fEl, sEl, mEl, h0, sp: spring(h0, { eps: 0.03 }), drawn: NaN });
  }

  // The loupe, painted last: it hovers above everything it passes over. Its handle points away
  // from the row, so it is the farther part and is painted first.
  const lg = mk("g", {}, g);
  const handleEl = solid(lg), rimEl = solid(lg), wallEl = mk("path", { class: "nf lo" }, lg);
  const outer = circ(RL, 40), outerIn = circ(RL - 0.9, 40), hole = circ(RL - RW, 40);
  const shift = (ring, x) => ring.map((q) => ({ ...q, u: q.u + x, v: q.v + CY }));
  const lx = spring(REST_X);
  let lDrawn = NaN;

  function drawScreen(s) {
    const h = s.sp.x;
    if (h === s.drawn) return;
    s.drawn = h;
    const top = h + T;
    put(s.el, prism(P, front, s.ring, s.inner, h, top));
    s.fEl.setAttribute("d", poly(ringAt(P, s.face, top)));
    s.sEl.setAttribute("d", seg(P(s.x0 + SW / 2 - 4, 2.6, top), P(s.x0 + SW / 2 + 4, 2.6, top)));
    s.mEl.setAttribute("d", s.marks.map((m) => poly(ringAt(P, m, top))).join(""));
  }

  function drawLoupe() {
    const x = lx.x;
    if (x === lDrawn) return;
    lDrawn = x;
    const o = shift(outer, x), oi = shift(outerIn, x), h = shift(hole, x);
    const pr = prism(P, front, o, oi, ZL, ZL + RT);
    let hp = ringAt(P, h, ZL + RT);
    const sil = hull(o);
    if (Math.sign(area(hp)) === Math.sign(area(sil))) hp = hp.slice().reverse();
    put(rimEl, { sil: pr.sil + poly(hp), crease: pr.crease });
    // the far inside wall of the ring, seen through the hole
    wallEl.setAttribute("d", open(ringAt(P, run(h, (q) => !front(q)), ZL)));
    const [hr, hi] = rings(x - 2.6, CY - RL - HL_, x + 2.6, CY - RL + 1.5, 2.6, 0.8);
    put(handleEl, prism(P, front, hr, hi, ZL - 0.5, ZL + RT + 0.5));
  }
  /** The ring's outline on screen: the hull of its top and bottom circles. */
  function hull(o) { return HL.hull(ringAt(P, o, ZL).concat(ringAt(P, o, ZL + RT))); }

  let lit = -1;
  /** The screen the loupe is aiming at: from the spring's target, never its position. */
  function aim() {
    const t = lx.t;
    let best = 0;
    scr.forEach((s, i) => { if (Math.abs(cx(i) - t) < Math.abs(cx(best) - t)) best = i; });
    if (best !== lit) { lit = best; scr.forEach((s, i) => s.el.sil.classList.toggle("hi", i === best)); }
    return best;
  }

  const B = register(stage, (dt) => {
    let m = stepS(lx, dt);
    for (const s of scr) { if (stepS(s.sp, dt)) m = true; drawScreen(s); }
    drawLoupe();
    return m;
  });
  bag.add(B.unregister);

  function retarget() {
    lx.t = over == null ? REST_X : over;
    scr.forEach((s, i) => { s.sp.t = over == null ? s.h0 : H0 + HMAX * falloff(Math.abs(cx(i) - over) / R); });
    const a = aim();
    read.textContent = over == null ? "rest" : "экран " + (a + 1);
    B.wake();
  }
  retarget();

  // The pointer is read on a fixed plane through the row, and only its x along the row counts.
  bag.add(pointer(stage, {
    move: (p) => {
      const w = unproj(C, p[0], p[1], HMAX / 3);
      over = Math.abs(w[1] - CY) > SH ? null : clamp(w[0], cx(0), cx(N - 1));
      retarget();
    },
    leave: () => { over = null; retarget(); },
  }));
  bag.add(() => svg.replaceChildren());

  return {
    set: (v) => { R = v * PITCH; retarget(); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "p3-loupe",
  means: "Лупа идёт вдоль ряда референсов, и экран под ней поднимается ближе, а соседние чуть меньше.",
  rules: [1, 3, 4, 8],
  range: [0.7, 1.2, 2],
  tour: [[101, 135], [196, 177], [291, 231], null],
  mount,
});
