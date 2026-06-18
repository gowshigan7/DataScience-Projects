# Portfolio Website

A modern, sleek single-page portfolio — vanilla HTML/CSS/JS (no build step), tested
with **Playwright**. All content and assets are **placeholders** meant to be iterated on.

## Preview locally

```bash
cd portfolio
python3 -m http.server 4173      # then open http://localhost:4173
# or: npm run serve
```

## Animations (DS / AI / CS)

Ten uniform, looping canvas animations (embeddings, gradient descent, attention,
k-means, …) live under [`animations/`](./animations/). Shared engine + one pure
function per scene, dark **and** light themes, with a headless GIF exporter.

```bash
npm run serve     # then open http://localhost:4173/animations/gallery.html
npm run render    # export GIFs + stills to animations/out/
```

Full docs: [`animations/README.md`](./animations/README.md) ·
design system: [`animations/STORYBOARD.md`](./animations/STORYBOARD.md).

## Playwright

```bash
cd portfolio
npm install
npx playwright install --with-deps chromium   # first time only
npm test          # run smoke + a11y tests (desktop + mobile)
npm run shots     # write full-page screenshots to ./screenshots
```

## Structure

```
index.html            ← page markup (sections: hero, about, skills, projects, experience, contact)
styles/main.css       ← theme + layout. Re-skin via the CSS variables at the top (:root)
scripts/main.js       ← nav state, mobile menu, scroll-reveal (no dependencies)
assets/*.svg          ← placeholder images (portrait, projects, og, favicon)
assets/resume.pdf     ← placeholder CV
tests/portfolio.spec.js ← Playwright tests
scripts/screenshot.mjs  ← screenshot capture across viewports
```

## How to personalize (iteration checklist)

- **Name / role / bio**: search `index.html` for `Gowshigan` and the `[Your ...]` / `(Placeholder ...)` markers.
- **Colors**: edit `--accent`, `--accent-2`, `--accent-3` in `styles/main.css`.
- **Projects**: replace the three `.project` blocks + swap `assets/project-*.svg` with real screenshots.
- **Experience**: edit the `.timeline` items.
- **Assets**: drop a real `portrait.jpg`, project images, `resume.pdf`, `og-image.png` into `assets/` and update the references.
- **Social links**: footer + contact use `Gowshigan.Selladurai@gmail.com`, GitHub `GowshiganS`, LinkedIn `gowshigan-selladurai`.

> Real profile content (Gowshigan Selladurai — AI Engineer & Data Scientist @ Cleva,
> projects RAG / GMM-from-scratch / DataScience-Projects, hackathon highlights) is
> already integrated. Only the **portrait** and **project images** remain placeholders.

## Deploy (Vercel)

This is a static site, so Vercel needs no build. `vercel.json` is included.

```bash
cd portfolio
npx vercel        # first deploy (links/creates the project) — needs Vercel login
npx vercel --prod # promote to production
```

Or connect the GitHub repo in the Vercel dashboard and set the **Root Directory** to `portfolio`.

**Make it private:** Vercel → Project → *Settings → Deployment Protection* → enable
**Vercel Authentication** (only you / your team can open the URL).
```
