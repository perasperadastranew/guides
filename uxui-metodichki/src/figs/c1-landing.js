/**
 * Landing: a long landing page standing upright on a stand, cut into four
 * section plates: the hero with its phone and headline, a row of two stories,
 * a row of three screens, and the footer with its store button. The pointer's
 * height picks a section; it slides out to the side and a little forward,
 * and its neighbours follow less, staggered by distance. The slider is how far
 * the section slides.
 */
const {
  Cam, clamp, fit, poly, proj, rrect, rings, prism, facing, seg, tween, tset, tval, tdone,
  mk, put, solid, pointer, register, disposer,
} = HL;

const W = 112, T = 3.4, G = 3.5, R = 4;
const SEC = [
  { h: 52, word: "обещание" },
  { h: 34, word: "истории" },
  { h: 34, word: "экраны" },
  { h: 24, word: "скачать" },
];
const REST = [9, 3, 0, 4], FOLLOW = [1, 0.22, 0.08, 0.04], FWD = 0.25, STEP = 45;
// section bottoms, from the top section down
let acc = 0;
for (let i = SEC.length - 1; i >= 0; i--) { SEC[i].z0 = acc; acc += SEC[i].h + G; }
const TOP = acc - G;

/** A rounded rectangle in the section's face plane, as [u, v] points. */
const box = (u0, v0, u1, v1, r) => rrect(u0, v0, u1, v1, r, 4).map((q) => [q.u, q.v]);

/** What each section carries on its face, in its own [u, v]: [points, closed, dim]. */
function content(i, h) {
  const out = [];
  const add = (pts, closed, dim) => out.push([pts, closed, dim]);
  const line = (u0, u1, v, dim) => add([[u0, v], [u1, v]], false, dim);
  if (i === 0) {
    add(box(76, 6, 100, 46, 4.5), true, false);          // the phone in the hero
    add(box(78.6, 9, 97.4, 43, 2.6), true, true);
    line(85, 91, 44.4, true);
    add(box(10, 34, 62, 40, 3), true, false);            // the headline, two bars
    add(box(10, 25, 50, 31, 3), true, false);
    line(10, 44, 18, true);
    add(box(10, 6, 34, 13, 3.5), true, false);           // the call to action
  } else if (i === 1) {
    for (const u of [6, 59]) {                           // two stories: a face and two lines
      add(box(u, 5, u + 47, h - 5, 3), true, true);
      add(box(u + 5, 10, u + 17, 22, 6), true, false);
      line(u + 22, u + 42, 20, false);
      line(u + 22, u + 36, 13, true);
    }
  } else if (i === 2) {
    for (const u of [14, 48, 82]) {                      // three screens
      add(box(u, 4, u + 17, h - 4, 3), true, false);
      line(u + 6, u + 11, h - 6.5, true);
    }
  } else {
    add(box(37, 6, 75, h - 6, 5), true, false);          // the store button
    add(box(41, 9.5, 49, h - 9.5, 2.5), true, true);
    line(53, 70, h / 2, true);
    for (const u of [10, 17, 24, 88, 95, 102]) line(u, u + 2, h / 2, true);
  }
  return out;
}

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let D = value;
  const C = Cam(45, 0.5, 1.46);
  fit(C, [[-12, -16, -7], [W + 12, 14, -7], [-12, -16, TOP], [W + 52, 14, TOP], [W + 52, 14, 0], [-12, 14, -7]], 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  const [br, bi] = rings(-12, -16, W + 12, 14, 7, 2);
  put(solid(g), prism(P, front, br, bi, -7, 0));
  // the slot the page stands in
  const [sr, si] = rings(-4, -T - 3, W + 4, 3, 2.5, 1);
  put(solid(g), prism(P, front, sr, si, 0, 2.5));

  const secs = SEC.map((s, i) => {
    const grp = mk("g", {}, g);
    const back = mk("path", { class: "lo" }, grp), face = mk("path", { class: "sil" }, grp);
    const full = mk("path", { class: "nf" }, grp), dim = mk("path", { class: "nf lo" }, grp);
    return { ...s, i, grp, back, face, full, dim, items: content(i, s.h), x: tween(REST[i]), y: tween(0), last: "" };
  });

  function draw(s, x, y) {
    const key = x.toFixed(2) + "," + y.toFixed(2);
    if (key === s.last) return;
    s.last = key;
    const at = (u, v, d) => P(u + x, y - d, s.z0 + v);
    const out = box(0, 0, W, s.h, R);
    s.back.setAttribute("d", poly(out.map((p) => at(p[0], p[1], T))));
    s.face.setAttribute("d", poly(out.map((p) => at(p[0], p[1], 0))));
    let a = "", b = "";
    for (const [pts, closed, dimmed] of s.items) {
      const q = pts.map((p) => at(p[0], p[1], 0));
      const d = closed ? poly(q) : seg(q[0], q[1]);
      if (dimmed) b += d; else a += d;
    }
    s.full.setAttribute("d", a);
    s.dim.setAttribute("d", b);
  }

  let order = "";
  const B = register(stage, (_dt, now) => {
    let moving = false;
    for (const s of secs) {
      draw(s, tval(s.x, now), tval(s.y, now));
      if (!tdone(s.x, now) || !tdone(s.y, now)) moving = true;
    }
    // the section further forward is nearer: paint it last
    const sorted = secs.slice().sort((p, q) => tval(p.y, now) - tval(q.y, now) || p.i - q.i);
    const key = sorted.map((s) => s.i).join("");
    if (key !== order) { order = key; for (const s of sorted) g.appendChild(s.grp); }
    return moving;
  });
  bag.add(B.unregister);

  // hit test: the pointer on the page's resting face plane (y = 0), which never moves; its height picks the section.
  const zf = Math.sqrt(1 - 0.25), o = P(0, 0, 0), ux = P(1, 0, 0);
  function hit([sx, sy]) {
    const x = (sx - o[0]) / (ux[0] - o[0]);
    const z = (o[1] + x * (ux[1] - o[1]) - sy) / (C.S * zf);
    if (x < -14 || x > W + 62 || z < -6 || z > TOP + 6) return -1;
    let best = 0, bd = 1e9;
    secs.forEach((s, i) => { const d = Math.abs(z - (s.z0 + s.h / 2)); if (d < bd) { bd = d; best = i; } });
    return best;
  }

  let act = -2;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = a >= 0 ? a : Math.max(act, 0);
    act = a;
    secs.forEach((s, i) => {
      const k = Math.abs(i - from), out = a < 0 ? REST[i] : D * FOLLOW[Math.min(k, 3)];
      tset(s.x, out, now, k * STEP);
      tset(s.y, a < 0 ? 0 : out * FWD, now, k * STEP);
      s.face.classList.toggle("hi", a < 0 ? i === 0 : i === a);
    });
    read.textContent = a < 0 ? "rest" : SEC[a].word;
    B.wake();
  }
  setActive(-1);

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());

  return {
    set: (v) => { D = clamp(v, 0, 52); const a = act; act = -2; setActive(a); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "c1-landing",
  means: "Лендинг как стопка секций: обещание, истории, экраны и кнопка скачать; секция под указателем выезжает вбок.",
  rules: [1, 2, 5, 10],
  range: [24, 38, 52],
  tour: [[150, 90], [170, 170], [190, 230], null],
  mount,
});
