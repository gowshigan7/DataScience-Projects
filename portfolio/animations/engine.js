/* =========================================================
   engine.js — shared animation engine for the 10 DS/AI/CS loops.
   Enforces the uniform system from STORYBOARD.md: fixed canvas,
   palette, grid, mono label, 6s loop, reduced-motion. Each scene
   is just a pure draw(ctx, t, env) with t in [0,1).
   Works as a plain <script> global (browser + headless export).
   ========================================================= */
window.Anim = (function () {
  'use strict';

  const PALETTE = {
    bg: '#0e0d0f', grid: '#1b1820',
    teal: '#2fc3b4',  // active / current
    clay: '#df7a57',  // data / secondary
    sand: '#e8a766',  // result / highlight
    dim: '#46434a',   // inactive
    label: '#b0a6a0',
  };
  const W = 1200, H = 675, M = 64, LOOP = 6000;
  const registry = {};

  const register = (id, label, draw) => { registry[id] = { id, label, draw }; };
  const get = (id) => registry[id];
  const list = () => Object.values(registry);

  // ---- shared helpers exposed to scenes via env ----
  const env = {
    W, H, M, P: PALETTE,
    // easings
    easeOut: (x) => 1 - Math.pow(1 - Math.max(0, Math.min(1, x)), 3),
    easeInOut: (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
    // a smooth 0..1..0 bump centred at c with width w (Gaussian)
    bump: (t, c, w) => Math.exp(-Math.pow((t - c) / w, 2)),
    // deterministic seeded RNG (mulberry32) so frames are reproducible
    rng: (seed) => () => {
      seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
      let r = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
      return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
    },
    // unit normal sample from a uniform rng (Box–Muller)
    gauss: (rnd) => Math.sqrt(-2 * Math.log(rnd() || 1e-9)) * Math.cos(2 * Math.PI * rnd()),
    dot: (ctx, x, y, r, color, a = 1) => {
      ctx.globalAlpha = a; ctx.fillStyle = color;
      ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
      ctx.globalAlpha = 1;
    },
    glow: (ctx, x, y, r, color, a = 0.5) => {
      const g = ctx.createRadialGradient(x, y, 0, x, y, r);
      g.addColorStop(0, color); g.addColorStop(1, 'transparent');
      ctx.globalAlpha = a; ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
      ctx.globalAlpha = 1;
    },
  };

  function background(ctx) {
    ctx.fillStyle = PALETTE.bg; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = PALETTE.grid; ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = M; x <= W - M; x += 48) { ctx.moveTo(x + 0.5, M); ctx.lineTo(x + 0.5, H - M); }
    for (let y = M; y <= H - M; y += 48) { ctx.moveTo(M, y + 0.5); ctx.lineTo(W - M, y + 0.5); }
    ctx.stroke();
  }

  function label(ctx, scene) {
    ctx.fillStyle = PALETTE.label;
    ctx.font = '14px "JetBrains Mono", ui-monospace, monospace';
    ctx.textBaseline = 'alphabetic';
    ctx.fillText('// ' + scene.label, M, H - M + 36);
    // index tag, top-right, for a consistent "set" feel
    ctx.fillStyle = PALETTE.dim;
    ctx.textAlign = 'right';
    ctx.fillText(scene.id, W - M, M - 24);
    ctx.textAlign = 'left';
  }

  function frame(ctx, scene, t) {
    t = ((t % 1) + 1) % 1;
    background(ctx);
    ctx.save();
    scene.draw(ctx, t, env);
    ctx.restore();
    label(ctx, scene);
  }

  // Mount a scene on a canvas. Returns controls; renderAt(t) is used by the
  // headless exporter for deterministic frames.
  function mount(canvas, id) {
    const scene = get(id);
    if (!scene) return null;
    canvas.width = W; canvas.height = H;
    const ctx = canvas.getContext('2d');
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    let raf = 0, start = 0;
    const renderAt = (t) => frame(ctx, scene, t);
    const loop = (now) => { if (!start) start = now; renderAt((now - start) / LOOP); raf = requestAnimationFrame(loop); };
    return {
      scene, renderAt,
      play() { if (reduce) { renderAt(0.42); return; } cancelAnimationFrame(raf); start = 0; raf = requestAnimationFrame(loop); },
      stop() { cancelAnimationFrame(raf); },
    };
  }

  return { PALETTE, W, H, M, LOOP, register, get, list, mount, frame };
})();
