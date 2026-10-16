/**
 * Brief: a card-file box with its lid swung open behind it, holding six index
 * cards. Each card's tab carries as many dots as its point's number, the
 * first card in front. The card under the pointer stands up and lifts; those
 * in front of it lean forward, those behind lean back, staggered outwards
 * from it. The slider is the lift.
 */
const {
  Cam, clamp, facing, fillet, fit, hull, open, poly, proj, rad, ringAt, rrect, run, seg,
  tdone, tset, tval, tween, disposer, mk, place, pointer, register,
} = HL;

const N = 6, W = 64, H = 42, G = 10, TW = 18, TH = 7, TABS = [5, 23, 41];
const REST = -14, BACK = -26, FWD = 15, LMAX = 24;
const X0 = -5, X1 = W + 5, Y0 = -9, Y1 = (N - 1) * G + 9, WH = 24, WR = 5, WT = 2.4, LD = 44, LA = 28;
const CAM_S = 1.9;
const lidTop = [Y0 - LD * Math.sin(rad(LA)), WH + LD * Math.cos(rad(LA))];
const CAM_FIT = [[X0, Y0, 0], [X1, Y1, 0], [X1, Y0, 0], [X0, Y1, 0], [X0, lidTop[0], lidTop[1]], [X1, lidTop[0], lidTop[1]], [X1, 0, H + TH + LMAX]];

