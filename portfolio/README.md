# Portfolio Website

A modern, sleek single-page portfolio — vanilla HTML/CSS/JS (no build step), tested
with **Playwright**. All content and assets are **placeholders** meant to be iterated on.

## Preview locally

```bash
cd portfolio
python3 -m http.server 4173      # then open http://localhost:4173
# or: npm run serve
```

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
- **Social links**: update the footer + contact email (`gowshigan6@gmail.com`).
```
