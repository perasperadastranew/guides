/**
 * Tiers: a tower of three trays. The bottom one holds a grid of round token
 * chips; the middle one holds components, a pill button, a toggle with its
 * knob, a checkbox, a radio and a text field; the top one is a screen, a
 * phone-shaped tray with a header, a picture card, two rows and a button.
 * Dashed drops tie each tray to the one under it. The pointer's x scrubs the
 * gap between the trays, on a spring; its y picks a tray, which takes the
 * bright edge. At rest the tower is slightly apart and the screen is bright.
 * The slider is the widest gap.
 */
const {
  Cam, fit, proj, facing, prism, rings, rrect, seg, extremes, poly, ringAt, clamp, lerp,
  spring, stepS, mk, solid, put, pointer, register, disposer,
} = HL;

const T = 5, CL = 7, W = 84, GR = 14, GMIN = 6, NAMES = ["токены", "компоненты", "экраны"];
/** The gap between tray i and the one over it: the upper gap a little wider, so the rest pose flares. */
const gapAt = (g, i) => g * (i === 0 ? 0.9 : 1.15);
const baseOf = (g, i) => (i === 0 ? 0 : i === 1 ? T + CL + gapAt(g, 0) : 2 * (T + CL) + gapAt(g, 0) + gapAt(g, 1));

/** Box solids: [x0, y0, x1, y1, r, b, height]. */
const box = (x0, y0, x1, y1, r, b, h) => ({ fp: rings(x0, y0, x1, y1, r, b), h });
function contents(i) {
  const out = [];
  if (i === 0) {
    for (let a = 0; a < 4; a++) for (let c = 0; c < 4; c++) {
      const x = 15 + a * 18, y = 15 + c * 18, r = a === 3 && c === 0 ? 6 : 4.6;
      out.push(box(x - r, y - r, x + r, y + r, r, 1, a === 3 && c === 0 ? 4 : 2.4));
    }
  } else if (i === 1) {
    out.push(box(10, 10, 48, 26, 8, 1.4, 3.4)); // a button
    out.push(box(56, 12, 72, 28, 8, 1.2, 3)); // a radio
    out.push(box(10, 36, 42, 50, 7, 1.2, 1.6)); // a toggle's track
    out.push(box(29, 37, 41, 49, 6, 1.1, 4.6)); // its knob
    out.push(box(54, 36, 72, 52, 3, 1.2, 3)); // a checkbox
    out.push(box(10, 60, 74, 74, 3, 1.2, 1.6)); // a text field
  } else {
    out.push(box(26, 10, 58, 20, 2.5, 1, 1.6)); // the header
    out.push(box(26, 24, 58, 46, 3, 1.2, 2.4)); // a picture card
    out.push(box(26, 50, 58, 56, 2, 0.8, 1.2)); // a row
    out.push(box(26, 59, 58, 65, 2, 0.8, 1.2)); // a row
    out.push(box(30, 69, 54, 77, 4, 1, 2.6)); // a button
  }
  return out.sort((p, q) => p.fp[0][0].u + p.fp[0][0].v - (q.fp[0][0].u + q.fp[0][0].v));
}

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let GMAX = value;

  const C = Cam(45, 0.5, 1.9);
  const top = (g) => baseOf(g, 2) + T + 4;
  fit(C, [[0, 0, 0], [W, W, 0], [W, 0, 0], [0, W, 0], [0, 0, top(40)], [W, 0, top(40)], [0, W, top(40)]], 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg), tiers = [];
  for (let i = 0; i < 3; i++) {
    const fp = i === 2 ? rings(16, -2, 68, W + 2, 10, 2) : rings(0, 0, W, W, 8, 2);
    const guide = i > 0 ? mk("path", { class: "nf lo dash" }, g) : null;
    const tray = solid(g), lip = mk("path", { class: "nf lo" }, g);
    const lipRing = i === 2 ? rrect(22, 4, 62, W - 4, 5, 5) : rrect(5, 5, W - 5, W - 5, 4, 5);
    const parts = contents(i).map((c) => ({ ...c, el: solid(g) }));
    tiers.push({ fp, guide, tray, lip, lipRing, parts, drops: extremes(P, fp[0]) });
  }

  const gap = spring(GR);
  let drawn = NaN;
  function draw(gv) {
    if (gv === drawn) return;
    drawn = gv;
    tiers.forEach((t, i) => {
      const z = baseOf(gv, i);
      put(t.tray, prism(P, front, t.fp[0], t.fp[1], z, z + T));
      t.lip.setAttribute("d", poly(ringAt(P, t.lipRing, z + T)));
      for (const p of t.parts) put(p.el, prism(P, front, p.fp[0], p.fp[1], z + T, z + T + p.h));
      if (t.guide) {
        const zb = baseOf(gv, i - 1) + T;
        t.guide.setAttribute("d", t.drops.slice(0, 2).map((q) => seg(P(q.u, q.v, zb), P(q.u, q.v, z))).join(""));
      }
    });
  }

  const B = register(stage, (dt) => {
    const m = stepS(gap, dt);
    draw(gap.x);
    return m;
  });
  bag.add(B.unregister);

  let act = -1, over = null;
  /** x sets the gap's target; y picks the tray whose middle, at that target, is nearest. */
  function update() {
    let a = -1;
    if (over) {
      gap.t = lerp(GMIN, GMAX, clamp((over[0] - 90) / 220, 0, 1));
      let bd = 1e9;
      for (let i = 0; i < 3; i++) {
        const y = P(W / 2, W / 2, baseOf(gap.t, i) + T)[1], d = Math.abs(over[1] - y);
        if (d < bd) { bd = d; a = i; }
      }
    } else gap.t = GR;
    act = a;
    tiers.forEach((t, i) => t.tray.sil.classList.toggle("hi", a < 0 ? i === 2 : i === a));
    read.textContent = a < 0 ? "rest" : NAMES[a];
    B.wake();
  }
  update();

  bag.add(pointer(stage, { move: (p) => { over = p; update(); }, leave: () => { over = null; update(); } }));
  bag.add(() => svg.replaceChildren());

  return {
    set: (v) => { GMAX = v; update(); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "d1-tiers",
  means: "Три лотка друг над другом: токены, компоненты, экраны. Указатель по горизонтали раздвигает их, по вертикали выбирает слой.",
  rules: [1, 3, 5, 8],
  range: [20, 30, 40],
  tour: [[140, 250], [250, 205], [330, 95], null],
  mount,
});
