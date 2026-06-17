/* Scene 04 — k-means
   Points get assigned to the nearest centroid (recolouring), centroids glide to
   the mean of their members and converge. Unsupervised clustering. Ping-pongs
   so the loop re-scatters seamlessly. */
(function () {
  'use strict';
  const A = window.Anim, W = A.W, H = A.H;
  let S = null;

  function build(env) {
    const rnd = env.rng(5), N = 66, K = 3, keys = ['teal', 'clay', 'sand'];
    const trueC = [[0.34, 0.40], [0.60, 0.66], [0.72, 0.34]];
    const pts = [];
    for (let i = 0; i < N; i++) {
      const c = trueC[i % K];
      pts.push({ x: (c[0] + env.gauss(rnd) * 0.05) * W, y: (c[1] + env.gauss(rnd) * 0.05) * H });
    }
    let cents = [];
    for (let k = 0; k < K; k++) { const r = pts[Math.floor(rnd() * N)]; cents.push({ x: r.x, y: r.y }); }
    const traj = [cents.map((c) => ({ ...c }))], assign = new Array(N).fill(0);
    for (let it = 0; it < 7; it++) {
      for (let i = 0; i < N; i++) {
        let bd = Infinity, bk = 0;
        for (let k = 0; k < K; k++) { const d = (pts[i].x - cents[k].x) ** 2 + (pts[i].y - cents[k].y) ** 2; if (d < bd) { bd = d; bk = k; } }
        assign[i] = bk;
      }
      for (let k = 0; k < K; k++) {
        let sx = 0, sy = 0, c = 0;
        for (let i = 0; i < N; i++) if (assign[i] === k) { sx += pts[i].x; sy += pts[i].y; c++; }
        if (c) cents[k] = { x: sx / c, y: sy / c };
      }
      traj.push(cents.map((c) => ({ ...c })));
    }
    return { pts, traj, assign, K, keys };
  }

  function draw(ctx, t, env) {
    if (!S) S = build(env);
    const P = env.P, T = S.traj.length - 1;
    const phase = t < 0.85 ? t / 0.85 : (1 - t) / 0.15;     // converge then re-scatter
    const conv = env.easeInOut(Math.min(1, phase));
    const cin = env.easeOut(Math.min(1, phase / 0.6));
    const fi = conv * T, idx = Math.floor(fi), fr = fi - idx;
    const cents = S.traj[idx].map((c, k) => {
      const n = S.traj[Math.min(idx + 1, T)][k];
      return { x: c.x + (n.x - c.x) * fr, y: c.y + (n.y - c.y) * fr };
    });

    for (let i = 0; i < S.pts.length; i++) {
      const k = S.assign[i], col = P[S.keys[k]];
      ctx.strokeStyle = col; ctx.globalAlpha = 0.10 * cin; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(S.pts[i].x, S.pts[i].y); ctx.lineTo(cents[k].x, cents[k].y); ctx.stroke();
      ctx.globalAlpha = 1;
      env.dot(ctx, S.pts[i].x, S.pts[i].y, 2.4, cin > 0.5 ? col : P.dim, 0.72);
    }
    for (let k = 0; k < S.K; k++) {
      const col = P[S.keys[k]];
      env.glow(ctx, cents[k].x, cents[k].y, 16, col, 0.45);
      ctx.strokeStyle = col; ctx.globalAlpha = 0.9; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(cents[k].x, cents[k].y, 7, 0, Math.PI * 2); ctx.stroke();
      ctx.globalAlpha = 1;
      env.dot(ctx, cents[k].x, cents[k].y, 2.5, col, 1);
    }
  }

  A.register('04', 'k-means · clustering', draw);
})();
