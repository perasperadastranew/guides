/**
 * Story: a tear-off ticket of three segments joined by perforations, lying on
 * the desk. The segment under the pointer lifts off the ticket; its neighbours
 * part from it, staggered outwards. At rest the stub is half torn away and its
 * perforation is the bright mark. The slider is the lift.
 */
const { Cam, clamp, fit, poly, proj, rad, seg, tween, tset, tval, tdone, flatDot, mk, place, pointer, register, disposer, unproj } = HL;

const N = 3, L = 46, W = 60, GAP = 1.4, TH = 2.6, RC = 5, RN = 4.4, STEP = L + GAP;
const REST = [{ dx: 0, z: 0, a: 0 }, { dx: 0, z: 0, a: 0 }, { dx: 5, z: 2.5, a: 7 }];
const WORDS = ["когда", "хочу", "чтобы"];

/** Points of a quarter arc round (cx, cy) from a0 to a1 degrees. */
const arc = (cx, cy, r, a0, a1) => [0, 1, 2, 3, 4, 5].map((k) => {
  const t = rad(a0 + ((a1 - a0) * k) / 5);
  return [cx + r * Math.cos(t), cy + r * Math.sin(t)];
});

/** Segment i's outline in its own frame (u along the ticket, 0..L): rounded outer corners, half-round notches at a seam. */
function outline(i) {
  const nl = i > 0, nr = i < N - 1;
  return [
    ...(nl ? arc(0, 0, RN, 90, 0) : arc(RC, RC, RC, 180, 270)),
    ...(nr ? arc(L, 0, RN, 180, 90) : arc(L - RC, RC, RC, 270, 360)),
    ...(nr ? arc(L, W, RN, 270, 180) : arc(L - RC, W - RC, RC, 0, 90)),
    ...(nl ? arc(0, W, RN, 360, 270) : arc(RC, W - RC, RC, 90, 180)),
  ];
}

/** What is printed on segment i, as lines in its own frame: text rows, or the stub's bar code. */
function print(i) {
  if (i === 0) return [[8, 14, 34, 14], [8, 22, 28, 22], [8, 30, 36, 30], [8, 38, 22, 38]];
  if (i === 1) return [[8, 14, 38, 14], [8, 22, 32, 22], [8, 30, 38, 30], [8, 38, 26, 38], [8, 46, 34, 46]];
  const out = [], xs = [9, 11, 12.5, 15, 16.5, 19, 22, 23.5, 26, 29, 30.5, 33, 35];
  for (const x of xs) out.push([x, 16, x, 42]);
  return out;
}

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let lift = value;

  const C = Cam(45, 0.5, 2.02);
  const far = N * STEP + 10;
  fit(C, [[-10, -4, 0], [far, -4, 0], [-10, W + 4, 0], [far, W + 4, 0], [-10, -4, 36], [far, -4, 36]], 200, 170);
  const P = proj(C);

  const g = mk("g", {}, svg), segs = [];
  // where each segment lies on the ticket, as a dashed guide under it: a lifted one leaves its place drawn
  const slot = mk("path", { class: "nf dash" }, g);
  for (let i = 0; i < N; i++) {
    const grp = mk("g", {}, g);
    const back = mk("path", { class: "lo" }, grp), face = mk("path", { class: "sil" }, grp);
    const lines = mk("path", { class: "nf lo" }, grp);
    // the perforation along the right seam, and the segment's number as dots in its corner
    const holes = [], num = [];
    if (i < N - 1) for (let v = RN + 4; v <= W - RN - 4; v += 4.4) holes.push({ v, el: flatDot(grp, C, 0.62, i === 1 ? "dot" : "dot off") });
    for (let k = 0; k <= i; k++) num.push({ u: L - 9 - k * 3.4, el: flatDot(grp, C, 0.7, "dot m") });
    const r = REST[i];
    segs.push({ i, shape: outline(i), ink: print(i), back, face, lines, holes, num, dx: tween(r.dx), z: tween(r.z), a: tween(r.a) });
  }

  /** Segment s's frame: a point (u, v) at height h, after its slide dx, its lift z and its turn a round the seam's middle. */
  function frame(s, dx, z, a) {
    const c = Math.cos(rad(a)), sn = Math.sin(rad(a)), x0 = s.i * STEP + dx;
    return (u, v, h) => P(x0 + u * c - (v - W / 2) * sn, W / 2 + u * sn + (v - W / 2) * c, z + h);
  }

  function draw(s, now) {
    const w = frame(s, tval(s.dx, now), tval(s.z, now), tval(s.a, now));
    s.back.setAttribute("d", poly(s.shape.map(([u, v]) => w(u, v, 0))));
    s.face.setAttribute("d", poly(s.shape.map(([u, v]) => w(u, v, TH))));
    s.lines.setAttribute("d", s.ink.map(([u0, v0, u1, v1]) => seg(w(u0, v0, TH), w(u1, v1, TH))).join(""));
    s.holes.forEach((h) => place(h.el, w(L - 2.4, h.v, TH)));
    s.num.forEach((d) => place(d.el, w(d.u, W - 7, TH)));
  }

  slot.setAttribute("d", segs.map((s) => poly(s.shape.map(([u, v]) => P(s.i * STEP + u, v, 0)))).join(""));

  const B = register(stage, (_dt, now) => {
    let moving = false;
    for (const s of segs) { draw(s, now); if (!tdone(s.dx, now) || !tdone(s.z, now) || !tdone(s.a, now)) moving = true; }
    return moving;
  });
  bag.add(B.unregister);

  /** The segment under the pointer, on the ticket's resting top: it never moves. */
  function hit(p) {
    const [x, y] = unproj(C, p[0], p[1], TH);
    if (y < -6 || y > W + 6 || x < -6 || x > N * STEP + 6) return -1;
    return clamp(Math.floor(x / STEP), 0, N - 1);
  }

  let act = -1;
  function setActive(a, force) {
    if (a === act && !force) return;
    const now = performance.now(), from = a >= 0 ? a : act;
    act = a;
    for (const s of segs) {
      const d = Math.abs(s.i - from), delay = d * 45, r = REST[s.i];
      if (a < 0) { tset(s.dx, r.dx, now, delay); tset(s.z, r.z, now, delay); tset(s.a, r.a, now, delay); }
      else if (s.i === a) { tset(s.dx, 0, now, 0); tset(s.z, lift, now, 0); tset(s.a, 0, now, 0); }
      else { tset(s.dx, Math.sign(s.i - a) * 10 / d, now, delay); tset(s.z, lift * 0.14 / d, now, delay); tset(s.a, 0, now, delay); }
      s.face.classList.toggle("hi", s.i === a);
      s.holes.forEach((h) => h.el.setAttribute("class", s.i === 1 && a < 0 ? "dot" : "dot off"));
    }
    read.textContent = a < 0 ? "rest" : WORDS[a];
    B.wake();
  }

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());
  read.textContent = "rest";

  return {
    set: (v) => { lift = v; if (act >= 0) setActive(act, true); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "r5-story",
  means: "Билет из трёх частей «когда · хочу · чтобы»: часть под курсором отрывается от билета.",
  rules: [1, 2, 4, 10],
  range: [12, 22, 32],
  tour: [[131, 163], [198, 196], [266, 230], null],
  mount,
});
