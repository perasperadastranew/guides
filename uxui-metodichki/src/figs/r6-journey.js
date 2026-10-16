/**
 * Journey: six stepping stones across a bed of ground, joined by a dashed
 * path. Their heights follow the mood of the way, with one deep dip, and the
 * dip stone is the bright mark at rest. The stone under the pointer lifts; its
 * neighbours follow less the farther they are, staggered outwards. The slider
 * is the stagger, in ms.
 */
const { Cam, clamp, fit, open, proj, rrect, prism, facing, unproj, tween, tset, tval, tdone, mk, put, solid, pointer, register, disposer } = HL;

// The way runs across the screen and a little toward the viewer: along s, turned TURN degrees from (1, -1) on the ground; t is across it.
const TURN = 16, CX = 80, CY = 80, CA = Math.cos(((45 - TURN) * Math.PI) / 180), SA = Math.sin(((45 - TURN) * Math.PI) / 180);
const W = (s, t) => [CX + s * CA + t * SA, CY - s * SA + t * CA];
const STONES = [
  { s: -70, t: -4, a: 10, b: 9, h: 27 },
  { s: -42, t: 5, a: 9.5, b: 10, h: 35 },
  { s: -14, t: -3, a: 10.5, b: 9, h: 21 },
  { s: 14, t: 6, a: 10, b: 10, h: 5 },
  { s: 42, t: -4, a: 9.5, b: 9.5, h: 18 },
  { s: 70, t: 3, a: 10.5, b: 10, h: 41 },
];
const DIP = 3, LIFT = 26, FALL = [1, 0.42, 0.18, 0.07, 0.03, 0.02];
const BS = 86, BT = 28, GB = 4;

/** A rounded rectangle in (s, t), turned onto the ground: its samples and their normals. */
function band(s0, t0, s1, t1, r) {
  return rrect(s0, t0, s1, t1, r, 6).map((q) => {
    const [x, y] = W(q.u, q.v);
    return { u: x, v: y, nu: q.nu * CA + q.nv * SA, nv: -q.nu * SA + q.nv * CA };
  });
}

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let stag = value;

  const C = Cam(45, 0.5, 1.86);
  fit(C, [[...W(-BS, -BT), -GB], [...W(BS, -BT), -GB], [...W(-BS, BT), -GB], [...W(BS, BT), -GB], [...W(70, 3), 41 + LIFT], [...W(-42, 5), 35 + LIFT]], 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  put(solid(g), prism(P, front, band(-BS, -BT, BS, BT, 14), band(-BS + 2, -BT + 2, BS - 2, BT - 2, 12), -GB, 0));
  // the way itself, a dashed line on the ground from stone to stone, under them
  mk("path", { class: "nf dash", d: open(STONES.map((s) => P(...W(s.s, s.t), 0))) }, g);

  // back to front: by x + y, the far corner first
  const order = STONES.map((s, i) => i).sort((a, b) => W(STONES[a].s, STONES[a].t).reduce((m, v) => m + v) - W(STONES[b].s, STONES[b].t).reduce((m, v) => m + v));
  const stones = STONES.map((s, i) => {
    const ring = band(s.s - s.a, s.t - s.b, s.s + s.a, s.t + s.b, 6.5), inner = band(s.s - s.a + 1.4, s.t - s.b + 1.4, s.s + s.a - 1.4, s.t + s.b - 1.4, 5.1);
    const [x, y] = W(s.s, s.t);
    return { i, ...s, x, y, r: Math.max(s.a, s.b), ring, inner, z: tween(0), el: null, drawn: NaN };
  });
  for (const i of order) stones[i].el = solid(g);
  stones[DIP].el.sil.classList.add("hi");

  function drawStone(s, now) {
    const top = s.h + tval(s.z, now);
    if (top === s.drawn) return;
    s.drawn = top;
    put(s.el, prism(P, front, s.ring, s.inner, 0, top));
  }

  const B = register(stage, (_dt, now) => {
    let moving = false;
    for (const s of stones) { drawStone(s, now); if (!tdone(s.z, now)) moving = true; }
    return moving;
  });
  bag.add(B.unregister);

  /** The stone whose resting top, unprojected at its own height, puts the pointer nearest its middle. */
  function hit(p) {
    let best = -1, bd = Infinity;
    for (const s of stones) {
      const [x, y] = unproj(C, p[0], p[1], s.h);
      const d = Math.hypot(x - s.x, y - s.y) / s.r;
      if (d < bd) { bd = d; best = s.i; }
    }
    return bd < 1.5 ? best : -1;
  }

  let act = -1;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = a >= 0 ? a : act;
    act = a;
    for (const s of stones) {
      const d = Math.abs(s.i - from);
      tset(s.z, a < 0 ? 0 : LIFT * FALL[Math.abs(s.i - a)], now, d * stag);
      s.el.sil.classList.toggle("hi", a < 0 ? s.i === DIP : s.i === a);
    }
    read.textContent = a < 0 ? "rest" : "этап " + (a + 1);
    B.wake();
  }

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());
  read.textContent = "rest";

  return {
    set: (v) => { stag = clamp(v, 0, 120); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "r6-journey",
  means: "Путь из шести камней: чем ниже камень, тем хуже пользователю на этом этапе.",
  rules: [1, 2, 5, 9],
  range: [0, 45, 90],
  tour: [[77, 127], [222, 192], [324, 146], null],
  mount,
});
