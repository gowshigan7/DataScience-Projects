/* =========================================================
   latent.js — the hero "signature".
   A latent-space field: points drift and settle into a few
   Gaussian clusters, with faint intra-cluster links. It nods
   to the subject's world — RAG embeddings + GMM-from-scratch —
   rather than being decoration. Honors prefers-reduced-motion.
   ========================================================= */
(function () {
  'use strict';

  const canvas = document.getElementById('latent');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Cluster colours are derived from the active theme's CSS accents, so any
  // palette variant recolours the signature automatically.
  function hexToRgb(h) {
    h = (h || '').trim().replace('#', '');
    if (h.length === 3) h = h.split('').map((c) => c + c).join('');
    if (h.length !== 6) return null;
    const n = parseInt(h, 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  const cs = getComputedStyle(document.documentElement);
  const accent = (name, fb) => hexToRgb(cs.getPropertyValue(name)) || fb;
  const CLUSTERS = [
    { cx: 0.66, cy: 0.36, spread: 0.12, color: accent('--accent', [47, 195, 180]) },
    { cx: 0.84, cy: 0.62, spread: 0.10, color: accent('--accent-2', [223, 122, 87]) },
    { cx: 0.55, cy: 0.72, spread: 0.09, color: accent('--accent-3', [232, 167, 102]) },
  ];

  let W = 0, H = 0, dpr = 1, points = [];

  // Box-Muller: a unit normal sample. (The same Gaussian the GMM project models.)
  function gauss() {
    let u = 0, v = 0;
    while (u === 0) u = Math.random();
    while (v === 0) v = Math.random();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  }

  function sampleTarget(c) {
    return {
      x: (c.cx + gauss() * c.spread) * W,
      y: (c.cy + gauss() * c.spread) * H,
    };
  }

  function build() {
    const count = W < 680 ? 38 : 82;
    points = [];
    for (let i = 0; i < count; i++) {
      const c = CLUSTERS[i % CLUSTERS.length];
      const t = sampleTarget(c);
      points.push({
        c, cluster: i % CLUSTERS.length,
        x: Math.random() * W, y: Math.random() * H,
        tx: t.x, ty: t.y,
        r: 0.8 + Math.random() * 1.8,
        speed: 0.012 + Math.random() * 0.02,
        rest: Math.random() * 240,
      });
    }
  }

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.clientWidth;
    H = canvas.clientHeight;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    build();
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);

    // Faint intra-cluster links — the "retrieval" graph between near neighbours.
    for (let i = 0; i < points.length; i++) {
      for (let j = i + 1; j < points.length; j++) {
        const a = points[i], b = points[j];
        if (a.cluster !== b.cluster) continue;
        const dx = a.x - b.x, dy = a.y - b.y;
        const d2 = dx * dx + dy * dy;
        if (d2 < 9000) {
          const [r, g, bl] = a.c.color;
          ctx.strokeStyle = `rgba(${r},${g},${bl},${0.10 * (1 - d2 / 9000)})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    }

    // Points.
    for (const p of points) {
      const [r, g, bl] = p.c.color;
      ctx.fillStyle = `rgba(${r},${g},${bl},0.85)`;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function step() {
    for (const p of points) {
      p.x += (p.tx - p.x) * p.speed;
      p.y += (p.ty - p.y) * p.speed;
      // Occasionally re-sample a new target so the field keeps breathing.
      if (--p.rest <= 0 && Math.abs(p.tx - p.x) < 6 && Math.abs(p.ty - p.y) < 6) {
        const t = sampleTarget(p.c);
        p.tx = t.x; p.ty = t.y; p.rest = 180 + Math.random() * 320;
      }
    }
    draw();
    raf = requestAnimationFrame(step);
  }

  let raf = 0;
  resize();
  window.addEventListener('resize', () => { cancelAnimationFrame(raf); resize(); if (!reduce) raf = requestAnimationFrame(step); else draw(); });

  if (reduce) {
    // Settle points onto their targets and render a single static frame.
    for (const p of points) { p.x = p.tx; p.y = p.ty; }
    draw();
  } else {
    raf = requestAnimationFrame(step);
  }
})();
