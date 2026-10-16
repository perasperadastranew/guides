/**
 * Layers: one phone screen taken apart into three stacked plates. The top
 * plate is what you see (a picture block, text bars, a button), the middle one
 * the user's path (tap dots joined by a dashed route), the bottom one the
 * business task (a coin stack and three rising bars). The pointer picks a
 * plate: it lifts, the plates above it lift further, so the gap opens round
 * it, staggered by distance. The slider is the lift.
 */
const {
  Cam, circ, facing, fit, open, poly, prism, proj, ringAt, rings, rrect, seg, unproj,
  tset, tval, tdone, tween, flatDot, mk, place, pointer, put, register, disposer, solid,
} = HL;

const W = 50, D = 90, T = 3, R = 8;
const ZR = [0, 34, 70];
const NAMES = ["бизнес", "путь", "визуал"];
const LMAX = 24, UP = 1.5;
const CAM_S = 2.0;
const CAM_FIT = [[0, 0, 0], [W, D, 0], [W, 0, 0], [0, D, 0], [0, 0, ZR[2] + T + LMAX * UP], [W, 0, ZR[2] + T + LMAX * UP]];

const shift = (ring, cx, cy) => ring.map((q) => ({ ...q, u: q.u + cx, v: q.v + cy }));

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let L = value;
  const C = Cam(45, 0.5, CAM_S);
  fit(C, CAM_FIT, 200, 166);
  const P = proj(C), front = facing(C);
  const g = mk("g", {}, svg);
  const [pr, pi] = rings(0, 0, W, D, R, 1.6);

  // Each plate is a group of parts; a part redraws itself from the plate's height z.
  const layers = ZR.map((zr, i) => {
    const grp = mk("g", {}, g), parts = [];
    const plate = solid(grp);
    parts.push((z) => put(plate, prism(P, front, pr, pi, z, z + T)));
    const flat = (cls, fn) => { const el = mk("path", { class: cls }, grp); parts.push((z) => el.setAttribute("d", fn(z + T))); return el; };
    const box = (x0, y0, x1, y1, r, h) => {
      const s = solid(grp), [a, b] = rings(x0, y0, x1, y1, r, Math.min(1, (x1 - x0) / 4));
      parts.push((z) => put(s, prism(P, front, a, b, z + T, z + T + h)));
    };
    const dot = (u, v, cls) => { const el = flatDot(grp, C, 1.5, cls); parts.push((z) => place(el, P(u, v, z + T))); return el; };
    const dots = [];
    if (i === 0) {
      // business: a coin stack at the back, three bars rising toward the front
      for (let k = 0; k < 3; k++) {
        const s = solid(grp), a = shift(circ(7, 20), 30, 18), b = shift(circ(5.6, 20), 30, 18);
        parts.push((z) => put(s, prism(P, front, a, b, z + T + k * 3, z + T + k * 3 + 3)));
      }
      box(8, 50, 17, 59, 2, 6); box(8, 64, 17, 73, 2, 11); box(8, 78, 17, 87, 2, 18);
      flat("nf lo", (z) => seg(P(26, 55, z), P(42, 55, z)) + seg(P(26, 69, z), P(37, 69, z)) + seg(P(26, 83, z), P(42, 83, z)));
    } else if (i === 1) {
      // path: four taps joined by a dashed route
      const taps = [[12, 14], [37, 32], [14, 56], [37, 78]];
      flat("nf dash", (z) => open(taps.map(([u, v]) => P(u, v, z))));
      taps.forEach(([u, v], k) => dots.push(dot(u, v, k === 0 ? "dot" : "dot m")));
    } else {
      // visual: a picture block with a round mark, two text bars, a button
      box(6, 7, W - 6, 36, 3, 2);
      flat("nf lo", (z) => poly(ringAt(P, shift(circ(4.5, 16), 30, 15), z + 2)));
      flat("nf lo", (z) => seg(P(7, 46, z), P(40, 46, z)) + seg(P(7, 53, z), P(28, 53, z)));
      box(6, 66, W - 6, 78, 5, 2);
      flat("nf", (z) => seg(P(18, D - 5, z), P(W - 18, D - 5, z)));
    }
    return { grp, plate, parts, dots, zr, tw: tween(zr), drawn: NaN };
  });

  const draw = (ly, z) => { if (z === ly.drawn) return; ly.drawn = z; ly.parts.forEach((f) => f(z)); };
  const B = register(stage, (_dt, now) => {
    let m = false;
    layers.forEach((ly) => { draw(ly, tval(ly.tw, now)); if (!tdone(ly.tw, now)) m = true; });
    return m;
  });
  bag.add(B.unregister);

  /** Which plate: the pointer laid on each plate's REST top, nearest its middle wins. */
  function hit([sx, sy]) {
    let best = -1, bd = 1.15;
    ZR.forEach((zr, i) => {
      const [u, v] = unproj(C, sx, sy, zr + T);
      const d = Math.max(Math.abs(u - W / 2) / (W / 2), Math.abs(v - D / 2) / (D / 2));
      if (d < bd) { bd = d; best = i; }
    });
    return best;
  }

  let act = -1;
  function setActive(a, force) {
    if (a === act && !force) return;
    const now = performance.now(), from = a >= 0 ? a : act < 0 ? 2 : act;
    act = a;
    layers.forEach((ly, i) => {
      const to = a < 0 ? ly.zr : i === a ? ly.zr + L : i > a ? ly.zr + L * UP : ly.zr;
      tset(ly.tw, to, now, Math.abs(i - from) * 45);
      ly.plate.sil.classList.toggle("hi", i === a);
    });
    // the rest mark: the path's first tap, given up once a plate is chosen
    layers[1].dots[0].setAttribute("class", a < 0 ? "dot" : "dot m");
    read.textContent = a < 0 ? "rest" : NAMES[a];
    B.wake();
  }

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());
  return { set: (v) => { L = v; if (act >= 0) setActive(act, true); }, destroy: bag.dispose };
}

hairline({
  name: "s1-layers",
  means: "Один экран в трёх слоях: визуал, путь пользователя и задача бизнеса, и слой под курсором поднимается.",
  rules: [1, 2, 5, 9],
  range: [10, 17, 24],
  tour: [[200, 134], [200, 196], [200, 255], null],
  mount,
});
