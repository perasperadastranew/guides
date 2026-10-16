/**
 * Instances: a long board; at its far end a stepped pedestal carries the main
 * component, a pill button with a label bar, and down the board stand five
 * copies of the same button, tied to it by a dashed line on the board. Over
 * the main one, all five copies lift in turn, spreading out from it; over a
 * copy, that copy lifts and its neighbours a little. At rest the main button
 * is bright and the copies lie in a ripple fading away from it. The slider is
 * the stagger, in ms.
 */
const {
  Cam, fit, proj, facing, prism, rings, rrect, seg,
  tween, tset, tval, tdone, mk, solid, put, pointer, register, disposer,
} = HL;

const N = 5, X0 = 40, GAP = 31, BW = 9, BL = 18, BH = 6, PED = 18, LIFT = 18, MAIN = 5;
const REST = [7, 4.5, 2.5, 1, 0];

/** A pill button standing on z0: its solid, plus a label bar along its top. */
function button(P, front, el, bar, x, z0) {
  const ring = rrect(x - BW, -BL, x + BW, BL, BW, 6), inner = rrect(x - BW + 1.4, -BL + 1.4, x + BW - 1.4, BL - 1.4, BW - 1.4, 6);
  put(el, prism(P, front, ring, inner, z0, z0 + BH));
  bar.setAttribute("d", seg(P(x, -7, z0 + BH), P(x, 7, z0 + BH)));
}

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let stag = value;
  const XE = X0 + (N - 1) * GAP;

  const C = Cam(45, 0.5, 1.62);
  fit(C, [[-18, -23, -5], [XE + 14, 23, -5], [XE + 14, -23, -5], [-18, 23, -5], [0, -BL, PED + BH + MAIN + 2], [X0, -BL, BH + LIFT]], 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  // the board, then the dashed tie along it, painted before everything that stands on it
  const [br, bi] = rings(-18, -23, XE + 14, 23, 8, 2);
  put(solid(g), prism(P, front, br, bi, -5, 0));
  mk("path", { d: seg(P(0, 0, 0), P(XE, 0, 0)), class: "nf lo dash" }, g);

  // the pedestal: a wide step, then a column
  const [s1, s1i] = rings(-15, -21, 15, 21, 5, 1.6);
  put(solid(g), prism(P, front, s1, s1i, 0, 4));
  const [s2, s2i] = rings(-11, -BL - 2, 11, BL + 2, 4, 1.4);
  put(solid(g), prism(P, front, s2, s2i, 4, PED));

  const parts = [];
  const add = (x, base, r0) => {
    const el = solid(g), bar = mk("path", { class: "nf lo" }, g);
    parts.push({ x, base, r0, el, bar, z: tween(r0), drawn: NaN });
  };
  add(0, PED, 0);
  for (let k = 0; k < N; k++) add(X0 + k * GAP, 0, REST[k]);

  const B = register(stage, (_dt, now) => {
    let m = false;
    for (const p of parts) {
      const h = tval(p.z, now);
      if (h !== p.drawn) { p.drawn = h; button(P, front, p.el, p.bar, p.x, p.base + h); }
      if (!tdone(p.z, now)) m = true;
    }
    return m;
  });
  bag.add(B.unregister);

  // hit: each part's rest top centre on screen; the nearest within reach
  const tops = parts.map((p) => P(p.x, 0, p.base + p.r0 + BH));
  function hit([sx, sy]) {
    let best = -1, bd = 30;
    tops.forEach((t, i) => { const d = Math.hypot(sx - t[0], (sy - t[1]) * 1.4); if (d < bd) { bd = d; best = i; } });
    return best;
  }

  let act = -1;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = a >= 0 ? a : act >= 0 ? act : 0;
    act = a;
    parts.forEach((p, i) => {
      const k = Math.abs(i - from);
      let to = p.r0;
      if (a === 0) to = i === 0 ? MAIN : LIFT * 0.75;
      else if (a > 0) to = i === a ? LIFT : k === 1 && i > 0 ? p.r0 + LIFT * 0.25 : p.r0;
      tset(p.z, to, now, k * stag);
      p.el.sil.classList.toggle("hi", a < 0 ? i === 0 : i === a);
    });
    read.textContent = a < 0 ? "rest" : a === 0 ? "главный" : "копия " + a;
    B.wake();
  }
  parts[0].el.sil.classList.add("hi");
  read.textContent = "rest";

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());

  return {
    set: (v) => { stag = v; },
    destroy: bag.dispose,
  };
}

hairline({
  name: "d2-instances",
  means: "Главный компонент на подставке и пять его копий: над главным копии поднимаются по очереди, над копией встаёт она одна.",
  rules: [1, 2, 4, 5],
  range: [0, 45, 90],
  tour: [[108, 98], [225, 179], [296, 218], null],
  mount,
});
