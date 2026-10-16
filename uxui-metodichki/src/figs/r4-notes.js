/**
 * R4 notes: a board lying flat with four piles of sticky notes, each pile a
 * problem and each note a quote. The pile under the pointer fans up into a
 * tall stack, note by note, each turning a little more than the one below,
 * so it can be counted. The read-out names the pile and its count. The
 * slider is the stagger, in ms.
 */
const {
  Cam, clamp, facing, fit, prism, proj, rings, rrect, rad, unproj, seg,
  tdone, tset, tval, tween, disposer, mk, pointer, put, register, solid,
} = HL;

const NS = 27, TK = 1.3, STEP = 2.5, FAN = 8.5, TURN = 7, PB = 4;
const X0 = 0, X1 = 120, Y0 = 0, Y1 = 106;
// piles back to front: centre, how many notes, and the slight twist of each note at rest
const PILES = [
  { c: [31, 29], n: 4 },
  { c: [89, 30], n: 6 },
  { c: [30, 78], n: 2 },
  { c: [88, 77], n: 3 },
];
const TWIST = [-8, 5, -3, 9, -6, 2];

/** A rounded square note ring, turned by deg about its centre, with its normals turned too. */
function turned(ring, [cx, cy], deg) {
  const c = Math.cos(rad(deg)), s = Math.sin(rad(deg));
  return ring.map((q) => ({ u: cx + q.u * c - q.v * s, v: cy + q.u * s + q.v * c, nu: q.nu * c - q.nv * s, nv: q.nu * s + q.nv * c }));
}

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let stag = value;
  const C = Cam(45, 0.5, 1.95);
  const top = 5 * FAN + 6;
  fit(C, [[X0, Y0, -PB], [X1, Y1, -PB], [X1, Y0, -PB], [X0, Y1, -PB], [89, 30, top], [31, 29, 3 * FAN + 6]], 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  const [br, bi] = rings(X0, Y0, X1, Y1, 8, 3.2);
  put(solid(g), prism(P, front, br, bi, -PB, 0));

  const base = rrect(-NS / 2, -NS / 2, NS / 2, NS / 2, 1.6, 3), baseIn = rrect(-NS / 2 + 0.8, -NS / 2 + 0.8, NS / 2 - 0.8, NS / 2 - 0.8, 1.2, 3);
  const notes = [];
  PILES.forEach((pl, p) => {
    pl.notes = [];
    for (let j = 0; j < pl.n; j++) {
      const el = solid(g), quote = mk("path", { class: "nf lo" }, el.g);
      const nt = { p, j, el, quote, z: tween(j * STEP), a: tween(TWIST[j]), drawn: "" };
      pl.notes.push(nt); notes.push(nt);
    }
  });

  function draw(nt, z, a) {
    const key = z.toFixed(2) + "," + a.toFixed(2);
    if (key === nt.drawn) return;
    nt.drawn = key;
    const c = PILES[nt.p].c;
    put(nt.el, prism(P, front, turned(base, c, a), turned(baseIn, c, a), z, z + TK));
    // the sticky band along one edge, and two lines of the quote
    const r = (u, v) => { const k = Math.cos(rad(a)), s = Math.sin(rad(a)); return P(c[0] + u * k - v * s, c[1] + u * s + v * k, z + TK); };
    nt.quote.setAttribute("d", seg(r(-NS / 2 + 1.5, -NS / 2 + 5), r(NS / 2 - 1.5, -NS / 2 + 5)) + seg(r(-7, 0), r(7, 0)) + seg(r(-7, 4.5), r(3, 4.5)));
  }

  const B = register(stage, (_dt, now) => {
    let m = false;
    for (const nt of notes) { draw(nt, tval(nt.z, now), tval(nt.a, now)); if (!tdone(nt.z, now) || !tdone(nt.a, now)) m = true; }
    return m;
  });
  bag.add(B.unregister);

  // hit: each pile's REST top, the pointer unprojected at that height; the nearest centre wins
  function hit([sx, sy]) {
    let best = -1, bd = 1e9;
    PILES.forEach((pl, p) => {
      const w = unproj(C, sx, sy, pl.n * STEP), d = Math.max(Math.abs(w[0] - pl.c[0]), Math.abs(w[1] - pl.c[1]));
      if (d < bd) { bd = d; best = p; }
    });
    return bd <= NS / 2 + 8 ? best : -1;
  }

  const big = PILES.reduce((a, b, i) => (b.n > PILES[a].n ? i : a), 0);
  let act = -1;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), was = act;
    act = a;
    PILES.forEach((pl, p) => pl.notes.forEach((nt) => {
      const up = p === a, j = nt.j;
      // rising: the top note leaves first; settling: the bottom one lands first, so no note passes through another
      const delay = p === a ? (pl.n - 1 - j) * stag : p === was ? j * stag : 0;
      tset(nt.z, up ? j * FAN : j * STEP, now, delay);
      tset(nt.a, up ? TWIST[j] + j * TURN : TWIST[j], now, delay);
      nt.el.sil.classList.toggle("hi", a < 0 ? p === big && j === pl.n - 1 : up);
    }));
    read.textContent = a < 0 ? "rest" : `проблема ${a + 1} · ${PILES[a].n}`;
    B.wake();
  }
  PILES[big].notes[PILES[big].n - 1].el.sil.classList.add("hi");

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());
  return { set: (v) => { stag = clamp(v, 0, 200); }, destroy: bag.dispose };
}

hairline({
  name: "r4-notes",
  means: "Доска с четырьмя стопками стикеров: стопка под указателем раскрывается вверх, и видно, сколько в ней цитат.",
  rules: [1, 2, 4, 6],
  range: [0, 45, 90],
  tour: [[200, 110], [130, 170], [270, 170], null],
  mount,
});
