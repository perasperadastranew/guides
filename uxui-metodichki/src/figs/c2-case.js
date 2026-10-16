/**
 * Case: a ring binder lying open, its five divider pages riffled round the
 * rings. Each page has a tab on its outer edge, at its own place along the
 * edge, punched with its number in dots. The page under the pointer stands up
 * and lifts; the pages before it fall to the left cover and the ones after it
 * to the right, staggered outwards. The slider is the stagger, in ms.
 */
const {
  Cam, clamp, fillet, fit, poly, open, proj, rad, rings, prism, facing, seg, unproj,
  tween, tset, tval, tdone, mk, place, put, solid, pointer, register, disposer,
} = HL;

const N = 5, L = 86, PW = 58, U0 = 10, ZH = 8, RR = 7.5, TH = 6, TW = 12, TK = 1.3, LIFT = 6;
const BX = 74, BY0 = -5, BY1 = L + 5, BZ = 2.5;
const WORDS = ["задача", "исследование", "решения", "тест", "итог"];
const REST = [150, 118, 88, 62, 16], RINGS = [0.2, 0.5, 0.8].map((f) => f * L);
const VIEW = 39; // the page angle seen edge-on: the nearer a page is to it, the later it is painted

/** Page i's outline in its own plane: u away from the spine, v along it, with its tab. */
function shape(i) {
  const u1 = U0 + PW, t0 = 8 + i * 14;
  return fillet(
    [[U0, 3], [u1, 3], [u1, t0], [u1 + TH, t0], [u1 + TH, t0 + TW], [u1, t0 + TW], [u1, L - 3], [U0, L - 3]],
    [1.5, 3, 1.6, 2.2, 2.2, 1.6, 3, 1.5],
  );
}

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let stag = value;
  const C = Cam(45, 0.5, 1.44);
  const tip = ZH + PW + U0 + TH + LIFT;
  fit(C, [[-BX, BY0, 0], [BX, BY0, 0], [-BX, BY1, 0], [BX, BY1, 0], [0, BY0, tip], [0, BY1, tip]], 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  // the open folder: one board, folded at the spine
  const [br, bi] = rings(-BX, BY0, BX, BY1, 6, 1.8);
  put(solid(g), prism(P, front, br, bi, 0, BZ));
  mk("path", { class: "nf lo", d: seg(P(-6, BY0 + 2, BZ), P(-6, BY1 - 2, BZ)) + seg(P(6, BY0 + 2, BZ), P(6, BY1 - 2, BZ)) }, g);
  // the ring mechanism along the spine
  const [mr, mi] = rings(-4, L * 0.12, 4, L * 0.88, 3, 1);
  put(solid(g), prism(P, front, mr, mi, BZ, BZ + 2.5));

  // the rings, cut into arcs by angle, so each arc is painted in its own place among the pages
  const arcs = [];
  for (let k = -15; k < 195; k += 15) {
    let d = "";
    for (const y of RINGS) {
      const pts = [];
      for (let a = k; a <= k + 15; a += 5) pts.push(P(RR * Math.cos(rad(a)), y, ZH + RR * Math.sin(rad(a))));
      d += open(pts);
    }
    arcs.push([Math.abs(k + 7.5 - VIEW), mk("path", { class: "nf sil", d }, g), "r" + k]);
  }
  const pages = [];
  for (let i = 0; i < N; i++) {
    const grp = mk("g", {}, g), sh = shape(i);
    const back = mk("path", { class: "lo" }, grp), face = mk("path", { class: "sil" }, grp);
    const lines = mk("path", { class: "nf lo" }, grp), head = mk("path", { class: "nf" }, grp);
    const dots = [];
    for (let k = 0; k <= i; k++) dots.push(mk("circle", { r: 0.95, class: "dot off" }, grp));
    pages.push({ i, sh, grp, back, face, lines, head, dots, a: tween(REST[i]), z: tween(0), last: "" });
  }

  function draw(pg, th, lift) {
    const key = th.toFixed(2) + "," + lift.toFixed(2);
    if (key === pg.last) return;
    pg.last = key;
    const c = Math.cos(rad(th)), s = Math.sin(rad(th));
    const w = (u, v, d = 0) => P(u * c + d * s, v, ZH + lift + u * s - d * c);
    pg.back.setAttribute("d", poly(pg.sh.map((p) => w(p[0], p[1], TK))));
    pg.face.setAttribute("d", poly(pg.sh.map((p) => w(p[0], p[1]))));
    pg.head.setAttribute("d", seg(w(U0 + PW - 8, 12), w(U0 + PW - 8, 44)));
    let d = "";
    for (let k = 0; k < 6; k++) { const u = U0 + PW - 17 - k * 7; d += seg(w(u, 12), w(u, k % 2 ? 60 : 72)); }
    pg.lines.setAttribute("d", d);
    const t0 = 8 + pg.i * 14 + TW / 2;
    pg.dots.forEach((el, k) => place(el, w(U0 + PW + TH / 2, t0 + (k - pg.i / 2) * 2.3)));
  }

  let order = "";
  const B = register(stage, (_dt, now) => {
    let moving = false;
    const depth = [];
    for (const pg of pages) {
      const th = tval(pg.a, now);
      draw(pg, th, tval(pg.z, now));
      if (!tdone(pg.a, now) || !tdone(pg.z, now)) moving = true;
      depth.push([Math.abs(th - VIEW), pg.grp, "p" + pg.i]);
    }
    depth.push(...arcs);
    depth.sort((p, q) => q[0] - p[0]);
    const key = depth.map((e) => e[2]).join("");
    if (key !== order) { order = key; for (const e of depth) g.appendChild(e[1]); }
    return moving;
  });
  bag.add(B.unregister);

  // hit test: the nearest page by the screen x of its RESTING outer edge; the rest pose never moves.
  const tipX = REST.map((th) => P((U0 + PW) * Math.cos(rad(th)), L / 2, ZH + (U0 + PW) * Math.sin(rad(th)))[0]);
  function hit([sx, sy]) {
    const [x, y] = unproj(C, sx, sy, ZH + 30);
    if (Math.abs(x) > BX + 20 || y < BY0 - 50 || y > BY1 + 50) return -1;
    let best = 0;
    tipX.forEach((t, i) => { if (Math.abs(sx - t) < Math.abs(sx - tipX[best])) best = i; });
    return best;
  }

  let act = -2;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = a >= 0 ? a : Math.max(act, 0);
    act = a;
    pages.forEach((pg, i) => {
      const k = Math.abs(i - from), delay = k * stag;
      const th = a < 0 ? REST[i] : i === a ? 90 : i < a ? 128 + (a - i) * 12 : 22 - (i - a) * 5;
      tset(pg.a, th, now, delay);
      tset(pg.z, i === a ? LIFT : 0, now, delay);
      const on = a < 0 ? i === 0 : i === a;
      pg.face.classList.toggle("hi", on);
      pg.head.classList.toggle("hi", on);
      pg.dots.forEach((el) => el.setAttribute("class", on ? "dot" : "dot off"));
    });
    read.textContent = a < 0 ? "rest" : WORDS[a];
    B.wake();
  }
  setActive(-1);

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());

  return {
    set: (v) => { stag = clamp(v, 0, 120); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "c2-case",
  means: "Кейс как папка на кольцах: задача, исследование, решения, тест и итог; страница под указателем встаёт.",
  rules: [1, 2, 6, 10],
  range: [0, 45, 90],
  tour: [[110, 150], [205, 110], [300, 170], null],
  mount,
});
