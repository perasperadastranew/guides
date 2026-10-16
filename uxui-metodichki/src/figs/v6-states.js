/**
 * States: a phone standing on a desk stand, its screen showing one button,
 * and behind it a slotted holder of four plates, each the same button in
 * another state: plain, pressed (an inner pill), loading (three dots) and
 * error (a line under it). The plate under the pointer slides up out of its
 * slot and stands straight; the plates in front of it lean forward and the
 * ones behind lean back, staggered outwards. At rest the phone's button is
 * bright. The slider is how far the plate slides up.
 */
const {
  Cam, fit, proj, facing, prism, rings, rrect, ringAt, poly, seg, clamp, rad,
  place, tween, tset, tval, tdone, mk, solid, put, pointer, register, disposer,
} = HL;

const N = 4, W = 56, H = 32, G = 10, HX = 66, HH = 9, TK = 1.4, STEP = 45;
const REST = [-15, -11, -8, -5], BACK = -22, FWD = 14;
const NAMES = ["ошибка", "загрузка", "нажато", "обычное"];
const PX = 18, PW = 40, PH = 74, PY = 62, PZ = 7, PLEAN = -12;

/** A ring of (u, v) samples drawn in an upright plane through w. */
const flat = (w, ring) => poly(ring.map((q) => w(q.u, q.v)));

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let LIFT = value;

  const C = Cam(45, 0.5, 1.82);
  fit(C, [[PX - 4, PY - 8, 0], [PX + PW + 4, PY + 10, 0], [HX - 6, -6, 0], [HX + W + 6, (N - 1) * G + 6, 0],
    [HX + W, 0, HH + H + 26], [HX, 0, HH + H + 26], [PX, PY - 15, PZ + PH]], 200, 166);
  const P = proj(C), front = facing(C);
  const g = mk("g", {}, svg);

  // the holder: a block whose top has a groove for each plate
  const [hr, hi] = rings(HX - 6, -6, HX + W + 6, (N - 1) * G + 6, 5, 1.6);
  put(solid(g), prism(P, front, hr, hi, 0, HH));
  mk("path", { d: [0, 1, 2, 3].map((i) => seg(P(HX, i * G - 1.5, HH), P(HX + W, i * G - 1.5, HH))).join(""), class: "nf lo" }, g);

  const face = rrect(0, 0, W, H, 4, 4), pill = rrect(10, 11, 40, 21, 5, 4);
  const plates = REST.map((r0, i) => {
    const grp = mk("g", {}, g);
    const back = mk("path", { class: "lo" }, grp), fc = mk("path", { class: "sil" }, grp);
    const pl = mk("path", { class: "nf" }, grp), mark = mk("path", { class: "nf lo" }, grp);
    const dots = i === 1 ? [0, 1, 2].map(() => mk("ellipse", { rx: 1.3, ry: 1.3, class: "dot off" }, grp)) : [];
    return { i, r0, back, fc, pl, mark, dots, a: tween(r0), z: tween(0), drawn: "" };
  });

  function draw(p, th, lift) {
    const key = th + "," + lift;
    if (key === p.drawn) return;
    p.drawn = key;
    const yb = p.i * G, s = Math.sin(rad(th)), c = Math.cos(rad(th));
    const w = (u, v) => P(HX + u, yb + v * s, HH + v * c + lift);
    const wb = (u, v) => P(HX + u, yb + v * s - TK * c, HH + v * c + TK * s + lift);
    p.back.setAttribute("d", poly(face.map((q) => wb(q.u, q.v))));
    p.fc.setAttribute("d", flat(w, face));
    p.pl.setAttribute("d", flat(w, pill));
    if (p.i === 0) p.mark.setAttribute("d", seg(w(10, 6), w(32, 6)));
    if (p.i === 2) p.mark.setAttribute("d", flat(w, rrect(12.5, 13, 37.5, 19, 3, 4)));
    p.dots.forEach((el, k) => { place(el, w(19 + k * 6, 16)); });
  }

  // the phone on its stand: a base, the phone leaning back, then the lip that holds its foot
  const [sr, si] = rings(PX - 4, PY - 8, PX + PW + 4, PY + 10, 5, 1.6);
  put(solid(g), prism(P, front, sr, si, 0, PZ));
  const ps = Math.sin(rad(PLEAN)), pc = Math.cos(rad(PLEAN));
  const pw = (u, v) => P(PX + u, PY + v * ps, PZ + v * pc);
  const pb = (u, v) => P(PX + u, PY + v * ps - 2.4 * pc, PZ + v * pc + 2.4 * ps);
  const body = rrect(0, 0, PW, PH, 7, 5);
  mk("path", { d: poly(body.map((q) => pb(q.u, q.v))), class: "lo" }, g);
  mk("path", { d: flat(pw, body), class: "sil" }, g);
  mk("path", { d: flat(pw, rrect(3, 4, PW - 3, PH - 4, 4.5, 5)), class: "nf lo" }, g);
  mk("path", { d: seg(pw(15, PH - 2), pw(25, PH - 2)) + flat(pw, rrect(7, 46, PW - 7, 64, 2, 3)), class: "nf lo" }, g);
  const btn = mk("path", { d: flat(pw, rrect(8, 12, PW - 8, 20, 4, 4)), class: "nf hi" }, g);
  const [lr, li] = rings(PX - 2, PY + 2, PX + PW + 2, PY + 7, 2.4, 1);
  put(solid(g), prism(P, front, lr, li, PZ, PZ + 5));

  const B = register(stage, (_dt, now) => {
    let m = false;
    for (const p of plates) { draw(p, tval(p.a, now), tval(p.z, now)); if (!tdone(p.a, now) || !tdone(p.z, now)) m = true; }
    return m;
  });
  bag.add(B.unregister);

  // hit bands along the RESTING top edges of the plates; they never move
  const top = (i) => P(HX + W / 2, i * G + H * Math.sin(rad(REST[i])), HH + H * Math.cos(rad(REST[i])));
  const c0 = top(0), c1 = top(N - 1), d = [(c1[0] - c0[0]) / (N - 1), (c1[1] - c0[1]) / (N - 1)];
  const e0 = P(0, 0, 0), e1 = P(1, 0, 0), ex = [e1[0] - e0[0], e1[1] - e0[1]], det = d[0] * ex[1] - d[1] * ex[0];
  function hit([x, y]) {
    const qx = x - c0[0], qy = y - c0[1];
    const s = (qx * ex[1] - qy * ex[0]) / det, r = (d[0] * qy - d[1] * qx) / det;
    if (Math.abs(r) > W / 2 + 4 || s < -0.6 || s > N + 0.8) return -1;
    return clamp(Math.round(s), 0, N - 1);
  }

  let act = -1;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = a >= 0 ? a : act >= 0 ? act : 0;
    act = a;
    plates.forEach((p, i) => {
      const delay = Math.abs(i - from) * STEP;
      tset(p.a, a < 0 ? p.r0 : i < a ? BACK : i > a ? FWD : 0, now, delay);
      tset(p.z, i === a ? LIFT : 0, now, delay);
      p.fc.classList.toggle("hi", i === a);
    });
    btn.classList.toggle("hi", a < 0);
    read.textContent = a < 0 ? "rest" : NAMES[a];
    B.wake();
  }
  read.textContent = "rest";

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());

  return {
    set: (v) => { LIFT = v; const a = act; act = -2; setActive(a); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "v6-states",
  means: "Телефон на подставке и четыре пластины с одной кнопкой в разных состояниях: пластина под указателем выезжает вверх.",
  rules: [1, 2, 4, 9],
  range: [10, 18, 26],
  tour: [[280, 148], [249, 163], [234, 174], null],
  mount,
});
