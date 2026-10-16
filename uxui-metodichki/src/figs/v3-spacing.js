/**
 * Spacing: four interface blocks (an avatar, a text card, a picture, a button)
 * standing on a ruler with a tick dot every 8 units. At rest the gaps are
 * uneven. The pointer's x picks a step of the scale (8, 16, 24, 32) and the
 * blocks move to it, one after another from the anchored first block; the dots
 * inside the gaps count the step. The slider is the stagger, in ms.
 */
const {
  Cam, clamp, facing, fit, open, poly, prism, proj, ringAt, rings, rrect,
  tdone, tset, tval, tween, mk, pointer, put, register, disposer, solid,
} = HL;

const X0 = 4, RL = 208, Y0 = 4, Y1 = 20, RZ = 5, CELL = 8, NC = 25;
const BW = [24, 16, 40, 24], BH = [16, 26, 20, 9], REST = [11, 21, 5];
const STEPS = [8, 16, 24, 32];

/** Where each block starts along the ruler for a list of three gaps. */
const lay = (gaps) => { const xs = []; let x = X0; BW.forEach((w, i) => { xs.push(x); x += w + (gaps[i] || 0); }); return xs; };

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let stag = value;
  const C = Cam(45, 0.5, 1.64);
  fit(C, [[-2, -2, 0], [RL + 2, 26, 0], [RL + 2, -2, 0], [-2, 26, 0], [X0, Y0, RZ + 26], [RL, Y0, RZ + 26]], 200, 172);
  const P = proj(C), front = facing(C);
  const flat = (x0, y0, x1, y1, r, z) => poly(ringAt(P, rrect(x0, y0, x1, y1, r, 4), z));

  const g = mk("g", {}, svg);
  // the ruler: a long rounded bar with its tick dots along the near edge
  const [rr, ri] = rings(-2, -2, RL + 2, 26, 4, 1.4);
  put(solid(g), prism(P, front, rr, ri, 0, RZ));
  mk("path", { d: open([P(RL + 2, 6, RZ * 0.5), P(RL + 2, 18, RZ * 0.5)]), class: "nf lo" }, g);

  const blocks = BW.map((w, i) => ({ i, w, h: BH[i], el: solid(g), top: mk("path", { class: "nf lo" }, g), x: tween(lay(REST)[i]), drawn: NaN }));
  const dots = [];
  for (let k = 0; k < NC; k++) {
    const el = mk("circle", { r: 1.25, class: "dot off" }, g), p = P(X0 + k * CELL + CELL / 2, 23, RZ);
    el.setAttribute("cx", p[0]); el.setAttribute("cy", p[1]);
    dots.push(el);
  }

  /** What each block carries on its top: an avatar's face ring, a card's lines, a picture's horizon, a button's label. */
  function marks(b, x) {
    const z = RZ + b.h, x1 = x + b.w;
    if (b.i === 0) return flat(x + 5, Y0 + 3, x1 - 5, Y1 - 3, 6, z);
    if (b.i === 1) return [7, 10, 13].map((y) => open([P(x + 4, y, z), P(x1 - 4, y, z)])).join("");
    if (b.i === 2) return flat(x + 3, Y0 + 3, x1 - 3, Y1 - 3, 2, z) + open([P(x + 6, Y1 - 5, z), P(x + 16, Y0 + 6, z), P(x + 24, Y1 - 8, z), P(x1 - 6, Y0 + 5, z)]);
    return flat(x + 6, Y0 + 5.5, x1 - 6, Y1 - 5.5, 2.5, z);
  }
  function draw(b, x) {
    if (x === b.drawn) return;
    b.drawn = x;
    const [ring, inner] = rings(x, Y0, x + b.w, Y1, b.i === 0 ? 8 : b.i === 3 ? 7 : 3, 1.2);
    put(b.el, prism(P, front, ring, inner, RZ, RZ + b.h));
    b.top.setAttribute("d", marks(b, x));
  }

  const B = register(stage, (_dt, now) => {
    let m = false;
    for (const b of blocks) { draw(b, tval(b.x, now)); if (!tdone(b.x, now)) m = true; }
    return m;
  });
  bag.add(B.unregister);

  /** The dots inside a gap count it; the first gap's are bright at rest, every gap's when a step is chosen. */
  function paint(gaps, chosen) {
    const xs = lay(gaps);
    dots.forEach((el, k) => {
      const cx = X0 + k * CELL + CELL / 2;
      let cls = "dot off";
      for (let i = 0; i < 3; i++) if (cx > xs[i] + BW[i] && cx < xs[i + 1]) cls = chosen || i === 0 ? "dot" : "dot m";
      el.setAttribute("class", cls);
    });
  }

  let act = -2;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), gaps = a < 0 ? REST : [STEPS[a], STEPS[a], STEPS[a]], xs = lay(gaps);
    act = a;
    blocks.forEach((b) => tset(b.x, xs[b.i], now, b.i * stag));
    paint(gaps, a >= 0);
    read.textContent = a < 0 ? "rest" : STEPS[a] + " pt";
    B.wake();
  }
  setActive(-1);

  // hit test: the pointer's screen x across the ruler's fixed span, in four equal zones
  const A = P(X0, 12, RZ), Bp = P(RL, 12, RZ), dx = Bp[0] - A[0], dy = Bp[1] - A[1], len = Math.hypot(dx, dy);
  const hit = ([sx, sy]) => {
    const off = Math.abs(dx * (sy - A[1]) - dy * (sx - A[0])) / len;
    return off > 58 || sx < A[0] - 16 || sx > Bp[0] + 16 ? -1 : clamp(Math.floor(((sx - A[0]) / dx) * 4), 0, 3);
  };
  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());

  return { set: (v) => { stag = v; }, destroy: bag.dispose };
}

hairline({
  name: "v3-spacing",
  means: "Четыре блока на линейке: курсор выбирает шаг отступа, и блоки встают на одинаковое расстояние, кратное восьми.",
  rules: [1, 2, 5, 8],
  range: [20, 45, 70],
  tour: [[96, 131], [226, 196], [307, 237], null],
  mount,
});
