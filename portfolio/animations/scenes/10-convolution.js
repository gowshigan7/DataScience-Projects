/* Scene 10 — convolution
   A 3x3 kernel slides over an input feature-map; each position writes one output
   cell, revealed in sand. CNN / tensor operation. */
(function () {
  'use strict';
  const A = window.Anim, W = A.W, H = A.H;
  let S = null;

  function build(env) {
    const rnd = env.rng(2), gw = 9, gh = 6, cell = 56;
    const ix = (W - gw * cell) / 2, iy = (H - gh * cell) / 2;
    const vals = [];
    for (let i = 0; i < gw * gh; i++) vals.push(0.2 + rnd() * 0.8);
    return { gw, gh, cell, ix, iy, vals, P: (gw - 2) * (gh - 2) };
  }

  function draw(ctx, t, env) {
    if (!S) S = build(env);
    const P = env.P, { gw, gh, cell, ix, iy } = S;
    const fade = 1 - env.easeOut(Math.max(0, (t - 0.92) / 0.08));

    // input feature-map
    for (let r = 0; r < gh; r++) for (let c = 0; c < gw; c++) {
      const v = S.vals[r * gw + c];
      ctx.fillStyle = P.dim; ctx.globalAlpha = 0.10 + 0.28 * v;
      ctx.fillRect(ix + c * cell + 2, iy + r * cell + 2, cell - 4, cell - 4);
    }
    ctx.globalAlpha = 1;

    const sweep = Math.min(1, t / 0.9) * S.P, cur = Math.floor(sweep), ow = gw - 2;

    // output cells written so far
    for (let k = 0; k <= cur && k < S.P; k++) {
      const oc = k % ow, or = Math.floor(k / ow);
      const cx = ix + (oc + 1) * cell, cy = iy + (or + 1) * cell, age = cur - k;
      ctx.fillStyle = P.sand; ctx.globalAlpha = Math.max(0.22, 0.9 - age * 0.045) * fade;
      ctx.fillRect(cx + 9, cy + 9, cell - 18, cell - 18);
    }
    ctx.globalAlpha = 1;

    // sliding kernel
    if (cur < S.P) {
      const oc = cur % ow, or = Math.floor(cur / ow), kx = ix + oc * cell, ky = iy + or * cell;
      env.glow(ctx, kx + cell * 1.5, ky + cell * 1.5, 34, P.teal, 0.18 * fade);
      ctx.strokeStyle = P.teal; ctx.lineWidth = 2; ctx.globalAlpha = 0.9 * fade;
      ctx.strokeRect(kx + 1, ky + 1, cell * 3 - 2, cell * 3 - 2);
      ctx.globalAlpha = 1;
    }
  }

  A.register('10', 'convolution · CNN kernel', draw);
})();
