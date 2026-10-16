/**
 * iOS: an iPhone lying flat, its screen exploded into five thin layers that
 * climb from the home indicator up to the status bar: status bar with the
 * island, navigation bar with its large title, content rows, tab bar with four
 * tabs, the indicator pill. Pointer x scrubs the explode gap on a spring;
 * pointer y picks a layer, which takes the bright edge. The slider is the
 * largest gap.
 */
const {
  Cam, clamp, facing, fit, open, poly, prism, proj, rings, ringAt, rrect, seg,
  spring, stepS, disposer, mk, pointer, put, register, solid,
} = HL;

const L = 96, W = 46, BT = 5, LT = 1.6, Z0 = BT + 1;
const NAMES = ["статус-бар", "навбар", "контент", "таб-бар", "индикатор"];
// Each layer: its footprint along the phone [x0, x1, y0, y1], and its marks [x0, y0, x1, y1, r, class].
const LAYERS = [
  { f: [4, 11, 4, W - 4], marks: [[6, 17, 9, 29, 1.5, "nf"], [6, 33, 9, 39, 1.2, "nf lo"], [6.5, 7, 8.5, 12, 1, "nf lo"]] },
  { f: [12.5, 27, 4, W - 4], marks: [[19, 7, 25, 29, 2.2, "nf"], [14, 36, 17, 40, 1.5, "nf lo"]] },
  { f: [28.5, 71.5, 4, W - 4], marks: [0, 1, 2].flatMap((r) => [[31 + r * 13.5, 7, 40 + r * 13.5, 16, 2.2, "nf lo"], [32 + r * 13.5, 19, 35 + r * 13.5, 38, 1.4, "nf lo"], [37 + r * 13.5, 19, 40 + r * 13.5, 31, 1.4, "nf lo"]]) },
  { f: [73, 84, 4, W - 4], marks: [0, 1, 2, 3].map((t) => [76.5, 8 + t * 9, 80.5, 12 + t * 9, 2, "nf lo"]) },
  { f: [87, 90.5, 15, 31], marks: [] },
];
const REST_LAYER = 1;

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let GMAX = value;
  const zOf = (k, g) => Z0 + g * (4 - k);

  const C = Cam(45, 0.5, 2.6);
  fit(C, [[0, 0, 0], [L, W, 0], [L, 0, 0], [0, W, 0], [4, 4, zOf(0, 13) + LT], [4, W - 4, zOf(0, 13) + LT]], 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  // The body: a slab with rounded corners, its screen recess, and the side buttons as short ridges.
  const [br, bi] = rings(0, 0, L, W, 11, 1.6);
  put(solid(g), prism(P, front, br, bi, 0, BT));
  mk("path", { class: "nf lo", d: poly(ringAt(P, rrect(2.5, 2.5, L - 2.5, W - 2.5, 9, 6), BT)) }, g);
  mk("path", { class: "nf", d: seg(P(18, W, 1.5), P(26, W, 1.5)) + seg(P(30, W, 1.5), P(38, W, 1.5)) }, g);

  const layers = LAYERS.map((ly, k) => {
    const [x0, x1, y0, y1] = ly.f, r = k === 4 ? 1.7 : 3;
    const [ring, inner] = rings(x0, y0, x1, y1, r, k === 4 ? 0.5 : 0.9);
    const guide = mk("path", { class: "nf dash" }, g);
    const el = solid(g);
    const marks = ly.marks.map(([a, b, c, d, rr, cls]) => ({ ring: rrect(a, b, c, d, rr, 4), el: mk("path", { class: cls }, el.g) }));
    return { x0, x1, y0, y1, ring, inner, guide, el, marks };
  });

  const gap = spring(GMAX * 0.45);
  let drawn = NaN;
  function draw() {
    if (gap.x === drawn) return;
    drawn = gap.x;
    const gg = Math.max(0, gap.x);
    layers.forEach((ly, k) => {
      const z = zOf(k, gg), t = z + LT;
      // a dashed drop from the layer's left corner to where it sits on the screen
      ly.guide.setAttribute("d", z - Z0 > 1 ? open([P(ly.x0 + 1, ly.y1 - 1, z), P(ly.x0 + 1, ly.y1 - 1, BT)]) : "");
      put(ly.el, prism(P, front, ly.ring, ly.inner, z, t));
      ly.marks.forEach((m) => m.el.setAttribute("d", poly(ringAt(P, m.ring, t))));
    });
  }

  const B = register(stage, (dt) => { const m = stepS(gap, dt); draw(); return m; });
  bag.add(B.unregister);

  let act = -2;
  function setActive(a) {
    if (a === act) return;
    act = a;
    layers.forEach((ly, k) => ly.el.sil.classList.toggle("hi", k === (a < 0 ? REST_LAYER : a)));
    read.textContent = a < 0 ? "rest" : NAMES[a];
  }
  setActive(-1);

  /** y picks the layer whose middle sits nearest on screen, at the gap's TARGET, never the pose drawn. */
  function pick(sy) {
    let best = 0, bd = Infinity;
    layers.forEach((ly, k) => {
      const c = P((ly.x0 + ly.x1) / 2, (ly.y0 + ly.y1) / 2, zOf(k, gap.t) + LT);
      if (Math.abs(c[1] - sy) < bd) { bd = Math.abs(c[1] - sy); best = k; }
    });
    return best;
  }

  bag.add(pointer(stage, {
    move: ([sx, sy]) => { gap.t = GMAX * clamp((sx - 70) / 260, 0, 1); setActive(pick(sy)); B.wake(); },
    leave: () => { gap.t = GMAX * 0.45; setActive(-1); B.wake(); },
  }));
  bag.add(() => svg.replaceChildren());

  return {
    set: (v) => { const was = GMAX; GMAX = v; gap.t = was ? gap.t * (v / was) : v * 0.45; B.wake(); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "g1-ios",
  means: "Экран iPhone, разобранный на пять слоёв по гайдлайнам Apple: курсор по горизонтали раздвигает их, по вертикали выбирает слой.",
  rules: [1, 3, 4, 9],
  range: [5, 9, 13],
  tour: [[130, 140], [204, 197], [310, 250], null],
  mount,
});
