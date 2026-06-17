/* Scene 03 — neural-net
   A forward pass through a 4-6-6-2 MLP: a wave of activation sweeps left→right,
   pulses travel along the edges, the output neuron lights up in sand. */
(function () {
  'use strict';
  const A = window.Anim, W = A.W, H = A.H, M = A.M;
  let S = null;

  function build() {
    const layers = [4, 6, 6, 2], L = layers.length;
    const x0 = M + 130, x1 = W - M - 130;
    const nodes = layers.map((n, li) => {
      const x = x0 + (x1 - x0) * li / (L - 1), col = [];
      for (let j = 0; j < n; j++) col.push({ x, y: H / 2 + (j - (n - 1) / 2) * 62 });
      return col;
    });
    return { L, nodes };
  }

  function draw(ctx, t, env) {
    if (!S) S = build();
    const P = env.P, L = S.L, seg = 0.78 / (L - 1);

    for (let li = 0; li < L - 1; li++) {
      const a = S.nodes[li], b = S.nodes[li + 1];
      const local = (t - 0.06 - li * seg) / seg;
      for (const s of a) for (const d of b) {
        ctx.strokeStyle = P.dim; ctx.globalAlpha = 0.12; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(s.x, s.y); ctx.lineTo(d.x, d.y); ctx.stroke();
        if (local > 0 && local < 1) {
          const px = s.x + (d.x - s.x) * local, py = s.y + (d.y - s.y) * local;
          env.dot(ctx, px, py, 2, P.clay, 0.6 * (1 - Math.abs(local - 0.5) * 1.4));
        }
      }
    }
    ctx.globalAlpha = 1;

    for (let li = 0; li < L; li++) {
      const act = env.bump(t, 0.06 + li * seg, 0.1), lastLayer = li === L - 1;
      const col = lastLayer ? P.sand : P.teal;
      for (const nd of S.nodes[li]) {
        if (act > 0.05) env.glow(ctx, nd.x, nd.y, 14, col, 0.6 * act);
        env.dot(ctx, nd.x, nd.y, 4, act > 0.1 ? col : P.dim, 0.45 + 0.55 * act);
      }
    }
  }

  A.register('03', 'neural-net · forward pass', draw);
})();
