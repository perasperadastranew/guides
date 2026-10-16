/**
 * Mockup: a scene a generator would draw, a plinth with a sphere and a potted
 * plant, and a phone lying on a small stand, its screen recess empty. The
 * screen plate floats above it, dashed drops marking where it lands. The
 * pointer's height lowers the plate into the phone, on a spring. The slider is
 * how high the plate floats.
 */
const {
  Cam, clamp, circ, extremes, facing, fillet, fit, open, poly, prism, proj, rad, rings, rrect, run, seg,
  spring, stepS, mk, put, solid, pointer, register, disposer,
} = HL;

const BX = 62, BY = 46, Z0 = 8, PX = 14, PY = 6, ZS = 20, ZP = 24, PW = 17, PL = 33, IN = 2.6;
const SPH = { x: -36, y: -22, r: 15 }, POT = { x: -46, y: 20, r: 9, h: 15 };

/** One leaf of the plant, standing in its own plane from the pot's soil, leaning out at angle a. */
function leaf(P, a, len) {
  const d = [Math.cos(rad(a)), Math.sin(rad(a))], e = [-d[1], d[0]], zt = Z0 + POT.h - 2;
  const at = (w, h) => P(POT.x + d[0] * h * 0.5 + e[0] * w, POT.y + d[1] * h * 0.5 + e[1] * w, zt + h * 0.86);
  const shape = fillet([[0, 0], [5.5, len * 0.45], [0, len], [-5.5, len * 0.45]], [0.6, 4, 0.6, 4]);
  return { d: poly(shape.map((p) => at(p[0], p[1]))), rib: seg(at(0, 1), at(0, len * 0.8)), depth: d[0] + d[1] };
}

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let ZMAX = value;
  const C = Cam(45, 0.5, 1.8);
  fit(C, [[-BX, -BY, 0], [BX, BY, 0], [BX, -BY, 0], [-BX, BY, 0], [PX - PW, PY - PL, ZP + 70]], 200, 166);
  const P = proj(C), front = facing(C);
  const g = mk("g", {}, svg);

  // the plinth
  const [br, bi] = rings(-BX, -BY, BX, BY, 10, 2);
  put(solid(g), prism(P, front, br, bi, 0, Z0));

  // the sphere, resting on the plinth: a round outline and the near half of its equator
  const sc = P(SPH.x, SPH.y, Z0 + SPH.r);
  mk("ellipse", { cx: sc[0], cy: sc[1], rx: SPH.r * C.S, ry: SPH.r * C.S, class: "sil" }, g);
  const eq = circ(SPH.r, 32);
  mk("path", { class: "nf lo", d: open(run(eq, front).map((q) => P(SPH.x + q.u, SPH.y + q.v, Z0 + SPH.r))) }, g);

  // the plant: a round pot and three leaves, far leaves first
  const [pr, pi] = rings(POT.x - POT.r, POT.y - POT.r, POT.x + POT.r, POT.y + POT.r, POT.r, 1.4);
  const leaves = [[-130, 24], [-60, 30], [200, 20], [20, 22]].map(([a, l]) => leaf(P, a, l));
  for (const lf of leaves.filter((l) => l.depth < 0)) { mk("path", { class: "sil", d: lf.d }, g); mk("path", { class: "nf lo", d: lf.rib }, g); }
  put(solid(g), prism(P, front, pr, pi, Z0, Z0 + POT.h));
  for (const lf of leaves.filter((l) => l.depth >= 0)) { mk("path", { class: "sil", d: lf.d }, g); mk("path", { class: "nf lo", d: lf.rib }, g); }

  // the stand and the phone lying on it, its screen recess empty and its camera pill at the far end
  const [sr, si] = rings(PX - PW - 4, PY - PL - 4, PX + PW + 4, PY + PL + 4, 6, 1.6);
  put(solid(g), prism(P, front, sr, si, Z0, ZS));
  const [hr, hi] = rings(PX - PW, PY - PL, PX + PW, PY + PL, 7, 1.1);
  put(solid(g), prism(P, front, hr, hi, ZS, ZP));
  const rec = rrect(PX - PW + IN, PY - PL + IN, PX + PW - IN, PY + PL - IN, 5, 4);
  mk("path", { class: "nf lo", d: poly(rec.map((q) => P(q.u, q.v, ZP))) }, g);

  // the drops, behind the plate, then the plate with what the screen shows
  const drops = mk("path", { class: "dash nf" }, g);
  const plate = solid(g);
  plate.sil.classList.add("hi");
  const ui = mk("path", { class: "nf lo" }, g), btn = mk("path", { class: "nf" }, g);
  const [lr, li] = rings(PX - PW + IN, PY - PL + IN, PX + PW - IN, PY + PL - IN, 4.4, 1);
  const box = (x0, y0, x1, y1, r) => rrect(PX + x0, PY + y0, PX + x1, PY + y1, r, 4);

  let drawn = NaN;
  function draw(h) {
    if (Math.abs(h - drawn) < 0.01) return;
    drawn = h;
    const z0 = ZP - 1 + h, z1 = z0 + 1.6;
    put(plate, prism(P, front, lr, li, z0, z1));
    const on = (r) => poly(r.map((q) => P(q.u, q.v, z1)));
    const line = (x0, x1, y) => seg(P(PX + x0, PY + y, z1), P(PX + x1, PY + y, z1));
    ui.setAttribute("d", on(box(-9, -24, 9, -6, 2.5)) + line(-9, -1, -27.5) + line(-9, 7, 1) + line(-9, 2, 6) + line(-9, 5, 11));
    btn.setAttribute("d", on(box(-8, 17, 8, 23, 3)));
    let d = "";
    if (h > 2) for (const q of extremes(P, lr)) d += seg(P(q.u, q.v, ZP), P(q.u, q.v, z0));
    drops.setAttribute("d", d);
  }

  const REST = 0.62;
  const sp = spring(ZMAX * REST, { eps: 0.02 });
  const B = register(stage, (dt) => { const m = stepS(sp, dt); draw(Math.max(0, sp.x)); return m; });
  bag.add(B.unregister);

  // the pointer's height alone sets the target: from above the floating plate down to the phone
  let t = null;
  const yA = () => P(PX, PY, ZP + ZMAX)[1], yB = () => P(PX, PY + PL, ZP)[1];
  function retarget() {
    if (t === null) { sp.t = ZMAX * REST; read.textContent = "rest"; }
    else {
      const h = ZMAX * (1 - t);
      sp.t = h;
      read.textContent = t < 0.4 ? "сцена" : t < 0.9 ? "ближе" : "экран на месте";
    }
    B.wake();
  }
  bag.add(pointer(stage, {
    move: ([, sy]) => { t = clamp((sy - yA()) / (yB() - yA()), 0, 1); retarget(); },
    leave: () => { t = null; retarget(); },
  }));
  bag.add(() => svg.replaceChildren());
  read.textContent = "rest";

  return {
    set: (v) => { ZMAX = clamp(v, 20, 70); retarget(); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "c3-mockup",
  means: "Сцена для мокапа: телефон на подставке, а экран парит над ним; указатель опускает экран на место.",
  rules: [3, 5, 6, 8],
  range: [34, 50, 66],
  tour: [[220, 70], [230, 160], [240, 230], null],
  mount,
});
