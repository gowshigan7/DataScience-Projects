# Animations — DS / AI / CS loop set

Ten uniform, looping canvas animations illustrating real data-science / AI /
computer-science concepts. One shared engine guarantees a single visual
language (palette, grid, timing, label); each scene is a small pure function.
Web-native (tiny, crisp, accessible) with a headless GIF/stills exporter.

See **[STORYBOARD.md](./STORYBOARD.md)** for the design system and the brief of
each scene.

## Quick start

```bash
cd portfolio
npm install                       # first time (installs Playwright + gifenc)
npm run serve                     # static server on http://localhost:4173

# then open:
#   http://localhost:4173/animations/gallery.html         ← all 10, dark/light toggle
#   http://localhost:4173/animations/scene.html?scene=03&theme=light   ← one scene
```

No server is strictly required to view — you can also open the files directly —
but a server avoids any `file://` quirks with the web fonts.

## The 10 scenes

| id | concept | id | concept |
|----|---------|----|---------|
| `01` latent-space | embeddings & retrieval (RAG) | `06` attention | transformer |
| `02` gradient-descent | optimisation | `07` gmm-density | mixture, EM |
| `03` neural-net | forward pass (MLP) | `08` sorting | algorithms |
| `04` k-means | clustering | `09` graph-search | shortest path |
| `05` decision-boundary | classification | `10` convolution | CNN kernel |

## Architecture

```
animations/
  STORYBOARD.md          ← design system + per-scene brief
  README.md              ← this file
  engine.js              ← shared engine: canvas, THEMES, grid, label, 6s loop, reduced-motion
  scene.html             ← single-scene viewer  (?scene=NN&theme=dark|light)
  gallery.html           ← grid of all 10 + dark/light toggle
  scenes/
    01-latent-space.js   ← one pure draw(ctx, t, env) per scene, t ∈ [0,1)
    … 10 files …
  out/                   ← generated GIFs + stills (git-ignored, regenerate any time)
```

### How the engine works

- `Anim.mount(canvas, id, theme)` returns `{ play, stop, renderAt(t) }`.
  - `play()` runs the 6 s rAF loop (or, under `prefers-reduced-motion`, draws a
    single representative frame and stops).
  - `renderAt(t)` draws one deterministic frame at normalised time `t` — this is
    what the exporter drives, frame by frame.
- The engine paints the **background, grid, mono label and index tag**, then
  calls the scene's `draw`. Scenes never touch those — uniformity by construction.
- **Themes** live in `engine.js` (`THEMES.dark`, `THEMES.light`). The chosen
  palette is passed to every scene as `env.P`. Scenes reference colours by
  **key** (`env.P.teal`, `env.P[node.key]`), resolved at draw time, so switching
  theme recolours everything with no scene changes.

### The `env` passed to every scene

| member | purpose |
|--------|---------|
| `W, H, M` | canvas size (1200×675) and safe-area margin (64) |
| `P` | the active palette (`bg, grid, teal, clay, sand, dim, label`) |
| `easeOut, easeInOut` | easings |
| `bump(t, c, w)` | smooth 0→1→0 pulse centred at `c`, width `w` (for "beats") |
| `rng(seed)` | deterministic mulberry32 RNG (reproducible frames) |
| `gauss(rnd)` | unit-normal sample from an `rng` |
| `dot(ctx,x,y,r,color,a)` / `glow(ctx,x,y,r,color,a)` | drawing helpers |

## Adding a new scene

1. Create `scenes/NN-name.js` with the standard header docstring and an IIFE
   that builds its state lazily and exposes a pure `draw(ctx, t, env)`.
2. Use **colour keys** (`env.P.teal` …), never hard-coded hex — so both themes work.
3. Make it **loop seamlessly**: frame at `t→1` must match `t=0` (use periodic
   motion, or a ping-pong / fade near the end).
4. Register it: `window.Anim.register('NN', 'name · concept', draw);`
5. Add a `<script src="scenes/NN-name.js">` tag to **both** `scene.html` and
   `gallery.html`.

## Rendering (export)

```bash
cd portfolio
npm run render            # all scenes, both themes → animations/out/<id>-<theme>.gif (+ stills)
npm run render -- 03 07   # only these scene ids
node scripts/montage.mjs  # full-page contact sheets → out/contact-dark.png / contact-light.png
```

- The renderer (`scripts/render-gif.mjs`) loads each scene headless, calls
  `renderAt(t)` for 48 frames, ships each downscaled frame to Node and encodes a
  looping GIF with **gifenc**. It also saves crisp PNG stills at a few `t` values.
- Output goes to `animations/out/` which is **git-ignored** — regenerate any time.
- **MP4 / Remotion**: not wired yet. The same deterministic `renderAt(t)` is the
  hook — feed it into Remotion or an ffmpeg frame pipe when MP4 clips are needed.

## Using a scene on the site

A scene is just a `<canvas>` plus the engine and that scene's script:

```html
<canvas id="hero-anim"></canvas>
<script src="/animations/engine.js"></script>
<script src="/animations/scenes/01-latent-space.js"></script>
<script>
  Anim.mount(document.getElementById('hero-anim'), '01', 'dark').play();
</script>
```
