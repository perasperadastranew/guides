/**
 * Coins: four stacks on a tray, stepping down toward the viewer, each with its
 * own cap: a tall stack with a slot in its top coin (ads), a stack under a
 * flat ring (subscription), a short stack with a small coin cut off on top
 * (commission), one big single coin (a purchase). The pointer picks a stack:
 * it rises, and the others part from it, staggered by distance. The slider is
 * the rise.
 */
const {
  Cam, circ, facing, fit, poly, prism, proj, ringAt, rings, rrect,
  tset, tval, tdone, tween, mk, pointer, put, register, disposer, solid,
} = HL;

const GAP = 30, CR = 10, CT = 3, PART = 6, LMAX = 26;
const X0 = -18, X1 = 3 * GAP + 18, Y0 = -18, Y1 = 18, TH = 5;
// back to front: [name, coins, cap]
const STACKS = [["реклама", 7, "slot"], ["подписка", 5, "ring"], ["комиссия", 3, "cut"], ["покупка", 1, "big"]];
const CAM_S = 2.45;
const CAM_FIT = [[X0, Y0, 0], [X1, Y1, 0], [X1, Y0, 0], [X0, Y1, 0], [0, 0, TH + 7 * CT + LMAX], [-PART, 0, TH + 7 * CT + LMAX]];

const disc = (R, cx, cy) => circ(R, 28).map((q) => ({ ...q, u: q.u + cx, v: q.v + cy }));

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let L = value;
  const C = Cam(45, 0.5, CAM_S);
  fit(C, CAM_FIT, 200, 166);
  const P = proj(C), front = facing(C);
  const g = mk("g", {}, svg);

  // the tray: a low slab with a lip
  const [ta, tb] = rings(X0, Y0, X1, Y1, 12, 2);
  put(solid(g), prism(P, front, ta, tb, 0, TH));
  mk("path", { class: "nf lo", d: poly(ringAt(P, rrect(X0 + 4, Y0 + 4, X1 - 4, Y1 - 4, 9, 6), TH)) }, g);

  const stacks = STACKS.map(([name, n, cap], i) => {
    const grp = mk("g", {}, g), parts = [], cx = i * GAP;
    const coin = (R, ox, oy, z0, z1) => {
      const s = solid(grp);
      parts.push((dx, h) => put(s, prism(P, front, disc(R, cx + dx + ox, oy), disc(R - 1.3, cx + dx + ox, oy), TH + z0 + h, TH + z1 + h)));
      return s;
    };
    const flat = (cls, fn) => { const el = mk("path", { class: cls }, grp); parts.push((dx, h) => el.setAttribute("d", fn(cx + dx, TH + h))); return el; };
    let capEl, top;
    if (cap === "big") { capEl = coin(14, 0, 0, 0, 5).sil; top = 5; flat("nf lo", (x, z) => poly(ringAt(P, disc(9, x, 0), z + 5))); }
    else {
      for (let k = 0; k < n; k++) { const s = coin(CR, 0, 0, k * CT, (k + 1) * CT); if (k === n - 1) capEl = s.sil; }
      top = n * CT;
      if (cap === "slot") capEl = flat("nf", (x, z) => poly(ringAt(P, rrect(x - 6, -1.4, x + 6, 1.4, 1.4, 4), z + top)));
      if (cap === "ring") { capEl = coin(CR - 0.5, 0, 0, top, top + 2.2).sil; flat("nf", (x, z) => poly(ringAt(P, disc(6.2, x, 0), z + top + 2.2))); top += 2.2; }
      if (cap === "cut") { capEl = coin(5, 3, 3, top, top + CT).sil; top += CT; }
    }
    return { name, cx, top, grp, parts, capEl, dx: tween(0), h: tween(0), drawn: "" };
  });

  const draw = (s, dx, h) => { const k = dx + "," + h; if (k === s.drawn) return; s.drawn = k; s.parts.forEach((f) => f(dx, h)); };
  const B = register(stage, (_dt, now) => {
    let m = false;
    stacks.forEach((s) => { draw(s, tval(s.dx, now), tval(s.h, now)); if (!tdone(s.dx, now) || !tdone(s.h, now)) m = true; });
    return m;
  });
  bag.add(B.unregister);

  /** Which stack: the pointer against each stack's REST middle, nearest in screen x, within the row's band. */
  const mids = stacks.map((s) => P(s.cx, 0, TH + s.top / 2));
  function hit([sx, sy]) {
    let best = -1, bd = 40;
    mids.forEach((m, i) => { const d = Math.abs(sx - m[0]); if (d < bd && Math.abs(sy - m[1]) < 60) { bd = d; best = i; } });
    return best;
  }

  let act = -1;
  function setActive(a, force) {
    if (a === act && !force) return;
    const now = performance.now(), from = a >= 0 ? a : act;
    act = a;
    stacks.forEach((s, i) => {
      const delay = from < 0 ? 0 : Math.abs(i - from) * 45;
      tset(s.h, i === a ? L : 0, now, delay);
      tset(s.dx, a < 0 || i === a ? 0 : i < a ? -PART : PART, now, delay);
      s.capEl.classList.toggle("hi", a < 0 ? i === 1 : i === a);
    });
    read.textContent = a < 0 ? "rest" : stacks[a].name;
    B.wake();
  }
  setActive(-1, true);

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());
  return { set: (v) => { L = v; if (act >= 0) setActive(act, true); }, destroy: bag.dispose };
}

hairline({
  name: "s4-coins",
  means: "Четыре способа зарабатывать на продукте: подписка, покупка, реклама и комиссия.",
  rules: [1, 2, 4, 5],
  range: [10, 18, 26],
  tour: [[122, 130], [226, 195], [278, 228], null],
  mount,
});
