/**
 * S6 screens: a slotted rack holding five phones upright like books, each
 * showing a different kind of screen (splash, onboarding, list, card, form).
 * The phone under the pointer slides up out of its slot; its neighbours rise
 * a little, staggered outwards. The slider is the stagger, in ms.
 */
const {
  Cam, clamp, fillet, fit, poly, proj, rad, rings, prism, facing, seg,
  tdone, tset, tval, tween, disposer, mk, place, pointer, put, register, solid,
} = HL;

const N = 5, W = 34, H = 62, TK = 2.6, G = 30, LEAN = -7, RH = 13, LIFT = 34;
const REST = [0, 5, 13, 2, 0], NEAR = [1, 0.2, 0.06];
const NAMES = ["заставка", "онбординг", "список", "карточка", "форма"];
const yOf = (i) => (N - 1 - i) * G + 8; // phone 0 stands in front, on the left

/** A rounded rectangle in the phone's own (u, v) plane, v up. */
const box = (u0, v0, u1, v1, r) => fillet([[u0, v0], [u1, v0], [u1, v1], [u0, v1]], [r, r, r, r]);
/** A circle in the phone's plane. */
const disc = (cu, cv, r) => Array.from({ length: 20 }, (_, k) => [cu + r * Math.cos(k * Math.PI / 10), cv + r * Math.sin(k * Math.PI / 10)]);

