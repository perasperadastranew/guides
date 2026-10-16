/**
 * Sheet: a phone lying flat, its screen holding a header and cards, and a
 * bottom sheet plate floating just over the screen. The pointer's place along
 * the phone sets how far the sheet slides up, on a spring; the slider is how
 * hard it snaps to the three stops (closed, half, full).
 */
const {
  Cam, clamp, facing, fit, lerp, open, poly, prism, proj, ringAt, rings, rrect, run, unproj,
  spring, stepS, mk, pointer, put, register, disposer, solid,
} = HL;

const W = 74, L = 152, R = 13, ZB = 8, ZS = 11, ZT = 13.4, IN = 4.5;
const FULL = 22, HALF = 74, CLOSED = 124, REST = 110, FOOT = L - IN - 1.5;
const STOPS = [CLOSED, HALF, FULL], NAMES = ["закрыта", "половина", "полная"];

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let snap = value;
  const C = Cam(45, 0.5, 1.88);
  fit(C, [[0, 0, 0], [W, L, 0], [W, 0, 0], [0, L, 0], [0, 0, ZT]], 200, 170);
  const P = proj(C), front = facing(C);
  const flat = (x0, y0, x1, y1, r, z) => poly(ringAt(P, rrect(x0, y0, x1, y1, r, 5), z));

  const g = mk("g", {}, svg);
  // the phone: a rounded slab, the screen's edge, the island, the side buttons
  const [pr, pi] = rings(0, 0, W, L, R, 1.6);
  put(solid(g), prism(P, front, pr, pi, 0, ZB));
  mk("path", { d: flat(IN, IN, W - IN, L - IN, R - IN, ZB), class: "nf" }, g);
  mk("path", { d: flat(W / 2 - 10, 8.5, W / 2 + 10, 14, 2.7, ZB), class: "nf" }, g);
  mk("path", { d: open([P(W, 34, ZB * 0.5), P(W, 52, ZB * 0.5)]), class: "nf lo" }, g);
  // what the sheet slides over: a header, a picture card and two rows
  const under = [
    flat(11, 20, W - 11, 28, 2, ZB), flat(11, 34, W - 11, 72, 4, ZB),
    flat(11, 78, W - 11, 92, 3, ZB), flat(11, 98, W - 11, 112, 3, ZB),
  ].join("");
  mk("path", { d: under, class: "nf lo" }, g);
  mk("path", { d: open([P(16, 64, ZB), P(28, 50, ZB), P(37, 59, ZB), P(46, 46, ZB), P(W - 16, 64, ZB)]), class: "nf lo" }, g);

  // the sheet: a thin plate, its grabber and its rows, redrawn when its top edge moves
  const sheet = solid(g);
  const grab = mk("path", { class: "nf hi" }, g), rows = mk("path", { class: "nf lo" }, g);
  const sp = spring(REST);
  let drawn = NaN, over = null;

  function draw(e) {
    if (e === drawn) return;
    drawn = e;
    const [sr, si] = rings(IN + 1.5, e, W - IN - 1.5, FOOT, R - IN - 1, 1.4);
    put(sheet, prism(P, front, sr, si, ZS, ZT));
    grab.setAttribute("d", flat(W / 2 - 8, e + 5, W / 2 + 8, e + 8, 1.5, ZT));
    let d = "";
    for (let y = e + 15; y + 10 < FOOT - 4; y += 15) d += flat(12, y, W - 12, y + 10, 2.5, ZT);
    rows.setAttribute("d", d);
  }

  const B = register(stage, (dt) => { const m = stepS(sp, dt); draw(sp.x); return m; });
  bag.add(B.unregister);

  /** The stop nearest a target edge. */
  const nearest = (t) => STOPS.reduce((a, b) => (Math.abs(b - t) < Math.abs(a - t) ? b : a));
  function retarget() {
    if (!over) { sp.t = REST; read.textContent = "rest"; }
    else {
      const raw = clamp(over[1], FULL, CLOSED), stop = nearest(raw);
      sp.t = lerp(raw, stop, snap);
      read.textContent = NAMES[STOPS.indexOf(stop)];
    }
    sheet.sil.classList.toggle("hi", !!over);
    B.wake();
  }

  // hit test: the screen plane, which never moves; along the phone, the pointer is where the edge goes
  bag.add(pointer(stage, {
    move: (p) => {
      const q = unproj(C, p[0], p[1], ZB);
      over = q[0] > -14 && q[0] < W + 14 && q[1] > -20 && q[1] < L + 12 ? q : null;
      retarget();
    },
    leave: () => { over = null; retarget(); },
  }));
  bag.add(() => svg.replaceChildren());

  return {
    set: (v) => { snap = v; if (over) retarget(); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "g3-sheet",
  means: "Нижняя шторка поверх экрана: она выезжает вверх до точки под курсором и цепляется за три положения.",
  rules: [1, 3, 5, 8],
  range: [0, 0.6, 1],
  tour: [[132, 202], [203, 167], [268, 134], null],
  mount,
});
