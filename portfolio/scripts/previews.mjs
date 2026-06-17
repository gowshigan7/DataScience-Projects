/**
 * previews.mjs
 * Captures one above-the-fold desktop screenshot per theme variant into
 * ./previews, so design directions can be compared side by side.
 *
 * Usage: node scripts/previews.mjs   (run from the portfolio/ directory)
 */
import { chromium } from '@playwright/test';
import { createServer } from 'http';
import { readFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { extname, join, normalize } from 'path';
import { fileURLToPath } from 'url';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const PORT = 4179;
const THEMES = ['latent', 'midnight', 'noir', 'paper'];

const MIME = {
  '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
  '.svg': 'image/svg+xml', '.pdf': 'application/pdf', '.json': 'application/json',
};

const server = createServer(async (req, res) => {
  try {
    let path = decodeURIComponent((req.url || '/').split('?')[0]);
    if (path === '/') path = '/index.html';
    const file = normalize(join(ROOT, path));
    if (!file.startsWith(ROOT) || !existsSync(file)) { res.writeHead(404); res.end('Not found'); return; }
    const body = await readFile(file);
    res.writeHead(200, { 'Content-Type': MIME[extname(file)] || 'application/octet-stream' });
    res.end(body);
  } catch { res.writeHead(500); res.end('Server error'); }
});

await mkdir(join(ROOT, 'previews'), { recursive: true });
await new Promise((r) => server.listen(PORT, r));
const browser = await chromium.launch();
try {
  for (const theme of THEMES) {
    const q = theme === 'latent' ? '' : `?theme=${theme}`;
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
    await page.goto(`http://127.0.0.1:${PORT}/${q}`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1200); // let the latent field settle
    await page.screenshot({ path: `previews/${theme}.png` }); // above-the-fold hero
    console.log(`captured previews/${theme}.png`);
    await page.close();
  }
} finally {
  await browser.close();
  server.close();
}