/** What each screen holds: shapes in its plane as [points, closed], and page dots as [u, v, cls]. */
function layout(i) {
  const L = [], D = [], line = (v, u0 = 6, u1 = W - 6) => L.push([[[u0, v], [u1, v]], false]);
  if (i === 0) { L.push([disc(W / 2, H / 2 + 2, 6.5), true]); L.push([disc(W / 2, H / 2 + 2, 3), true]); }
  if (i === 1) { L.push([box(6, 27, W - 6, 50, 2.5), true]); line(21, 9, W - 9); D.push([W / 2 - 4, 14, "dot m"], [W / 2, 14, "dot off"], [W / 2 + 4, 14, "dot off"]); }
  if (i === 2) for (let k = 0; k < 5; k++) { const v = 48 - k * 7.4; L.push([box(5.5, v - 2, 9.5, v + 2, 0.8), true]); line(v, 12, W - 6); }
  if (i === 3) { L.push([box(5, 29, W - 5, 51, 2.5), true]); line(24); line(20, 6, W - 13); L.push([box(5.5, 10, W - 5.5, 15, 2.4), true]); }
  if (i === 4) { for (let k = 0; k < 3; k++) L.push([box(5, 44 - k * 9, W - 5, 49 - k * 9, 1.5), true]); L.push([box(11, 11, W - 11, 16, 2.4), true]); }
  return { L, D };
}

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let stag = value;
  const s = Math.sin(rad(LEAN)), c = Math.cos(rad(LEAN));
  const X0 = -7, X1 = W + 7, Y0 = 0, Y1 = yOf(0) + 9;

  const C = Cam(45, 0.5, 1.9);
  fit(C, [[X0, Y0, -6], [X1, Y1, -6], [X1, Y0, -6], [X0, Y1, -6], [0, yOf(N - 1) + H * s, H * c + LIFT], [W, yOf(0) + H * s, H * c + LIFT]], 200, 170);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  const [br, bi] = rings(X0, Y0, X1, Y1, 6, 1.8);
  put(solid(g), prism(P, front, br, bi, -6, 0));
  /** One block of the rack, between two slots. */
  const block = (y0, y1) => { const [r, n] = rings(X0 + 2, y0, X1 - 2, y1, 3, 1.2); put(solid(g), prism(P, front, r, n, 0, RH)); };
  const outline = box(0, 0, W, H, 5), glass = box(2.3, 7, W - 2.3, H - 7, 1.6);

  const phones = [];
  for (let i = N - 1; i >= 0; i--) {
    const yb = yOf(i);
    block(i === N - 1 ? Y0 + 2 : yOf(i + 1) + 1.5, yb - TK - 1.5);
    const grp = mk("g", {}, g);
    const back = mk("path", { class: "lo" }, grp), face = mk("path", { class: "sil" }, grp);
    const det = mk("path", { class: "nf lo" }, grp), lay = mk("path", { class: "nf" }, grp);
    const { L, D } = layout(i);
    const dots = D.map((d) => mk("circle", { r: 0.9, class: d[2] }, grp));
    phones[i] = { yb, grp, back, face, det, lay, L, D, dots, z: tween(REST[i]), drawn: NaN };
  }
  block(yOf(0) + 1.5, Y1 - 2);

  function draw(i, lift) {
    const ph = phones[i];
    if (lift === ph.drawn) return;
    ph.drawn = lift;
    const w = (u, v) => P(u, ph.yb + v * s, v * c + lift);
    const wb = (u, v) => P(u, ph.yb + v * s - TK * c, v * c + TK * s + lift);
    ph.back.setAttribute("d", poly(outline.map((p) => wb(p[0], p[1]))));
    ph.face.setAttribute("d", poly(outline.map((p) => w(p[0], p[1]))));
    // the glass, the speaker slot and the home button
    ph.det.setAttribute("d", poly(glass.map((p) => w(p[0], p[1]))) + seg(w(W / 2 - 4, H - 3.5), w(W / 2 + 4, H - 3.5)) + poly(disc(W / 2, 3.5, 1.9).map((p) => w(p[0], p[1]))));
    ph.lay.setAttribute("d", ph.L.map(([pts, closed]) => (closed ? poly : (q) => seg(q[0], q[1]))(pts.map((p) => w(p[0], p[1])))).join(""));
    ph.dots.forEach((el, k) => place(el, w(ph.D[k][0], ph.D[k][1])));
  }

  const B = register(stage, (_dt, now) => {
    let moving = false;
    phones.forEach((ph, i) => { draw(i, tval(ph.z, now)); if (!tdone(ph.z, now)) moving = true; });
    return moving;
  });
  bag.add(B.unregister);

  // hit: the phone whose RESTING centre is nearest the pointer's x, inside a fixed band
  const mid = phones.map((ph, i) => P(W / 2, ph.yb + (H / 2) * s, (H / 2) * c + REST[i]));
  const half = (mid[1][0] - mid[0][0]) / 2 + 4;
  const yTop = P(W / 2, yOf(N - 1) + H * s, H * c + LIFT)[1] - 6, yBot = P(X1, Y1, -6)[1];
  function hit([x, y]) {
    if (y < yTop || y > yBot) return -1;
    let best = -1, bd = 1e9;
    mid.forEach((m, i) => { const d = Math.abs(x - m[0]); if (d < bd) { bd = d; best = i; } });
    return bd <= half + 6 ? best : -1;
  }

  let act = -1;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = a >= 0 ? a : act;
    act = a;
    phones.forEach((ph, i) => {
      const d = Math.abs(i - from);
      tset(ph.z, a < 0 ? REST[i] : LIFT * NEAR[clamp(Math.abs(i - a), 0, 2)], now, d * stag);
      ph.face.classList.toggle("hi", a < 0 ? i === 2 : i === a);
    });
    read.textContent = a < 0 ? "rest" : NAMES[a];
    B.wake();
  }
  phones[2].face.classList.add("hi");

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());
  return { set: (v) => { stag = v; }, destroy: bag.dispose };
}

hairline({
  name: "s6-screens",
  means: "Пять телефонов в подставке, у каждого свой тип экрана: тот, что под указателем, выезжает вверх.",
  rules: [1, 2, 5, 10],
  range: [0, 45, 90],
  tour: [[150, 150], [215, 120], [270, 90], null],
  mount,
});
