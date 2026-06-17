/* Scene 02 — gradient-descent
   A point descends the loss contours, zig-zagging with momentum, settling into
   the global minimum (which pulses in sand). Optimisation / model training. */
(function () {
  'use strict';
  const A = window.Anim, W = A.W, H = A.H;
  let S = null;

  function build(env) {
    const min = { x: 0.60 * W, y: 0.60 * H };
    const start = { x: 0.26 * W, y: 0.24 * H };
    const steps = 16, path = [];
    const ang = Math.atan2(min.y - start.y, min.x - start.x) + Math.PI / 2;
    for (let i = 0; i <= steps; i++) {
      const f = env.easeInOut(i / steps);
      const tx = start.x + (min.x - start.x) * f;
      const ty = start.y + (min.y - start.y) * f;
      const perp = Math.sin((i / steps) * Math.PI * 5) * (1 - i / steps) * 44;
      path.push({ x: tx + Math.cos(ang) * perp, y: ty + Math.sin(ang) * perp });
    }
    return { min, start, path };
  }

  function draw(ctx, t, env) {
    if (!S) S = build(env);
    const P = env.P, path = S.path, last = path.length - 1;

    // loss contours
    ctx.lineWidth = 1;
    for (let r = 7; r >= 1; r--) {
      ctx.strokeStyle = P.dim; ctx.globalAlpha = 0.12 + 0.03 * (8 - r);
      ctx.beginPath();
      ctx.ellipse(S.min.x, S.min.y, r * 46, r * 34, -0.5, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.globalAlpha = 1;

    const prog = env.easeInOut(Math.min(1, t / 0.8));
    const fi = prog * last, idx = Math.floor(fi), fr = fi - idx;
    const nx = path[Math.min(idx + 1, last)];
    const cur = { x: path[idx].x + (nx.x - path[idx].x) * fr, y: path[idx].y + (nx.y - path[idx].y) * fr };
    const fade = 1 - env.easeOut(Math.max(0, (t - 0.93) / 0.07));

    // trail
    ctx.strokeStyle = P.teal; ctx.lineWidth = 1.5; ctx.globalAlpha = 0.5 * fade;
    ctx.beginPath(); ctx.moveTo(path[0].x, path[0].y);
    for (let i = 1; i <= idx; i++) ctx.lineTo(path[i].x, path[i].y);
    ctx.lineTo(cur.x, cur.y); ctx.stroke(); ctx.globalAlpha = 1;
    for (let i = 0; i <= idx; i++) env.dot(ctx, path[i].x, path[i].y, 2, P.teal, 0.35 * fade);

    // minimum + descending ball
    const arrived = env.bump(t, 0.86, 0.1);
    env.glow(ctx, S.min.x, S.min.y, 18, P.sand, 0.25 + 0.55 * arrived);
    env.dot(ctx, S.min.x, S.min.y, 3, P.sand, 0.7);
    env.glow(ctx, cur.x, cur.y, 16, P.teal, 0.5 * fade);
    env.dot(ctx, cur.x, cur.y, 5, P.teal, fade);
  }

  A.register('02', 'gradient-descent · optimisation', draw);
})();
