/**
 * Persona: an ID badge hanging from a lanyard clip, its photo window and name
 * lines on the face, and three interview cards fanned out behind it. The card
 * under the pointer slides out from behind the badge along its own lean; the
 * other cards follow a little, staggered outwards. Over the badge the read-out
 * says the persona. The photo window is the bright mark at rest. The slider is
 * how far a card slides out.
 */
const { Cam, clamp, fit, open, poly, proj, rad, rrect, tween, tset, tval, tdone, mk, place, pointer, register, disposer } = HL;

const BW = 52, BH = 72, CW = 42, CH = 90, PX = BW / 2, PZ = 6, BT = 2;
const CARDS = [{ y: -13, th: -34 }, { y: -9, th: -9 }, { y: -5, th: 22 }];
const OUTMAX = 38;
const BADGE = rrect(0, 0, BW, BH, 6, 5), CARD = rrect(-CW / 2, 0, CW / 2, CH, 4, 4);
const WIN = rrect(9, 30, 43, 62, 4, 4), SLOT = rrect(18, 64, 34, 67.4, 1.7, 3);

/** A point (x, z) on the upright plane at depth y. */
const onPlane = (P, y) => (x, z) => P(x, y, z);
/** Card point (u, v) when the card leans th degrees round the pivot and has slid `out` along its lean. */
function cardPt(th, out, u, v) {
  const s = Math.sin(rad(th)), c = Math.cos(rad(th)), w = v + out;
  return [PX + u * c + w * s, PZ - u * s + w * c];
}

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let out = value;

  const C = Cam(45, 0.5, 2.1);
  const ext = [[0, 0, 0], [BW, 0, 0], [0, 0, BH + 40], [BW, 0, BH + 40]];
  for (const cd of CARDS) for (const [u, v] of [[-CW / 2, CH], [CW / 2, CH], [-CW / 2, 0], [CW / 2, 0]]) {
    const [x, z] = cardPt(cd.th, OUTMAX, u, v);
    ext.push([x, cd.y, z]);
  }
  fit(C, ext, 200, 160);
  const P = proj(C);
  const g = mk("g", {}, svg);

  // the cards, the farthest first: a thin back edge, the face, written lines, and its number in dots at the top
  const cards = CARDS.map((cd, i) => {
    const grp = mk("g", {}, g);
    const back = mk("path", { class: "lo" }, grp), face = mk("path", { class: "sil" }, grp), lines = mk("path", { class: "nf lo" }, grp);
    const dots = [];
    for (let k = 0; k <= i; k++) dots.push(mk("circle", { r: 1.1, class: "dot m" }, grp));
    return { ...cd, i, back, face, lines, dots, o: tween(0) };
  });

  // the lanyard: a strap rising from a ring, and the clip that holds the badge
  const strap = mk("path", {}, g);
  const B0 = onPlane(P, 0), Bb = onPlane(P, -BT), S1 = onPlane(P, 1);
  mk("path", { class: "lo", d: poly(BADGE.map((q) => Bb(q.u, q.v))) }, g);
  const face = mk("path", { class: "sil", d: poly(BADGE.map((q) => B0(q.u, q.v))) }, g);
  const win = mk("path", { class: "nf hi", d: poly(WIN.map((q) => B0(q.u, q.v))) }, g);
  const head = [];
  for (let k = 0; k <= 24; k++) { const a = (k / 24) * Math.PI * 2; head.push(B0(26 + 6 * Math.cos(a), 50 + 6.5 * Math.sin(a))); }
  const sh = [];
  for (let k = 0; k <= 12; k++) { const a = Math.PI * (k / 12); sh.push(B0(26 + 12 * Math.cos(a), 30 + 10 * Math.sin(a))); }
  mk("path", { class: "nf lo", d: poly(head) + open(sh) }, g);
  mk("path", { class: "nf lo", d: [[9, 22, 40], [9, 15, 32], [9, 8, 36]].map(([a, z, b]) => open([B0(a, z), B0(b, z)])).join("") }, g);
  mk("path", { class: "nf", d: poly(SLOT.map((q) => B0(q.u, q.v))) }, g);
  // the clip over the slot, then the ring it hangs from
  const CLIP = rrect(20, 62, 32, BH + 9, 3, 4);
  mk("path", { class: "lo", d: poly(CLIP.map((q) => onPlane(P, 0.6)(q.u, q.v))) }, g);
  mk("path", { class: "sil", d: poly(CLIP.map((q) => onPlane(P, 1.8)(q.u, q.v))) }, g);
  const ring = [];
  for (let k = 0; k <= 24; k++) { const a = (k / 24) * Math.PI * 2; ring.push(S1(26 + 5 * Math.cos(a), BH + 13 + 5 * Math.sin(a))); }
  mk("path", { class: "nf", d: poly(ring) }, g);
  strap.setAttribute("d", poly([S1(23, BH + 18.5), S1(19, BH + 40), S1(33, BH + 40), S1(29, BH + 18.5)]));

  function drawCard(cd, now) {
    const o = tval(cd.o, now), W = onPlane(P, cd.y), Wb = onPlane(P, cd.y - 1);
    const at = (u, v) => cardPt(cd.th, o, u, v);
    cd.back.setAttribute("d", poly(CARD.map((q) => Wb(...at(q.u, q.v)))));
    cd.face.setAttribute("d", poly(CARD.map((q) => W(...at(q.u, q.v)))));
    cd.lines.setAttribute("d", [76, 68, 60, 52, 44].map((v, k) => open([W(...at(-15, v)), W(...at(k % 2 ? 6 : 13, v))])).join(""));
    cd.dots.forEach((el, k) => place(el, W(...at(-14 + k * 4, CH - 6))));
  }

  const B = register(stage, (_dt, now) => {
    let moving = false;
    for (const cd of cards) { drawCard(cd, now); if (!tdone(cd.o, now)) moving = true; }
    return moving;
  });
  bag.add(B.unregister);

  // The plane's axes on screen, to read a pointer back into (x, z) on an upright plane.
  const O = P(0, 0, 0), ex = P(1, 0, 0), ez = P(0, 0, 1), ey = P(0, 1, 0);
  const ax = [ex[0] - O[0], ex[1] - O[1]], az = [ez[0] - O[0], ez[1] - O[1]], ay = [ey[0] - O[0], ey[1] - O[1]];
  const det = ax[0] * az[1] - ax[1] * az[0];
  function back([sx, sy], y) {
    const qx = sx - O[0] - y * ay[0], qy = sy - O[1] - y * ay[1];
    return [(qx * az[1] - qy * az[0]) / det, (ax[0] * qy - ax[1] * qx) / det];
  }

  let act = -1;
  /** -2 is the badge; a card is picked by its resting lean round the pivot, or by its slid-out pose while it is the one out. */
  function hit(p) {
    const [x, z] = back(p, 0);
    if ((x > -2 && x < BW + 2 && z > -2 && z < BH + 2) || (x > 18 && x < 34 && z < BH + 20 && z > 0)) return -2;
    const [cx, cz] = back(p, -9), r = Math.hypot(cx - PX, cz - PZ);
    if (cz < PZ) return -1;
    const ang = Math.atan2(cx - PX, cz - PZ) * 180 / Math.PI;
    let best = -1, bd = Infinity;
    CARDS.forEach((cd, i) => { const d = Math.abs(ang - cd.th); if (d < bd) { bd = d; best = i; } });
    const reach = CH + 6 + (best === act ? out : 0);
    return bd < 16 && r < reach ? best : -1;
  }

  function setActive(a, force) {
    if (a === act && !force) return;
    const now = performance.now(), from = a >= 0 ? a : act >= 0 ? act : 1;
    act = a;
    for (const cd of cards) {
      const d = Math.abs(cd.i - from);
      tset(cd.o, a < 0 ? 0 : cd.i === a ? out : out * 0.14, now, d * 45);
      cd.face.classList.toggle("hi", cd.i === a);
    }
    face.classList.toggle("hi", a === -2);
    win.setAttribute("class", a === -1 || a === -2 ? "nf hi" : "nf");
    read.textContent = a === -1 ? "rest" : a === -2 ? "персона" : "интервью " + (a + 1);
    B.wake();
  }

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());
  read.textContent = "rest";

  return {
    set: (v) => { out = clamp(v, 0, OUTMAX); if (act >= 0) setActive(act, true); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "r7-persona",
  means: "Бейдж персоны и три карточки интервью за ним: карточка под курсором выезжает из-за бейджа.",
  rules: [1, 2, 4, 10],
  range: [18, 28, 38],
  tour: [[151, 102], [203, 222], [258, 152], null],
  mount,
});
