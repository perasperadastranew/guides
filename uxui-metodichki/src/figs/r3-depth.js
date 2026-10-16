/**
 * R3 depth: a ground core sample standing on a round base, five strata of
 * different thickness. The pointer's x scrubs the gap and the core comes
 * apart in layers; its y picks a stratum, which takes the bright edge and
 * lights the pebbles on its top. At rest the core is barely parted and the
 * deep stratum is bright. The slider is the widest gap.
 */
const {
  Cam, clamp, facing, fit, prism, proj, rrect, ringAt, lerp, poly, seg, spring, stepS,
  mk, place, pointer, put, register, disposer, solid,
} = HL;

const R = 30, THICK = [8, 10, 13, 11, 16], N = 5, GAP0 = 3, BASE = 4;
// pebbles on each stratum's front face, [angle in degrees, height as a share of the stratum]: deeper strata hold more of them
const PEB = [[], [[30, 0.5], [70, 0.45]], [[5, 0.6], [40, 0.35], [80, 0.65]], [[15, 0.4], [35, 0.7], [62, 0.35], [95, 0.55]], [[0, 0.3], [22, 0.65], [45, 0.4], [68, 0.7], [90, 0.35]]];
// tufts of grass on the surface: [x, y] on the top disc
const TUFT = [[-14, 6], [-4, 14], [8, -10], [16, 4], [-12, -12], [4, 2]];

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let gmax = value;
  const total = THICK.reduce((a, b) => a + b, 0);
  const C = Cam(45, 0.5, 2.1);
  fit(C, [[-R - 10, -R - 10, -BASE], [R + 10, R + 10, -BASE], [R + 10, -R - 10, -BASE], [-R - 10, R + 10, -BASE], [0, 0, total + 4 * 14 + 5]], 200, 166);
  const P = proj(C), front = facing(C);
  const ring = rrect(-R, -R, R, R, R, 14), inner = rrect(-R + 1.2, -R + 1.2, R - 1.2, R - 1.2, R - 1.2, 14);

  const g = mk("g", {}, svg);
  const BR = R + 10;
  put(solid(g), prism(P, front, rrect(-BR, -BR, BR, BR, BR, 14), rrect(-BR + 2, -BR + 2, BR - 2, BR - 2, BR - 2, 14), -BASE, 0));
  // the socket the core stands in
  mk("path", { d: poly(ringAt(P, rrect(-R - 2, -R - 2, R + 2, R + 2, R + 2, 14), 0)), class: "nf lo" }, g);

  // strata, bottom (deepest, index 4) first, so each higher one covers the one below
  const layers = [];
  for (let i = N - 1; i >= 0; i--) {
    const el = solid(g), grp = el.g;
    const dots = PEB[i].map(() => mk("circle", { r: 1.5, class: "dot off" }, grp));
    const tuft = i === 0 ? mk("path", { class: "nf lo" }, grp) : null;
    layers[i] = { el, dots, tuft, drawn: NaN };
  }
  const gap = spring(GAP0);

  /** The bottom of stratum i at gap gp: everything under it, plus a gap per stratum under it. */
  const bottom = (i, gp) => { let z = 0; for (let j = N - 1; j > i; j--) z += THICK[j] + gp; return z; };

  function draw() {
    const gp = Math.max(0, gap.x);
    layers.forEach((L, i) => {
      const z0 = bottom(i, gp), z1 = z0 + THICK[i];
      if (z0 === L.drawn) return;
      L.drawn = z0;
      put(L.el, prism(P, front, ring, inner, z0, z1));
      L.dots.forEach((el, k) => { const [a, f] = PEB[i][k], t = (a * Math.PI) / 180; place(el, P(R * Math.cos(t), R * Math.sin(t), z0 + f * THICK[i])); });
      if (L.tuft) L.tuft.setAttribute("d", TUFT.map(([x, y]) => seg(P(x - 1.2, y, z1), P(x - 1.8, y, z1 + 3.5)) + seg(P(x, y, z1), P(x, y, z1 + 4.5)) + seg(P(x + 1.2, y, z1), P(x + 1.8, y, z1 + 3.5))).join(""));
    });
  }

  const B = register(stage, (dt) => { const m = stepS(gap, dt); draw(); return m; });
  bag.add(B.unregister);

  let act = -1;
  function mark(a) {
    const on = a < 0 ? 3 : a;
    layers.forEach((L, i) => {
      L.el.sil.classList.toggle("hi", i === on);
      L.dots.forEach((d) => d.setAttribute("class", i === on ? "dot" : "dot off"));
    });
  }
  mark(-1);

  // pick: the stratum whose front band, in the TARGET pose, holds the pointer's y
  function pick(sy) {
    const gp = gap.t, fx = R * Math.SQRT1_2;
    let best = 0, bd = 1e9;
    for (let i = 0; i < N; i++) {
      const z0 = bottom(i, gp), y0 = P(fx, fx, z0)[1], y1 = P(fx, fx, z0 + THICK[i])[1] - R * 0.5;
      const d = sy < y1 ? y1 - sy : sy > y0 ? sy - y0 : 0;
      if (d < bd) { bd = d; best = i; }
    }
    return best;
  }

  function move([sx, sy]) {
    gap.t = lerp(GAP0, gmax, clamp((sx - 90) / 220, 0, 1));
    const a = pick(sy);
    if (a !== act) { act = a; mark(a); read.textContent = "слой " + (a + 1); }
    B.wake();
  }
  function leave() { gap.t = GAP0; act = -1; mark(-1); read.textContent = "rest"; B.wake(); }

  bag.add(pointer(stage, { move, leave }));
  bag.add(() => svg.replaceChildren());
  return { set: (v) => { gmax = v; }, destroy: bag.dispose };
}

hairline({
  name: "r3-depth",
  means: "Керн из пяти слоёв: указатель по горизонтали раздвигает слои, по вертикали выбирает, насколько глубоко копать.",
  rules: [1, 3, 5, 8],
  range: [6, 10, 14],
  tour: [[150, 120], [250, 170], [320, 220], null],
  mount,
});
