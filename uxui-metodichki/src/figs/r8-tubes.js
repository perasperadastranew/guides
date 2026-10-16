/**
 * Tubes: a test-tube rack, a base and a shelf with three holes on two end
 * posts, and three round-bottomed tubes standing through the holes, each
 * filled to its own level (a line on the glass). The tube under the pointer
 * lifts out of the rack; its neighbours stir a little, staggered outwards.
 * The fullest tube's level is the bright mark at rest. The slider is the lift.
 */
const { Cam, clamp, fit, hull, open, poly, proj, rings, prism, facing, tween, tset, tval, tdone, mk, put, solid, pointer, register, disposer } = HL;

const RL = 100, RD = 28, CY = RD / 2, BZ = 4, SZ0 = 30, SZ1 = 34, R = 5.2, TL = 64, TZ = 8, LMAX = 50;
const TUBES = [{ x: 26, lvl: 0.56 }, { x: 50, lvl: 0.86 }, { x: 74, lvl: 0.71 }];
const FULL = 1;

/** A tube's circle at height z, as screen points, n of them, from angle a0 to a1 (degrees). */
const arc = (P, cx, z, r, a0, a1, n) => Array.from({ length: n + 1 }, (_, k) => {
  const a = ((a0 + ((a1 - a0) * k) / n) * Math.PI) / 180;
  return P(cx + r * Math.cos(a), CY + r * Math.sin(a), z);
});

/** The silhouette of the stretch of a tube from z0 to z1: round at the bottom when z0 is the tube's own bottom. */
function piece(P, cx, z0, z1, round) {
  if (z1 - z0 < 0.2) return "";
  const pts = arc(P, cx, z1, R, 0, 360, 24);
  if (round) for (let k = 0; k <= 5; k++) {
    const t = (k / 5) * (Math.PI / 2), zz = z0 + R - R * Math.sin(t);
    if (zz <= z1) pts.push(...arc(P, cx, zz, R * Math.cos(t) + 0.01, 0, 360, 24));
  } else pts.push(...arc(P, cx, z0, R, 0, 360, 24));
  return poly(hull(pts));
}

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let lift = value;

  const C = Cam(45, 0.5, 2.2);
  fit(C, [[0, 0, 0], [RL, RD, 0], [RL, 0, 0], [0, RD, 0], [26, CY, TZ + TL + LMAX], [74, CY, TZ + TL + LMAX]], 200, 160);
  const P = proj(C), front = facing(C);
  const g = mk("g", {}, svg);

  // the rack: the base, the far post, the tubes below the shelf, the near post, the shelf and its holes
  const [br, bi] = rings(0, 0, RL, RD, 6, 1.6);
  put(solid(g), prism(P, front, br, bi, 0, BZ));
  const [p0, p0i] = rings(2, 3, 8, RD - 3, 2.4, 1);
  put(solid(g), prism(P, front, p0, p0i, BZ, SZ0));
  const tubes = TUBES.map((t, i) => ({ ...t, i, z: tween(0), lo: mk("path", { class: "sil" }, g), loLvl: mk("path", { class: "nf lo" }, g) }));
  const [p1, p1i] = rings(RL - 8, 3, RL - 2, RD - 3, 2.4, 1);
  put(solid(g), prism(P, front, p1, p1i, BZ, SZ0));
  put(solid(g), prism(P, front, br, bi, SZ0, SZ1));
  for (const t of TUBES) mk("path", { class: "nf", d: poly(arc(P, t.x, SZ1, R + 1.2, 0, 360, 24)) }, g);
  for (const t of tubes) {
    t.hi = mk("path", { class: "sil" }, g);
    t.mouth = mk("path", { class: "nf" }, g);
    t.lip = mk("path", { class: "nf lo" }, g);
    t.hiLvl = mk("path", { class: "nf lo" }, g);
  }

  /** Draws tube t with its bottom at zb: the stretch under the shelf, and the stretch above it. */
  function drawTube(t, zb) {
    const top = zb + TL, zf = zb + 1.5 + (TL - 8) * t.lvl;
    t.lo.setAttribute("d", piece(P, t.x, zb, Math.min(SZ0, top), true));
    t.hi.setAttribute("d", zb >= SZ1 ? piece(P, t.x, zb, top, true) : piece(P, t.x, SZ1, top, false));
    t.mouth.setAttribute("d", poly(arc(P, t.x, top, R, 0, 360, 24)));
    t.lip.setAttribute("d", open(arc(P, t.x, top - 3, R, -45, 135, 12)));
    const level = open(arc(P, t.x, zf, R, -45, 135, 12));
    const below = zf < SZ0, hidden = zf >= SZ0 && zf <= SZ1;
    t.loLvl.setAttribute("d", below ? level : "");
    t.hiLvl.setAttribute("d", !below && !hidden ? level : "");
  }

  const B = register(stage, (_dt, now) => {
    let moving = false;
    for (const t of tubes) { drawTube(t, TZ + tval(t.z, now)); if (!tdone(t.z, now)) moving = true; }
    return moving;
  });
  bag.add(B.unregister);

  // hit test: the vertical band of each tube's resting axis, reaching up to its lifted top
  const axis = TUBES.map((t) => P(t.x, CY, 0)[0]);
  const yTop = (t) => P(t.x, CY, TZ + TL + lift)[1] - 8, yBot = (t) => P(t.x, CY, 0)[1] + 10;
  function hit([x, y]) {
    let best = -1, bd = Infinity;
    axis.forEach((ax, i) => { const d = Math.abs(x - ax); if (d < bd) { bd = d; best = i; } });
    const t = TUBES[best];
    return bd < 15 && y > yTop(t) && y < yBot(t) ? best : -1;
  }

  let act = -1;
  function setActive(a, force) {
    if (a === act && !force) return;
    const now = performance.now(), from = a >= 0 ? a : act;
    act = a;
    for (const t of tubes) {
      const d = Math.abs(t.i - from);
      tset(t.z, a < 0 ? 0 : t.i === a ? lift : lift * 0.1, now, d * 45);
      for (const el of [t.lo, t.hi]) el.classList.toggle("hi", t.i === a);
      const lit = a < 0 ? t.i === FULL : t.i === a;
      for (const el of [t.loLvl, t.hiLvl]) el.setAttribute("class", lit ? "nf hi" : "nf lo");
    }
    read.textContent = a < 0 ? "rest" : "гипотеза " + (a + 1);
    B.wake();
  }

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());
  setActive(-1, true);

  return {
    set: (v) => { lift = clamp(v, 0, LMAX); if (act >= 0) setActive(act, true); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "r8-tubes",
  means: "Штатив с тремя пробирками-гипотезами: пробирка под курсором поднимается из штатива на проверку.",
  rules: [1, 2, 4, 6],
  range: [26, 38, 50],
  tour: [[163, 128], [200, 146], [237, 165], null],
  mount,
});
