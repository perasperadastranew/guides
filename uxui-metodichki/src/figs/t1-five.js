/**
 * Five: a round table on one column, a phone lying in the middle of its top,
 * and five stools round it, each a round seat on a gas-lift leg over a foot
 * disc. The stool under the pointer rises; its two neighbours rise a little,
 * staggered outwards round the table. At rest the stools stand at uneven
 * heights and distances and the phone, the one prototype, is bright. The
 * slider is the lift.
 */
const {
  Cam, fit, proj, facing, prism, rrect, unproj, ringAt, poly, seg,
  tween, tset, tval, tdone, mk, solid, put, pointer, register, disposer, rad,
} = HL;

const N = 5, TR = 34, TOP = 30, TT = 3, SR = 10, SEAT = 17, ST = 4, LEG = 2.6, FOOT = 7, STEP = 45;
// each stool: its angle round the table, its distance, and its rest lift, uneven on purpose
const SEATS = [[150, 58, 2], [218, 66, 0], [298, 60, 4], [12, 56, 1], [80, 61, 0]];

/** A round footprint and its crease, centred on (cx, cy). */
const disc = (cx, cy, R, b, n = 8) => [rrect(cx - R, cy - R, cx + R, cy + R, R, n), rrect(cx - R + b, cy - R + b, cx + R - b, cy + R - b, R - b, n)];

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let LIFT = value;

  const C = Cam(45, 0.5, 2.0);
  const ext = [];
  SEATS.forEach(([a, d]) => {
    const x = d * Math.cos(rad(a)), y = d * Math.sin(rad(a));
    ext.push([x - SR, y - SR, 0], [x + SR, y + SR, 0], [x - SR, y + SR, 0], [x + SR, y - SR, 0], [x, y, SEAT + ST + 28]);
  });
  fit(C, ext.concat([[0, 0, TOP + TT + 2]]), 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  const back = mk("g", {}, g), table = mk("g", {}, g), fore = mk("g", {}, g);

  // the table: a foot disc, a column, a thick round top
  const [fr, fi] = disc(0, 0, 15, 1.4);
  put(solid(table), prism(P, front, fr, fi, 0, 2));
  const [cr] = disc(0, 0, 4, 0.8);
  put(solid(table), prism(P, front, cr, null, 2, TOP));
  const [tr, ti] = disc(0, 0, TR, 2, 14);
  put(solid(table), prism(P, front, tr, ti, TOP, TOP + TT));

  // the phone: a thin slab lying on the top, its screen inset, a speaker slot and a home bar
  const z1 = TOP + TT, z2 = z1 + 1.6;
  const ph = solid(table);
  put(ph, prism(P, front, rrect(-9, -16, 9, 16, 3.5, 5), rrect(-8, -15, 8, 15, 2.8, 5), z1, z2));
  mk("path", { d: poly(ringAt(P, rrect(-7, -12, 7, 12, 1.5, 4), z2)), class: "nf lo" }, table);
  mk("path", { d: seg(P(-2, -14, z2), P(2, -14, z2)) + seg(P(-3, 13.6, z2), P(3, 13.6, z2)), class: "nf lo" }, table);

  // the stools: the ones behind the table are painted before it, the ones in front after
  const stools = SEATS.map(([a, d, r0], i) => {
    const x = d * Math.cos(rad(a)), y = d * Math.sin(rad(a));
    const par = x + y < 0 ? back : fore;
    const sg = mk("g", {}, par);
    const foot = solid(sg), leg = solid(sg), seat = solid(sg);
    const [ff, fi2] = disc(x, y, FOOT, 1);
    put(foot, prism(P, front, ff, fi2, 0, 1.6));
    leg.cr.remove();
    return { x, y, r0, d: x + y, sg, leg, seat, ring: disc(x, y, SR, 1.6, 8), lr: disc(x, y, LEG, 0.6)[0], z: tween(r0), drawn: NaN };
  });
  // within each half, far to near
  [back, fore].forEach((par) => stools.filter((s) => s.sg.parentNode === par).sort((p, q) => p.d - q.d).forEach((s) => par.append(s.sg)));

  function draw(s, h) {
    if (h === s.drawn) return;
    s.drawn = h;
    put(s.leg, prism(P, front, s.lr, null, 1.6, SEAT + h));
    put(s.seat, prism(P, front, s.ring[0], s.ring[1], SEAT + h, SEAT + h + ST));
  }

  const B = register(stage, (_dt, now) => {
    let m = false;
    for (const s of stools) { draw(s, tval(s.z, now)); if (!tdone(s.z, now)) m = true; }
    return m;
  });
  bag.add(B.unregister);

  // hit: the pointer on each stool's own rest seat top; the nearest centre within reach
  function hit([sx, sy]) {
    let best = -1, bd = SR + 8;
    stools.forEach((s, i) => {
      const [wx, wy] = unproj(C, sx, sy, SEAT + s.r0 + ST);
      const dd = Math.hypot(wx - s.x, wy - s.y);
      if (dd < bd) { bd = dd; best = i; }
    });
    return best;
  }

  let act = -1;
  const ring = (i, a) => { const k = Math.abs(i - a) % N; return Math.min(k, N - k); };
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = a >= 0 ? a : act >= 0 ? act : 0;
    act = a;
    stools.forEach((s, i) => {
      const k = ring(i, from);
      const to = a < 0 ? s.r0 : k === 0 ? LIFT : k === 1 ? s.r0 + LIFT * 0.35 : s.r0;
      tset(s.z, to, now, k * STEP);
      s.seat.sil.classList.toggle("hi", i === a);
    });
    ph.sil.classList.toggle("hi", a < 0);
    read.textContent = a < 0 ? "rest" : "участник " + (a + 1);
    B.wake();
  }
  ph.sil.classList.add("hi");
  read.textContent = "rest";

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());

  return {
    set: (v) => { LIFT = v; const a = act; act = -2; setActive(a); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "t1-five",
  means: "Пять табуретов вокруг стола с одним телефоном: табурет под указателем поднимается, соседи чуть следом.",
  rules: [1, 2, 5, 6],
  range: [12, 20, 28],
  tour: [[87, 154], [182, 107], [313, 148], [127, 222], null],
  mount,
});
