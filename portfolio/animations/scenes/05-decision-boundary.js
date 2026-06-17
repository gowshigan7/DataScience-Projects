/* Scene 05 — decision-boundary
   Two classes of points; a boundary rotates from a poor separation to a clean
   one, the half-planes tint, a margin appears in sand. Classification. */
(function () {
  'use strict';
  const A = window.Anim, W = A.W, H = A.H, M = A.M;
  let S = null;

  function build(env) {
    const rnd = env.rng(9), a = [], b = [];
    for (let i = 0; i < 34; i++) a.push({ x: (0.30 + env.gauss(rnd) * 0.07) * W, y: (0.62 + env.gauss(rnd) * 0.10) * H });
    for (let i = 0; i < 34; i++) b.push({ x: (0.66 + env.gauss(rnd) * 0.07) * W, y: (0.40 + env.gauss(rnd) * 0.10) * H });
    return { a, b };
  }

  function draw(ctx, t, env) {
    if (!S) S = build(env);
    const P = env.P, x0 = M, x1 = W - M, midX = W / 2, midY = H / 2;
    const tri = t < 0.5 ? t / 0.5 : (1 - t) / 0.5, k = env.easeInOut(tri);
    const slope = -0.18 - 0.85 * k;
    const by = (x) => midY + slope * (x - midX);

    // tint the half-planes
    ctx.globalAlpha = 0.06 + 0.06 * k;
    ctx.fillStyle = P.clay;
    ctx.beginPath(); ctx.moveTo(x0, M); ctx.lineTo(x1, M); ctx.lineTo(x1, by(x1)); ctx.lineTo(x0, by(x0)); ctx.closePath(); ctx.fill();
    ctx.fillStyle = P.teal;
    ctx.beginPath(); ctx.moveTo(x0, H - M); ctx.lineTo(x1, H - M); ctx.lineTo(x1, by(x1)); ctx.lineTo(x0, by(x0)); ctx.closePath(); ctx.fill();
    ctx.globalAlpha = 1;

    // margin (dashed) + boundary
    const nrm = Math.hypot(slope, 1), off = 26;
    ctx.setLineDash([6, 7]); ctx.strokeStyle = P.sand; ctx.lineWidth = 1; ctx.globalAlpha = 0.45 * k;
    for (const s of [-1, 1]) {
      ctx.beginPath();
      ctx.moveTo(x0, by(x0) + s * off * nrm); ctx.lineTo(x1, by(x1) + s * off * nrm); ctx.stroke();
    }
    ctx.setLineDash([]); ctx.globalAlpha = 1;
    ctx.strokeStyle = P.sand; ctx.lineWidth = 2; ctx.globalAlpha = 0.5 + 0.5 * k;
    ctx.beginPath(); ctx.moveTo(x0, by(x0)); ctx.lineTo(x1, by(x1)); ctx.stroke(); ctx.globalAlpha = 1;

    for (const p of S.a) env.dot(ctx, p.x, p.y, 2.6, P.teal, 0.85);
    for (const p of S.b) env.dot(ctx, p.x, p.y, 2.6, P.clay, 0.85);
  }

  A.register('05', 'decision-boundary · classification', draw);
})();
