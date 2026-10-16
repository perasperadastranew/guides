/**
 * B2C and B2B: two pedestals side by side. On the left one, a single phone
 * lies on a small stool: one person chooses, pays and uses. On the right one,
 * an office desk carries three monitors: different people choose, pay and
 * work. The pointer picks a pedestal: it rises and the other sinks a little,
 * staggered. The slider is the rise.
 */
const {
  Cam, circ, facing, fillet, fit, poly, prism, proj, rings, rrect, seg,
  tset, tval, tdone, tween, flatDot, mk, place, pointer, put, register, disposer, solid,
} = HL;

const PW = 25, HA = 12, HB = 22, LMAX = 24, SINK = 0.35;
const CA = [0, 62], CB = [62, 0];
const NAMES = ["B2C", "B2B"];
const CAM_S = 1.86;
const CAM_FIT = [
  [CA[0] - PW, CA[1] - PW, 0], [CA[0] - PW, CA[1] + PW, 0], [CA[0] + PW, CA[1] + PW, 0],
  [CB[0] - PW, CB[1] - PW, 0], [CB[0] + PW, CB[1] - PW, 0], [CB[0] + PW, CB[1] + PW, 0],
  [CA[0] - PW, CA[1] - PW, HA + LMAX + 18], [CB[0] - PW, CB[1] - PW, HB + LMAX + 42], [CB[0] + PW, CB[1] - PW, HB + LMAX + 42],
];

const shift = (ring, cx, cy) => ring.map((q) => ({ ...q, u: q.u + cx, v: q.v + cy }));
const MON = fillet([[0, 0], [13, 0], [13, 12], [0, 12]], [1.8, 1.8, 1.8, 1.8]);

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let L = value;
  const C = Cam(45, 0.5, CAM_S);
  fit(C, CAM_FIT, 200, 166);
  const P = proj(C), front = facing(C);
  const g = mk("g", {}, svg);

  function stand([cx, cy], h0) {
    const grp = mk("g", {}, g), parts = [];
    const box = (x0, y0, x1, y1, r, b, z0, z1) => {
      const s = solid(grp), [a, c] = rings(x0, y0, x1, y1, r, b);
      parts.push((h) => put(s, prism(P, front, a, c, h + z0, h + z1)));
      return s;
    };
    const ped = solid(grp), [pa, pc] = rings(cx - PW, cy - PW, cx + PW, cy + PW, 9, 2);
    parts.push((h) => put(ped, prism(P, front, pa, pc, 0, h)));
    return { grp, parts, box, ped, h0, tw: tween(h0), drawn: NaN };
  }

  // B2C: a stool with three legs, a phone lying on its seat
  const A = stand(CA, HA), [ax, ay] = CA;
  [[-9, -3], [3, -9], [6, 7]].forEach(([dx, dy]) => A.box(ax + dx - 1.6, ay + dy - 1.6, ax + dx + 1.6, ay + dy + 1.6, 1.5, 0.6, 0, 11));
  const seat = solid(A.grp), sa = shift(circ(16.5, 24), ax, ay), sb = shift(circ(15, 24), ax, ay);
  A.parts.push((h) => put(seat, prism(P, front, sa, sb, h + 11, h + 14)));
  A.box(ax - 7.5, ay - 13, ax + 7.5, ay + 13, 3.2, 1, 14, 16);
  const scr = mk("path", { class: "nf lo" }, A.grp);
  A.parts.push((h) => scr.setAttribute("d", poly(rrect(ax - 5.5, ay - 10, ax + 5.5, ay + 10, 2, 3).map((q) => P(q.u, q.v, h + 16)))));
  const note = flatDot(A.grp, C, 1.6, "dot");
  A.parts.push((h) => place(note, P(ax + 1.5, ay - 4, h + 16)));

  // B2B: a desk on two side panels, three monitors on its back edge
  const B = stand(CB, HB), [bx, by] = CB;
  B.box(bx - 21, by - 10, bx - 18, by + 10, 1.2, 0.6, 0, 22);
  B.box(bx + 18, by - 10, bx + 21, by + 10, 1.2, 0.6, 0, 22);
  B.box(bx - 23, by - 12, bx + 23, by + 12, 3, 1.2, 22, 25);
  [-20.5, -6.5, 7.5].forEach((x0) => {
    const mx = bx + x0 + 6.5, my = by - 6;
    B.box(mx - 4, my - 3, mx + 4, my + 3, 1.5, 0.8, 25, 26.2);
    B.box(mx - 1, my - 1, mx + 1, my + 1, 0.8, 0.4, 26.2, 31);
    const back = mk("path", { class: "lo" }, B.grp), face = mk("path", { class: "sil" }, B.grp), inner = mk("path", { class: "nf lo" }, B.grp);
    const at = (h, dy) => (p) => P(bx + x0 + p[0], my + dy, h + 29 + p[1]);
    B.parts.push((h) => {
      back.setAttribute("d", poly(MON.map(at(h, -1.4))));
      face.setAttribute("d", poly(MON.map(at(h, 0))));
      inner.setAttribute("d", seg(at(h, 0)([2.5, 8.5]), at(h, 0)([8, 8.5])) + seg(at(h, 0)([2.5, 5.5]), at(h, 0)([10.5, 5.5])));
    });
  });

  const items = [A, B];
  const draw = (it, h) => { if (h === it.drawn) return; it.drawn = h; it.parts.forEach((f) => f(h)); };
  const Bk = register(stage, (_dt, now) => {
    let m = false;
    items.forEach((it) => { draw(it, tval(it.tw, now)); if (!tdone(it.tw, now)) m = true; });
    return m;
  });
  bag.add(Bk.unregister);

  /** Which pedestal: the pointer against each one's REST pose, its middle raised to the middle of what stands on it. */
  const mids = [P(ax, ay, HA + 8), P(bx, by, HB + 18)];
  function hit([sx, sy]) {
    let best = -1, bd = 78;
    mids.forEach((m, i) => { const d = Math.hypot(sx - m[0], (sy - m[1]) * 1.3); if (d < bd) { bd = d; best = i; } });
    return best;
  }

  let act = -1;
  function setActive(a, force) {
    if (a === act && !force) return;
    const now = performance.now(), from = a >= 0 ? a : act;
    act = a;
    items.forEach((it, i) => {
      const to = a < 0 ? it.h0 : i === a ? it.h0 + L : it.h0 - L * SINK;
      tset(it.tw, to, now, Math.abs(i - Math.max(from, 0)) * 60);
      it.ped.sil.classList.toggle("hi", i === a);
    });
    note.setAttribute("class", a < 0 ? "dot" : "dot m");
    read.textContent = a < 0 ? "rest" : NAMES[a];
    Bk.wake();
  }

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());
  return { set: (v) => { L = v; if (act >= 0) setActive(act, true); }, destroy: bag.dispose };
}

hairline({
  name: "s2-b2cb2b",
  means: "В B2C один человек выбирает, платит и пользуется, а в B2B это делают разные люди.",
  rules: [1, 2, 5, 10],
  range: [8, 16, 24],
  tour: [[118, 205], [282, 164], [118, 230], null],
  mount,
});
