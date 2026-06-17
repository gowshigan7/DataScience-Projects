/* Scene 08 — sorting
   Selection sort visualised: bars settle into order one by one. Placed bars turn
   sand, the current scan is teal. Ping-pongs so the loop re-shuffles. CS basics. */
(function () {
  'use strict';
  const A = window.Anim, W = A.W, H = A.H, M = A.M;
  let S = null;

  function build(env) {
    const rnd = env.rng(8), n = 26, a = [];
    for (let i = 0; i < n; i++) a[i] = 0.15 + rnd() * 0.72;
    const states = [a.slice()];
    for (let i = 0; i < n; i++) {
      let m = i;
      for (let j = i + 1; j < n; j++) if (a[j] < a[m]) m = j;
      const tmp = a[i]; a[i] = a[m]; a[m] = tmp;
      states.push(a.slice());
    }
    return { n, states };
  }

  function draw(ctx, t, env) {
    if (!S) S = build(env);
    const P = env.P, n = S.n, T = S.states.length - 1;
    const phase = t < 0.85 ? t / 0.85 : (1 - t) / 0.15;
    const fi = env.easeInOut(Math.min(1, phase)) * T, idx = Math.floor(fi), fr = fi - idx;
    const a = S.states[idx], b = S.states[Math.min(idx + 1, T)];
    const x0 = M + 8, x1 = W - M - 8, bw = (x1 - x0) / n, maxH = H - 2 * M - 30, base = H - M - 16;

    for (let i = 0; i < n; i++) {
      const h = (a[i] + (b[i] - a[i]) * fr) * maxH, x = x0 + i * bw, y = base - h;
      let col, al;
      if (i < idx) { col = P.sand; al = 0.8; }
      else if (i === idx) { col = P.teal; al = 0.9; }
      else { col = P.clay; al = 0.45; }
      ctx.fillStyle = col; ctx.globalAlpha = al;
      ctx.fillRect(x + 1.5, y, bw - 3, h);
    }
    ctx.globalAlpha = 1;
  }

  A.register('08', 'sorting · algorithms', draw);
})();
