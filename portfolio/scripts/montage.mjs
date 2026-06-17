/**
 * montage.mjs — full-page screenshot of the gallery (all 10 tiles) in both
 * themes, as a single contact sheet per theme.
 */
import { chromium } from '@playwright/test';
import { createServer } from 'http';
import { readFile } from 'fs/promises';
import { existsSync } from 'fs';
import { extname, join, normalize } from 'path';
import { fileURLToPath } from 'url';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const PORT = 4182;
const MIME = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json' };
const server = createServer(async (req, res) => {
  let p = decodeURIComponent((req.url || '/').split('?')[0]);
  const f = normalize(join(ROOT, p));
  if (!f.startsWith(ROOT) || !existsSync(f)) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'Content-Type': MIME[extname(f)] || 'application/octet-stream' });
  res.end(await readFile(f));
});
await new Promise((r) => server.listen(PORT, r));
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1320, height: 1000 }, deviceScaleFactor: 1.5 });
await page.goto(`http://127.0.0.1:${PORT}/animations/gallery.html`, { waitUntil: 'networkidle' });
await page.waitForFunction('window.Anim && window.Anim.list().length === 10');
await page.waitForTimeout(700);
await page.screenshot({ path: join(ROOT, 'animations', 'out', 'contact-dark.png'), fullPage: true });
await page.click('#themes button[data-theme="light"]');
await page.waitForTimeout(700);
await page.screenshot({ path: join(ROOT, 'animations', 'out', 'contact-light.png'), fullPage: true });
console.log('contact sheets written');
await browser.close();
server.close();