const LR = (pts) => (pts[0][0] <= pts[pts.length - 1][0] ? pts : pts.slice().reverse());

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let L = value;
  const C = Cam(45, 0.5, CAM_S);
  fit(C, CAM_FIT, 200, 166);
  const P = proj(C), front = facing(C);
  const outer = rrect(X0, Y0, X1, Y1, WR, 6), inner = rrect(X0 + WT, Y0 + WT, X1 - WT, Y1 - WT, WR - WT, 6);
  const g = mk("g", {}, svg);

  // the lid, hinged on the back edge and swung open past upright; its thickness first
  const lidShape = fillet([[X0, 0], [X1, 0], [X1, LD], [X0, LD]], [1, 1, 4, 4]);
  const lid = (d) => (p) => P(p[0], Y0 - p[1] * Math.sin(rad(LA)) - d * Math.cos(rad(LA)), WH + p[1] * Math.cos(rad(LA)) - d * Math.sin(rad(LA)));
  mk("path", { class: "lo", d: poly(lidShape.map(lid(2.4))) }, g);
  mk("path", { class: "sil", d: poly(lidShape.map(lid(0))) }, g);
  mk("path", { class: "nf lo", d: poly(rrect(X0 + 5, 6, X1 - 5, LD - 5, 3, 4).map((q) => lid(0)([q.u, q.v]))) }, g);

  // the box's far half: body, rim, floor seam along the far walls
  mk("path", { class: "sil", d: poly(hull(ringAt(P, outer, 0).concat(ringAt(P, outer, WH)))) }, g);
  mk("path", { class: "nf", d: poly(ringAt(P, inner, WH)) }, g);
  mk("path", { class: "nf lo", d: open(ringAt(P, run(inner, (q) => !front(q)), 2.5)) }, g);

  const cards = [];
  for (let i = 0; i < N; i++) {
    const n = N - i, t0 = TABS[(N - 1 - i) % 3];
    const shape = fillet([[0, 0], [W, 0], [W, H], [t0 + TW, H], [t0 + TW, H + TH], [t0, H + TH], [t0, H], [0, H]], [1, 1, 3, 1.6, 2.2, 2.2, 1.6, 3]);
    const grp = mk("g", {}, g);
    const back = mk("path", { class: "lo" }, grp), face = mk("path", { class: "sil" }, grp), lines = mk("path", { class: "nf lo" }, grp);
    const dots = [];
    for (let k = 0; k < n; k++) dots.push(mk("circle", { r: 1.05, class: "dot m" }, grp));
    cards.push({ n, t0, shape, back, face, lines, dots, a: tween(REST), z: tween(0) });
  }

  // the near half: one opaque piece from the rim down to the floor, and a label frame on the front
  const iF = LR(ringAt(P, run(inner, front), WH)), oT = LR(ringAt(P, run(outer, front), WH)), oB = LR(ringAt(P, run(outer, front), 0));
  mk("path", { class: "fo", d: poly([...iF, oT[oT.length - 1], ...oB.slice().reverse(), oT[0]]) }, g);
  mk("path", { class: "nf lo", d: open(oT) }, g);
  mk("path", { class: "nf", d: open(iF) }, g);
  mk("path", { class: "nf sil", d: open([oT[0], ...oB, oT[oT.length - 1]]) }, g);
  const onFront = (r) => poly(r.map((q) => P(q.u, Y1, q.v)));
  const hx = (X0 + X1) / 2;
  mk("path", { class: "nf", d: onFront(rrect(hx - 13, 9, hx + 13, 17, 2, 4)) }, g);
  mk("path", { class: "nf lo", d: onFront(rrect(hx - 11, 10.5, hx + 11, 15.5, 1, 4)) }, g);

  function draw(i, th, lift) {
    const cd = cards[i], yb = i * G, s = Math.sin(rad(th)), c = Math.cos(rad(th));
    const w = (u, v) => P(u, yb + v * s, v * c + lift);
    cd.back.setAttribute("d", poly(cd.shape.map((p) => P(p[0], yb + p[1] * s - 1.3 * c, p[1] * c + 1.3 * s + lift))));
    cd.face.setAttribute("d", poly(cd.shape.map((p) => w(p[0], p[1]))));
    cd.lines.setAttribute("d", seg(w(5, H - 9), w(W - 5, H - 9)) + [H - 16, H - 22, H - 28].map((v) => seg(w(5, v), w(W - 18, v))).join(""));
    cd.dots.forEach((el, k) => place(el, w(cd.t0 + TW / 2 + (k - (cd.n - 1) / 2) * 2.6, H + TH / 2)));
  }

  const B = register(stage, (_dt, now) => {
    let moving = false;
    cards.forEach((cd, i) => { draw(i, tval(cd.a, now), tval(cd.z, now)); if (!tdone(cd.a, now) || !tdone(cd.z, now)) moving = true; });
    return moving;
  });
  bag.add(B.unregister);

  // hit bands along the RESTING top edges; they never move
  const top = (i) => P(W / 2, i * G + H * Math.sin(rad(REST)), H * Math.cos(rad(REST)));
  const c0 = top(0), c1 = top(1), d = [c1[0] - c0[0], c1[1] - c0[1]];
  const px0 = P(0, 0, 0), px1 = P(1, 0, 0), ex = [px1[0] - px0[0], px1[1] - px0[1]];
  const HALF = W / 2 + 6, det = d[0] * ex[1] - d[1] * ex[0];
  function hit([x, y]) {
    const qx = x - c0[0], qy = y - c0[1];
    const s = (qx * ex[1] - qy * ex[0]) / det, r = (d[0] * qy - d[1] * qx) / det;
    if (Math.abs(r) > HALF || s < -0.6 || s > N + 1.5) return -1;
    return clamp(Math.round(s), 0, N - 1);
  }

  let act = -1;
  function setActive(a, force) {
    if (a === act && !force) return;
    const now = performance.now(), from = a >= 0 ? a : act;
    act = a;
    cards.forEach((cd, i) => {
      const delay = from < 0 ? 0 : Math.abs(i - from) * 45;
      tset(cd.a, a < 0 ? REST : i < a ? BACK : i > a ? FWD : 0, now, delay);
      tset(cd.z, a === i ? L : 0, now, delay);
      cd.face.classList.toggle("hi", i === a);
      const on = a < 0 ? i === N - 1 : i === a;
      cd.dots.forEach((el) => el.setAttribute("class", on ? "dot" : "dot m"));
    });
    read.textContent = a < 0 ? "rest" : "пункт " + cards[a].n;
    B.wake();
  }
  setActive(-1, true);

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());
  return { set: (v) => { L = v; if (act >= 0) setActive(act, true); }, destroy: bag.dispose };
}

hairline({
  name: "s5-brief",
  means: "Бриф из шести пунктов лежит как карточки в ящике, и карточка под курсором встаёт.",
  rules: [1, 2, 6, 10],
  range: [8, 16, 24],
  tour: [[153, 174], [193, 154], [220, 140], null],
  mount,
});
