/* Scene 07 — gmm-density
   Three Gaussian components breathe and re-fit their points (E/M steps), drawn
   as concentric density ellipses. Nods to the from-scratch GMM project. */
(function () {
  'use strict';
  const A = window.Anim, W = A.W, H = A.H;
  let S = null;

  function build(env) {
    const rnd = env.rng(33), K = 3;
    const comp = [
      { x: 0.36 * W, y: 0.45 * H, rx: 92, ry: 64, rot: -0.4, key: 'teal' },
      { x: 0.62 * W, y: 0.62 * H, rx: 82, ry: 60, rot: 0.3, key: 'clay' },
      { x: 0.71 * W, y: 0.35 * H, rx: 72, ry: 54, rot: 0.1, key: 'sand' },
    ];
    const pts = [];
    for (let i = 0; i < 72; i++) {
      const c = comp[i % K];
      pts.push({ x: c.x + env.gauss(rnd) * c.rx * 0.7, y: c.y + env.gauss(rnd) * c.ry * 0.7, key: c.key });
    }
    return { comp, pts, K };
  }

  function draw(ctx, t, env) {
    if (!S) S = build(env);
    const P = env.P, w = 2 * Math.PI * t;

    for (const p of S.pts) env.dot(ctx, p.x, p.y, 2.2, P[p.key], 0.7);

    for (const c of S.comp) {
      const pulse = 1 + 0.07 * Math.sin(w + c.rot);
      const rot = c.rot + 0.06 * Math.sin(w);
      env.glow(ctx, c.x, c.y, 32, P[c.key], 0.16);
      for (let r = 3; r >= 1; r--) {
        ctx.save(); ctx.translate(c.x, c.y); ctx.rotate(rot);
        ctx.strokeStyle = P[c.key]; ctx.globalAlpha = 0.12 * r; ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.ellipse(0, 0, (c.rx * pulse * r) / 2.2, (c.ry * pulse * r) / 2.2, 0, 0, Math.PI * 2);
        ctx.stroke(); ctx.restore();
      }
      ctx.globalAlpha = 1;
      env.dot(ctx, c.x, c.y, 3, P[c.key], 0.9);
    }
  }

  A.register('07', 'gmm-density · mixture (EM)', draw);
})();
