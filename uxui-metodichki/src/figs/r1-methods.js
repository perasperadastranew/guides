/**
 * R1 methods: a square board split into four quadrants by two raised rails
 * that cross at a round boss, with a field of short pegs in each quadrant.
 * The pointer is put back on the ground; pegs rise near it on springs, and
 * the read-out names the quadrant: words or deeds, why or how many. At rest
 * one quadrant swells gently. The slider is the radius, in cells.
 */
const {
  Cam, clamp, facing, fit, prism, proj, rings, rrect, unproj, spring, stepS,
  mk, pointer, put, register, disposer, solid,
} = HL;

const Q = 4, CELL = 12, RG = 12, FOOT = 8, HMAX = 46, PB = 5, RW = 2.6, RH = 7, M = Q * CELL + RG / 2, EXT = 2 * M;

const falloff = (u) =>
  u <= 0 ? 1 : u <= 0.417 ? 1 - (u / 0.417) * 0.6875 : u <= 1 ? 0.3125 - ((u - 0.417) / 0.583) * 0.2185 : 0.094;
/** A cell's centre along one axis: the far quadrant, then the rail's gap, then the near one. */
const at = (i) => i * CELL + (i >= Q ? RG : 0) + CELL / 2;
const quad = (x, y) => (x < M ? "слова" : "дела") + "·" + (y < M ? "почему" : "сколько");

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  const C = Cam(45, 0.5, 1.86);
  fit(C, [[-6, -6, -PB], [EXT + 6, EXT + 6, -PB], [EXT + 6, -6, -PB], [-6, EXT + 6, -PB], [0, 0, HMAX]], 200, 166);
  const P = proj(C), front = facing(C);
  let R = value * CELL, over = null;

  const g = mk("g", {}, svg), cols = [];
  const [pr, pi] = rings(-6, -6, EXT + 6, EXT + 6, 9, 2.2);
  put(solid(g), prism(P, front, pr, pi, -PB, 0));

  /** One rail arm, a low bar from x0,y0 to x1,y1. */
  const arm = (x0, y0, x1, y1) => { const [r, n] = rings(x0, y0, x1, y1, RW, 0.8); put(solid(g), prism(P, front, r, n, 0, RH)); };
  /** The pegs of one quadrant, diagonal by diagonal from its far corner. */
  function pegs(qi, qj) {
    for (let s = 0; s <= 2 * (Q - 1); s++) for (let a = 0; a < Q; a++) {
      const b = s - a;
      if (b < 0 || b >= Q) continue;
      const i = qi * Q + a, j = qj * Q + b, cx = at(i), cy = at(j);
      const u = cx / EXT, v = cy / EXT;
      // rest: the "deeds · why" quadrant swells, a low ripple elsewhere
      const h0 = 5 + 17 * Math.exp(-((u - 0.74) ** 2 + (v - 0.27) ** 2) / 0.05) + 4 * Math.exp(-((u - 0.2) ** 2 + (v - 0.75) ** 2) / 0.04);
      const [ring, inner] = rings(cx - FOOT / 2, cy - FOOT / 2, cx + FOOT / 2, cy + FOOT / 2, 4, 0.9);
      cols.push({ cx, cy, h0, ring, inner, sp: spring(h0, { eps: 0.04 }), el: solid(g), drawn: NaN });
    }
  }
  // Paint order: far quadrant, far arms, the two side quadrants, near arms, the boss, near quadrant.
  pegs(0, 0);
  arm(M - RW, -2, M + RW, M); arm(-2, M - RW, M, M + RW);
  pegs(0, 1); pegs(1, 0);
  arm(M, M - RW, EXT + 2, M + RW); arm(M - RW, M, M + RW, EXT + 2);
  const boss = rrect(M - 6, M - 6, M + 6, M + 6, 6, 10), bossIn = rrect(M - 4.6, M - 4.6, M + 4.6, M + 4.6, 4.6, 10);
  const bossEl = solid(g);
  put(bossEl, prism(P, front, boss, bossIn, 0, RH + 3));
  pegs(1, 1);

  const peak = cols.reduce((a, b) => (b.h0 > a.h0 ? b : a));
  function drawCol(c) {
    const h = Math.max(0.6, c.sp.x);
    if (h === c.drawn) return;
    c.drawn = h;
    put(c.el, prism(P, front, c.ring, c.inner, 0, h));
    c.el.sil.classList.toggle("hi", over ? h > HMAX * 0.5 : c === peak);
  }

  const B = register(stage, (dt) => {
    let m = false;
    for (const c of cols) { if (stepS(c.sp, dt)) m = true; drawCol(c); }
    return m;
  });
  bag.add(B.unregister);

  function retarget() {
    for (const c of cols) {
      c.sp.t = over ? HMAX * falloff(Math.hypot(c.cx - over[0], c.cy - over[1]) / R) : c.h0;
      c.drawn = NaN;
    }
    read.textContent = over ? quad(over[0], over[1]) : "rest";
    B.wake();
  }

  bag.add(pointer(stage, {
    move: (p) => {
      const w = unproj(C, p[0], p[1], 0);
      over = w[0] < -6 || w[1] < -6 || w[0] > EXT + 6 || w[1] > EXT + 6 ? null : [clamp(w[0], 0, EXT), clamp(w[1], 0, EXT)];
      retarget();
    },
    leave: () => { over = null; retarget(); },
  }));
  bag.add(() => svg.replaceChildren());

  return { set: (v) => { R = v * CELL; if (over) retarget(); }, destroy: bag.dispose };
}

hairline({
  name: "r1-methods",
  means: "Доска из четырёх четвертей: слова или дела, почему или сколько. Колышки поднимаются там, где указатель.",
  rules: [1, 3, 5, 9],
  range: [1.5, 2.5, 4],
  tour: [[200, 110], [130, 175], [275, 175], [200, 235], null],
  mount,
});
