/* Scene 09 — graph-search
   A BFS wavefront spreads from the source across a node graph; once it reaches
   the far node, the shortest path lights up in sand. Graphs / distributed. */
(function () {
  'use strict';
  const A = window.Anim, W = A.W, H = A.H;
  let S = null;

  function build(env) {
    const rnd = env.rng(12), N = 15, nodes = [];
    for (let i = 0; i < N; i++) nodes.push({ x: (0.14 + rnd() * 0.72) * W, y: (0.18 + rnd() * 0.62) * H });
    const d2 = (i, j) => (nodes[i].x - nodes[j].x) ** 2 + (nodes[i].y - nodes[j].y) ** 2;
    const adj = Array.from({ length: N }, () => []), edges = [];
    const add = (i, j) => { if (i !== j && !adj[i].includes(j)) { adj[i].push(j); adj[j].push(i); edges.push([i, j]); } };
    // spanning tree → guarantees a single connected component
    for (let i = 1; i < N; i++) {
      let best = 0, bd = Infinity;
      for (let j = 0; j < i; j++) { const d = d2(i, j); if (d < bd) { bd = d; best = j; } }
      add(i, best);
    }
    // a couple of nearest-neighbour extras for richness
    for (let i = 0; i < N; i++) {
      const near = nodes.map((n, j) => ({ j, d: d2(i, j) })).filter((o) => o.j !== i).sort((a, b) => a.d - b.d).slice(0, 2);
      for (const o of near) add(i, o.j);
    }
    let src = 0; for (let i = 1; i < N; i++) if (nodes[i].x < nodes[src].x) src = i;
    const dist = Array(N).fill(Infinity), par = Array(N).fill(-1);
    dist[src] = 0; const q = [src];
    while (q.length) { const u = q.shift(); for (const v of adj[u]) if (dist[v] === Infinity) { dist[v] = dist[u] + 1; par[v] = u; q.push(v); } }
    let tgt = 0; for (let i = 0; i < N; i++) if (isFinite(dist[i]) && dist[i] > dist[tgt]) tgt = i;
    const path = []; for (let c = tgt; c !== -1; c = par[c]) path.push(c);
    const maxD = Math.max(...dist.filter(isFinite));
    return { N, nodes, edges, dist, src, tgt, path, maxD };
  }

  function draw(ctx, t, env) {
    if (!S) S = build(env);
    const P = env.P;
    const g = t < 0.78 ? t / 0.78 : (1 - t) / 0.22;
    const front = env.easeOut(Math.min(1, g)) * (S.maxD + 0.6);
    const pathHi = env.bump(t, 0.74, 0.12);

    for (const [a, b] of S.edges) {
      const reached = Math.max(S.dist[a], S.dist[b]) <= front;
      ctx.strokeStyle = reached ? P.teal : P.dim; ctx.globalAlpha = reached ? 0.4 : 0.14; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(S.nodes[a].x, S.nodes[a].y); ctx.lineTo(S.nodes[b].x, S.nodes[b].y); ctx.stroke();
    }
    ctx.globalAlpha = 1;

    if (pathHi > 0.02) {
      ctx.strokeStyle = P.sand; ctx.globalAlpha = 0.85 * pathHi; ctx.lineWidth = 2.5;
      ctx.beginPath();
      S.path.forEach((p, i) => { const nd = S.nodes[p]; i ? ctx.lineTo(nd.x, nd.y) : ctx.moveTo(nd.x, nd.y); });
      ctx.stroke(); ctx.globalAlpha = 1;
    }

    for (let i = 0; i < S.N; i++) {
      const nd = S.nodes[i], visited = S.dist[i] <= front;
      let col = visited ? P.teal : P.dim;
      if (pathHi > 0.3 && S.path.includes(i)) col = P.sand;
      if (visited && Math.abs(S.dist[i] - front) < 0.55) env.glow(ctx, nd.x, nd.y, 14, P.teal, 0.5);
      if (i === S.src || i === S.tgt) {
        ctx.strokeStyle = col; ctx.globalAlpha = 0.9; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(nd.x, nd.y, 8, 0, Math.PI * 2); ctx.stroke(); ctx.globalAlpha = 1;
      }
      env.dot(ctx, nd.x, nd.y, i === S.src || i === S.tgt ? 4.5 : 3.2, col, visited ? 0.95 : 0.5);
    }
  }

  A.register('09', 'graph-search · shortest path', draw);
})();
