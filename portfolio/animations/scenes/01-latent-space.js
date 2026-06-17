/* Scene 01 — latent-space
   Embeddings drift in their clusters; once per loop a query fires a ring and
   pulls its k nearest neighbours (they light up in sand). Nods to RAG retrieval
   + the latent-space hero signature. Deterministic & seamlessly looping. */
(function () {
  'use strict';
  const W = window.Anim.W, H = window.Anim.H;
  let S = null;

  function build(env) {
    const rnd = env.rng(7);
    const centers = [
      { x: 0.40 * W, y: 0.45 * H, key: 'teal' },
      { x: 0.64 * W, y: 0.63 * H, key: 'clay' },
      { x: 0.76 * W, y: 0.34 * H, key: 'sand' },
    ];
    const N = 72, K = 7;
    const pts = [];
    for (let i = 0; i < N; i++) {
      const ci = i % 3, c = centers[ci];
      pts.push({
        ci, key: c.key,
        hx: c.x + env.gauss(rnd) * 46,
        hy: c.y + env.gauss(rnd) * 40,
        phase: rnd() * Math.PI * 2,
        amp: 3 + rnd() * 5,
        spin: 0.6 + rnd() * 0.8,
      });
    }
    const q = { x: 0.55 * W, y: 0.48 * H };
    const knn = pts
      .map((p, i) => ({ i, d: Math.hypot(p.hx - q.x, p.hy - q.y) }))
      .sort((a, b) => a.d - b.d).slice(0, K).map((o) => o.i);
    const knnSet = new Set(knn);
    return { centers, pts, q, knn, knnSet, maxR: 320 };
  }

  function draw(ctx, t, env) {
    if (!S) S = build(env);
    const P = env.P;
    const pos = S.pts.map((p) => ({
      x: p.hx + Math.cos(p.phase + p.spin * 2 * Math.PI * t) * p.amp,
      y: p.hy + Math.sin(p.phase + p.spin * 2 * Math.PI * t) * p.amp,
    }));

    // intra-cluster links (the "neighbourhood" graph)
    ctx.lineWidth = 1;
    for (let i = 0; i < S.pts.length; i++) {
      for (let j = i + 1; j < S.pts.length; j++) {
        if (S.pts[i].ci !== S.pts[j].ci) continue;
        const dx = pos[i].x - pos[j].x, dy = pos[i].y - pos[j].y;
        const d2 = dx * dx + dy * dy;
        if (d2 < 5200) {
          ctx.strokeStyle = P[S.pts[i].key];
          ctx.globalAlpha = 0.12 * (1 - d2 / 5200);
          ctx.beginPath(); ctx.moveTo(pos[i].x, pos[i].y); ctx.lineTo(pos[j].x, pos[j].y); ctx.stroke();
        }
      }
    }
    ctx.globalAlpha = 1;

    // expanding query ring (t 0.25 → 0.75)
    const ringT = env.easeOut((t - 0.25) / 0.5);
    if (ringT > 0 && ringT < 1) {
      ctx.strokeStyle = P.teal; ctx.lineWidth = 1.5;
      ctx.globalAlpha = 0.5 * (1 - ringT);
      ctx.beginPath(); ctx.arc(S.q.x, S.q.y, ringT * S.maxR, 0, Math.PI * 2); ctx.stroke();
      ctx.globalAlpha = 1;
    }

    // highlight beat for the k nearest neighbours
    const hi = env.bump(t, 0.62, 0.13);

    // base points
    for (let i = 0; i < S.pts.length; i++) {
      const isHi = S.knnSet.has(i);
      if (isHi && hi > 0.02) {
        env.glow(ctx, pos[i].x, pos[i].y, 14, P.sand, 0.5 * hi);
        ctx.strokeStyle = P.sand; ctx.globalAlpha = 0.5 * hi; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(S.q.x, S.q.y); ctx.lineTo(pos[i].x, pos[i].y); ctx.stroke();
        ctx.globalAlpha = 1;
        env.dot(ctx, pos[i].x, pos[i].y, 3.4, P.sand, 0.85 + 0.15 * hi);
      } else {
        env.dot(ctx, pos[i].x, pos[i].y, 2.2, P[S.pts[i].key], 0.78);
      }
    }

    // the query point itself
    env.glow(ctx, S.q.x, S.q.y, 22, P.teal, 0.45 + 0.3 * hi);
    env.dot(ctx, S.q.x, S.q.y, 4.4, P.teal, 1);
  }

  window.Anim.register('01', 'latent-space · embeddings & retrieval', draw);
})();
