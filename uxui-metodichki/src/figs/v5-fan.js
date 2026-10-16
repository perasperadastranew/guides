/**
 * Fan: a paint swatch fan deck lying on the table, six long strips stacked on
 * one bolt and fanned out unevenly, as a hand leaves them. Each strip is cut
 * into chips across its length, and the bolt goes through the round ends. The
 * strip under the pointer takes the bright edge and the strips on either side
 * swing away from it, staggered outwards, so it stands alone in the fan. At
 * rest the accent strip is bright. The slider is how far the others part.
 */
const {
  Cam, fit, proj, facing, prism, rrect, unproj, seg, clamp,
  tween, tset, tval, tdone, mk, solid, put, pointer, register, disposer, rad,
} = HL;

const N = 6, L = 120, HW = 10, TK = 2.2, DZ = 2.8, STEP = 45, BOLT = 4.6;
const REST = [-96, -78, -61, -44, -26, -8];
const CHIPS = [44, 63, 82, 101];
const NAMES = ["основной", "фон", "текст", "акцент", "успех", "ошибка"];
const ACCENT = 3;

/** A ring turned by phi degrees about the bolt: positions and normals. */
function turn(ring, phi) {
  const c = Math.cos(rad(phi)), s = Math.sin(rad(phi));
  return ring.map((q) => ({ u: q.u * c - q.v * s, v: q.u * s + q.v * c, nu: q.nu * c - q.nv * s, nv: q.nu * s + q.nv * c }));
}
const at = (u, v, phi) => [u * Math.cos(rad(phi)) - v * Math.sin(rad(phi)), u * Math.sin(rad(phi)) + v * Math.cos(rad(phi))];

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let PART = value;

  const ring = rrect(-HW, -HW, L, HW, HW - 0.5, 6), inner = rrect(-HW + 1.3, -HW + 1.3, L - 1.3, HW - 1.3, HW - 1.8, 6);
  const C = Cam(45, 0.5, 2.1);
  const ext = [];
  for (const phi of [REST[0] - 22, REST[0], REST[N - 1], REST[N - 1] + 22]) for (const q of turn(ring, phi)) ext.push([q.u, q.v, 0], [q.u, q.v, N * DZ + 4]);
  fit(C, ext, 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  // bottom strip first: the deck is a stack, so its paint order is its height
  const strips = REST.map((phi, i) => {
    const el = solid(g), chips = mk("path", { class: "nf lo" }, g);
    return { phi, z0: i * DZ, el, chips, a: tween(phi), drawn: NaN };
  });
  // the bolt through the round ends, with a cap
  const bolt = solid(g);
  const bz = (N - 1) * DZ + TK;
  put(bolt, prism(P, front, rrect(-BOLT, -BOLT, BOLT, BOLT, BOLT, 6), rrect(-BOLT + 1, -BOLT + 1, BOLT - 1, BOLT - 1, BOLT - 1, 6), -0.5, bz + 2.4));

  function draw(s, phi) {
    if (phi === s.drawn) return;
    s.drawn = phi;
    const z1 = s.z0 + TK;
    put(s.el, prism(P, front, turn(ring, phi), turn(inner, phi), s.z0, z1));
    s.chips.setAttribute("d", CHIPS.map((u) => seg(P(...at(u, -HW + 1.3, phi), z1), P(...at(u, HW - 1.3, phi), z1))).join(""));
  }

  const B = register(stage, (_dt, now) => {
    let m = false;
    for (const s of strips) { draw(s, tval(s.a, now)); if (!tdone(s.a, now)) m = true; }
    return m;
  });
  bag.add(B.unregister);

  // hit: the pointer on the deck's middle plane, read as an angle round the bolt, against the REST angles
  function hit([sx, sy]) {
    const [x, y] = unproj(C, sx, sy, (N * DZ) / 2), r = Math.hypot(x, y);
    if (r < BOLT + 6 || r > L + 10) return -1;
    const phi = (Math.atan2(y, x) * 180) / Math.PI;
    let best = -1, bd = 12;
    REST.forEach((p, i) => { const d = Math.abs(phi - p); if (d < bd) { bd = d; best = i; } });
    return best;
  }

  let act = -1;
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = a >= 0 ? a : act >= 0 ? act : 0;
    act = a;
    strips.forEach((s, i) => {
      const k = Math.abs(i - from), push = a < 0 || k === 0 ? 0 : PART * clamp(1.15 - 0.15 * k, 0.5, 1);
      tset(s.a, s.phi + (i < a ? -push : push), now, k * STEP);
      s.el.sil.classList.toggle("hi", a < 0 ? i === ACCENT : i === a);
    });
    read.textContent = a < 0 ? "rest" : NAMES[a];
    B.wake();
  }
  strips[ACCENT].el.sil.classList.add("hi");
  read.textContent = "rest";

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());

  return {
    set: (v) => { PART = v; const a = act; act = -2; setActive(a); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "v5-fan",
  means: "Веер образцов цвета на одном болте: полоска под указателем остаётся, соседние расходятся от неё по очереди.",
  rules: [1, 2, 4, 5],
  range: [8, 14, 22],
  tour: [[226, 112], [296, 173], [258, 219], null],
  mount,
});
