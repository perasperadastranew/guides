/**
 * R2 compare: three competitor phones lie side by side on a tray, and behind
 * each stands a row of five pillars, its scores on five criteria. The pointer
 * picks a criterion, a row across all three: those pillars rise together,
 * spreading out from the column under the pointer, and take the bright edge.
 * The slider is the stagger, in ms.
 */
const {
  Cam, clamp, facing, fit, prism, proj, rings, rrect, ringAt, unproj, poly, seg,
  tdone, tset, tval, tween, disposer, mk, pointer, put, register, solid,
} = HL;

const COLS = 3, ROWS = 5, CW = 42, PW = 30, PL = 56, PT = 3, FOOT = 10, PITCH = 12.5, LIFT = 30, PB = 5;
const Y_PH = ROWS * PITCH + 6; // the phones lie in front of the pillars
const SCORE = [[22, 14, 30, 9, 18], [12, 26, 16, 24, 8], [28, 10, 20, 15, 32]]; // [column][criterion]
const cx = (c) => c * CW + PW / 2;
const cy = (k) => Y_PH - 6 - (k + 0.5) * PITCH; // criterion 1 sits nearest the phones

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let stag = value;
  const X0 = -6, X1 = (COLS - 1) * CW + PW + 6, Y0 = -4, Y1 = Y_PH + PL + 6;
  const C = Cam(45, 0.5, 1.62);
  fit(C, [[X0, Y0, -PB], [X1, Y1, -PB], [X1, Y0, -PB], [X0, Y1, -PB], [cx(2), cy(4), 32 + LIFT], [cx(0), cy(4), 32 + LIFT]], 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  const [tr, ti] = rings(X0, Y0, X1, Y1, 8, 2);
  put(solid(g), prism(P, front, tr, ti, -PB, 0));

  // pillars, diagonal by diagonal from the far corner
  const pil = [];
  const order = [];
  for (let c = 0; c < COLS; c++) for (let k = 0; k < ROWS; k++) order.push([c, k]);
  order.sort((a, b) => (cx(a[0]) + cy(a[1])) - (cx(b[0]) + cy(b[1])));
  for (const [c, k] of order) {
    const x = cx(c), y = cy(k), [ring, inner] = rings(x - FOOT / 2, y - FOOT / 2, x + FOOT / 2, y + FOOT / 2, 2.4, 0.9);
    pil.push({ c, k, x, y, h0: SCORE[c][k], ring, inner, z: tween(SCORE[c][k]), el: solid(g), drawn: NaN });
  }

  // the phones, lying flat: a slab, its glass, a speaker slot and a home button
  for (let c = 0; c < COLS; c++) {
    const x0 = c * CW, [r, n] = rings(x0, Y_PH, x0 + PW, Y_PH + PL, 5, 1);
    put(solid(g), prism(P, front, r, n, 0, PT));
    const glass = rrect(x0 + 2.4, Y_PH + 7, x0 + PW - 2.4, Y_PH + PL - 7, 1.6, 4);
    mk("path", { d: poly(ringAt(P, glass, PT)), class: "nf lo" }, g);
    mk("path", { d: seg(P(x0 + PW / 2 - 4, Y_PH + 3.5, PT), P(x0 + PW / 2 + 4, Y_PH + 3.5, PT)), class: "nf lo" }, g);
    mk("path", { d: poly(ringAt(P, rrect(x0 + PW / 2 - 2, Y_PH + PL - 5.5, x0 + PW / 2 + 2, Y_PH + PL - 1.5, 2, 3), PT)), class: "nf lo" }, g);
    // a few rows of content on each screen, different per competitor
    const rows = [[14, 22, 30, 38], [16, 28, 40], [13, 19, 25, 31, 37, 43]][c];
    mk("path", { d: rows.map((v) => seg(P(x0 + 7, Y_PH + v, PT), P(x0 + PW - 7, Y_PH + v, PT))).join(""), class: "nf lo" }, g);
  }

  const best = pil.reduce((a, b) => (b.h0 > a.h0 ? b : a));
  function draw(p, h) {
    if (h === p.drawn) return;
    p.drawn = h;
    put(p.el, prism(P, front, p.ring, p.inner, 0, h));
  }
  const B = register(stage, (_dt, now) => {
    let m = false;
    for (const p of pil) { draw(p, tval(p.z, now)); if (!tdone(p.z, now)) m = true; }
    return m;
  });
  bag.add(B.unregister);

  // hit: each pillar's REST top, unprojected at its own rest height; the nearest wins
  function hit([sx, sy]) {
    let bestP = null, bd = 1e9;
    for (const p of pil) {
      for (const z of [p.h0, p.h0 / 2]) {
        const w = unproj(C, sx, sy, z), d = Math.max(Math.abs(w[0] - p.x), Math.abs(w[1] - p.y));
        if (d < bd) { bd = d; bestP = p; }
      }
    }
    return bd <= PITCH * 0.75 ? bestP : null;
  }

  let act = -1;
  function setActive(p) {
    const a = p ? p.k : -1, from = p ? p.c : 1;
    if (a === act) return;
    const now = performance.now();
    act = a;
    for (const q of pil) {
      tset(q.z, a < 0 ? q.h0 : q.k === a ? q.h0 + LIFT : Math.max(4, q.h0 * 0.55), now, (Math.abs(q.c - from) + (q.k === a ? 0 : 0.5)) * stag);
      q.el.sil.classList.toggle("hi", a < 0 ? q === best : q.k === a);
    }
    read.textContent = a < 0 ? "rest" : "критерий " + (a + 1);
    B.wake();
  }
  best.el.sil.classList.add("hi");

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(null) }));
  bag.add(() => svg.replaceChildren());
  return { set: (v) => { stag = clamp(v, 0, 200); }, destroy: bag.dispose };
}

hairline({
  name: "r2-compare",
  means: "Три телефона конкурентов и за каждым пять столбиков-оценок: указатель выбирает критерий, и его ряд поднимается у всех трёх.",
  rules: [1, 2, 4, 10],
  range: [0, 50, 100],
  tour: [[150, 150], [230, 110], [260, 165], null],
  mount,
});
