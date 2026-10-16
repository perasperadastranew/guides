/**
 * Fit: two thick plates on a tray, cut along one matching edge, a square tab
 * and a round knob on one, the sockets for them in the other. The pointer's x
 * sets the gap between them, on a spring: to the left they stand far apart,
 * to the right they close and fit. The moving plate's top is the bright edge;
 * when they fit, the bright takes in both, as one piece. The slider is the
 * widest gap.
 */
const { Cam, clamp, fit, fillet, open, poly, proj, rings, prism, facing, seg, spring, stepS, mk, put, solid, pointer, register, disposer } = HL;

const W = 48, D = 64, H = 17, GREST = 26, GMAXX = 72, TX = 13;

/** The cut both plates share, from y = 0 to y = D: x is how far the left plate reaches at y. */
function profile() {
  const pts = [[0, 0], [0, 8], [TX, 8], [TX, 22], [0, 22], [0, 34]], r = [0, 1.8, 3, 3, 1.8, 1.8];
  for (let k = 1; k < 12; k++) { const a = -Math.PI / 2 + (Math.PI * k) / 12; pts.push([11 * Math.cos(a), 45 + 11 * Math.sin(a)]); r.push(0); }
  pts.push([0, 56], [0, D]); r.push(1.8, 0);
  return { pts, r };
}
const clean = (pts) => pts.filter((p, i) => { const q = pts[(i + pts.length - 1) % pts.length]; return Math.hypot(p[0] - q[0], p[1] - q[1]) > 1e-4; });

/** The two outlines, in their own frames, the cut at x = 0. */
function outlines() {
  const pr = profile(), rr = pr.r.slice(); rr[0] = 3; rr[rr.length - 1] = 3;
  const A = clean(fillet([[-W, 0], ...pr.pts, [-W, D]], [6, ...rr, 6]));
  const B = clean(fillet([[W, 0], [W, D], ...pr.pts.slice().reverse()], [6, 6, ...rr.slice().reverse()]));
  return { A, B };
}

/** The walls of an outline facing the viewer: their corners, and whether a turn to a hidden wall follows or precedes. */
function walls(pts) {
  let area = 0;
  pts.forEach((p, i) => { const q = pts[(i + 1) % pts.length]; area += p[0] * q[1] - q[0] * p[1]; });
  const sgn = area > 0 ? 1 : -1, n = pts.length;
  const faces = pts.map((p, i) => { const q = pts[(i + 1) % n]; return sgn * ((q[1] - p[1]) - (q[0] - p[0])) > 0; });
  const out = [];
  for (let i = 0; i < n; i++) if (faces[i]) out.push({ a: pts[i], b: pts[(i + 1) % n], edgeA: !faces[(i + n - 1) % n], edgeB: !faces[(i + 1) % n] });
  return { out, faces };
}

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let gmax = value;

  const C = Cam(45, 0.5, 1.68);
  const X0 = -W - GMAXX / 2 - 4, X1 = W + GMAXX / 2 + 4;
  fit(C, [[X0, -8, -4], [X1, D + 8, -4], [X1, -8, -4], [X0, D + 8, -4], [X0, -8, H], [X1, -8, H]], 200, 166);
  const P = proj(C), front = facing(C);
  const g = mk("g", {}, svg);
  const [tr, ti] = rings(X0, -8, X1, D + 8, 8, 2);
  put(solid(g), prism(P, front, tr, ti, -4, 0));

  const { A, B } = outlines();
  const wallG = mk("g", {}, g);
  const plates = [A, B].map((pts, k) => {
    const { out, faces } = walls(pts);
    const ws = out.map((w) => ({ ...w, k, key: 0, fo: mk("path", { class: "fo" }, wallG), st: mk("path", { class: "nf sil" }, wallG) }));
    const top = mk("g", {}, g);
    return { pts, faces, ws, face: mk("path", { class: "fo" }, top), sil: mk("path", { class: "nf sil" }, top), cr: mk("path", { class: "nf lo" }, top) };
  });

  const gap = spring(GREST);
  let drawn = NaN;
  function draw() {
    const gv = Math.max(0, gap.x);
    if (gv === drawn) return;
    drawn = gv;
    const all = [];
    plates.forEach((pl, k) => {
      const dx = k ? gv / 2 : -gv / 2, at = (p, z) => P(p[0] + dx, p[1], z);
      for (const w of pl.ws) {
        w.fo.setAttribute("d", poly([at(w.a, 0), at(w.b, 0), at(w.b, H), at(w.a, H)]));
        w.st.setAttribute("d", seg(at(w.a, 0), at(w.b, 0)) + (w.edgeA ? seg(at(w.a, 0), at(w.a, H)) : "") + (w.edgeB ? seg(at(w.b, 0), at(w.b, H)) : ""));
        w.key = w.a[0] + w.b[0] + 2 * dx + w.a[1] + w.b[1];
        all.push(w);
      }
      // the top: back-facing edges are the silhouette, front-facing ones the dim crease
      const n = pl.pts.length;
      let s = "", c = "";
      pl.pts.forEach((p, i) => { const e = seg(at(p, H), at(pl.pts[(i + 1) % n], H)); if (pl.faces[i]) c += e; else s += e; });
      pl.face.setAttribute("d", poly(pl.pts.map((p) => at(p, H))));
      pl.sil.setAttribute("d", s);
      pl.cr.setAttribute("d", c);
    });
    // painter's order: the walls of both plates, farthest first
    all.sort((u, v) => u.key - v.key);
    for (const w of all) { wallG.appendChild(w.fo); wallG.appendChild(w.st); }
  }

  const Bk = register(stage, (dt) => { const m = stepS(gap, dt); draw(); return m; });
  bag.add(Bk.unregister);

  let over = false;
  function mark() {
    const t = gap.t, fitted = over && t === 0;
    plates[0].sil.classList.add("hi");
    plates[1].sil.classList.toggle("hi", fitted);
    read.textContent = !over ? "rest" : t === 0 ? "совпало" : t > gmax * 0.5 ? "далеко" : "ближе";
  }
  /** The pointer's x, across the middle of the stage, sets the gap: far at the left, none at the right. */
  function aim(x) {
    const u = clamp((x - 70) / 220, 0, 1);
    gap.t = u > 0.8 ? 0 : gmax * (1 - u / 0.8);
    over = true; mark(); Bk.wake();
  }

  bag.add(pointer(stage, { move: (p) => aim(p[0]), leave: () => { over = false; gap.t = GREST; mark(); Bk.wake(); } }));
  bag.add(() => svg.replaceChildren());
  mark();

  return {
    set: (v) => { gmax = clamp(v, 30, GMAXX); if (over && gap.t > 0) { gap.t = Math.min(gap.t, gmax); mark(); Bk.wake(); } },
    destroy: bag.dispose,
  };
}

hairline({
  name: "p1-fit",
  means: "Обещание продукта и потребность человека как две детали с вырезами: веди вправо, и они сходятся и совпадают.",
  rules: [3, 5, 6, 8],
  range: [40, 56, 72],
  tour: [[100, 160], [200, 160], [290, 165], null],
  mount,
});
