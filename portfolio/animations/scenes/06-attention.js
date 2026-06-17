/* Scene 06 — attention
   A query scans a row of tokens; weighted attention arcs fan out, the dominant
   attended token lights up in sand. Transformer / LLM attention. */
(function () {
  'use strict';
  const A = window.Anim, W = A.W, H = A.H, M = A.M;
  let S = null;

  function build(env) {
    const rnd = env.rng(14), N = 9, y = H * 0.6, x0 = M + 90, x1 = W - M - 90;
    const toks = [];
    for (let i = 0; i < N; i++) toks.push({ x: x0 + (x1 - x0) * i / (N - 1), y });
    const Wt = [];
    for (let i = 0; i < N; i++) {
      const row = []; let s = 0;
      for (let j = 0; j < N; j++) { const w = Math.exp(-Math.abs(i - j) * 0.5) * (0.4 + rnd()); row.push(w); s += w; }
      for (let j = 0; j < N; j++) row[j] /= s;
      Wt.push(row);
    }
    return { N, toks, Wt };
  }

  function draw(ctx, t, env) {
    if (!S) S = build(env);
    const P = env.P, N = S.N, q = Math.floor(((t % 1) + 1) % 1 * N) % N;
    const row = S.Wt[q];
    let best = 0; for (let j = 0; j < N; j++) if (row[j] > row[best]) best = j;

    // arcs from the query token
    for (let j = 0; j < N; j++) {
      if (j === q) continue;
      const a = S.toks[q], b = S.toks[j];
      const mx = (a.x + b.x) / 2, my = a.y - Math.abs(a.x - b.x) * 0.4 - 24;
      ctx.strokeStyle = j === best ? P.sand : P.teal;
      ctx.globalAlpha = Math.min(0.9, row[j] * 2.2);
      ctx.lineWidth = Math.max(0.6, row[j] * 11);
      ctx.beginPath(); ctx.moveTo(a.x, a.y - 16); ctx.quadraticCurveTo(mx, my, b.x, b.y - 16); ctx.stroke();
    }
    ctx.globalAlpha = 1;

    // tokens
    for (let i = 0; i < N; i++) {
      const tk = S.toks[i], isQ = i === q, isBest = i === best;
      if (isBest) env.glow(ctx, tk.x, tk.y, 16, P.sand, 0.5);
      ctx.fillStyle = isQ ? P.teal : isBest ? P.sand : P.dim;
      ctx.globalAlpha = isQ || isBest ? 1 : 0.55;
      ctx.fillRect(tk.x - 6, tk.y - 16, 12, 32);
      ctx.globalAlpha = 1;
    }
  }

  A.register('06', 'attention · transformer', draw);
})();
