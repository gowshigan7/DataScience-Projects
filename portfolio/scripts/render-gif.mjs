/**
 * render-gif.mjs — headless preview renderer for the animation scenes.
 * Loads animations/scene.html?scene=<id>, drives the engine's deterministic
 * renderAt(t) frame by frame, ships each (downscaled) frame to Node as base64
 * RGBA, and encodes a looping GIF with gifenc. Also saves crisp PNG stills.
 *
 * Usage: node scripts/render-gif.mjs [sceneId ...]   (default: all registered)
 */
import { chromium } from '@playwright/test';
import { createServer } from 'http';
import { readFile, mkdir, writeFile } from 'fs/promises';
import { existsSync } from 'fs';
import { extname, join, normalize } from 'path';
import { fileURLToPath } from 'url';
import gifencPkg from 'gifenc';
const { GIFEncoder, quantize, applyPalette } = gifencPkg;

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const PORT = 4181;
const GIF_W = 512, GIF_H = 288, FRAMES = 48, DELAY = Math.round(6000 / FRAMES);
const STILLS = [0.18, 0.5, 0.82];

const MIME = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.json': 'application/json' };
const server = createServer(async (req, res) => {
  try {
    let p = decodeURIComponent((req.url || '/').split('?')[0]);
    if (p === '/') p = '/index.html';
    const f = normalize(join(ROOT, p));
    if (!f.startsWith(ROOT) || !existsSync(f)) { res.writeHead(404); res.end('nope'); return; }
    res.writeHead(200, { 'Content-Type': MIME[extname(f)] || 'application/octet-stream' });
    res.end(await readFile(f));
  } catch { res.writeHead(500); res.end('err'); }
});

await mkdir(join(ROOT, 'animations', 'out'), { recursive: true });
await new Promise((r) => server.listen(PORT, r));
const browser = await chromium.launch();

try {
  let ids = process.argv.slice(2);
  if (!ids.length) {
    const probe = await browser.newPage();
    await probe.goto(`http://127.0.0.1:${PORT}/animations/gallery.html`, { waitUntil: 'load' });
    await probe.waitForFunction('window.Anim && window.Anim.list().length > 0');
    ids = await probe.evaluate(() => window.Anim.list().map((s) => s.id));
    await probe.close();
  }

  for (const id of ids) {
    const page = await browser.newPage({ viewport: { width: 1280, height: 760 }, deviceScaleFactor: 2 });
    await page.goto(`http://127.0.0.1:${PORT}/animations/scene.html?scene=${id}`, { waitUntil: 'networkidle' });
    await page.waitForFunction('window.__ready === true');

    // crisp stills
    for (const t of STILLS) {
      await page.evaluate((tt) => window.__renderAt(tt), t);
      await page.locator('canvas').screenshot({ path: join(ROOT, 'animations', 'out', `${id}-t${Math.round(t * 100)}.png`) });
    }

    // looping gif — capture downscaled RGBA per frame, encode in Node
    const enc = GIFEncoder();
    for (let f = 0; f < FRAMES; f++) {
      const b64 = await page.evaluate(({ t, GW, GH }) => {
        window.__renderAt(t);
        const src = document.querySelector('canvas');
        let off = window.__off;
        if (!off) { off = window.__off = document.createElement('canvas'); off.width = GW; off.height = GH; }
        const octx = off.getContext('2d');
        octx.clearRect(0, 0, GW, GH);
        octx.drawImage(src, 0, 0, GW, GH);
        const u8 = new Uint8Array(octx.getImageData(0, 0, GW, GH).data.buffer);
        let bin = ''; const ch = 0x8000;
        for (let i = 0; i < u8.length; i += ch) bin += String.fromCharCode.apply(null, u8.subarray(i, i + ch));
        return btoa(bin);
      }, { t: f / FRAMES, GW: GIF_W, GH: GIF_H });
      const data = new Uint8ClampedArray(Buffer.from(b64, 'base64'));
      const palette = quantize(data, 256);
      const index = applyPalette(data, palette);
      enc.writeFrame(index, GIF_W, GIF_H, { palette, delay: DELAY, repeat: 0 });
    }
    enc.finish();
    await writeFile(join(ROOT, 'animations', 'out', `${id}.gif`), Buffer.from(enc.bytesView()));
    console.log(`rendered ${id}: out/${id}.gif (+ stills)`);
    await page.close();
  }
} finally {
  await browser.close();
  server.close();
}
