// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Smoke tests for the portfolio website.
 * Verifies the page loads, key sections render, navigation works,
 * placeholder assets resolve, and there are no console errors.
 */

test.beforeEach(async ({ page }) => {
  await page.goto('/');
});

test('page has correct title and hero', async ({ page }) => {
  await expect(page).toHaveTitle(/Gowshigan/);
  await expect(page.locator('.hero__eyebrow')).toContainText('Gowshigan');
  await expect(page.locator('.hero__title')).toContainText('AI');
  await expect(page.getByRole('link', { name: 'See the work' })).toBeVisible();
  await expect(page.locator('#latent')).toBeVisible();
});

test('all main sections are present', async ({ page }) => {
  for (const id of ['#about', '#skills', '#projects', '#experience', '#contact']) {
    await expect(page.locator(id)).toHaveCount(1);
  }
  await expect(page.locator('.project')).toHaveCount(3);
  await expect(page.locator('.card')).toHaveCount(3);
});

test('placeholder images load successfully', async ({ page }) => {
  // Scroll through the page so lazy-loaded images are requested before asserting.
  await page.evaluate(async () => {
    for (let y = 0; y <= document.body.scrollHeight; y += 400) {
      window.scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 30));
    }
  });
  const imgs = page.locator('img');
  const count = await imgs.count();
  expect(count).toBeGreaterThan(0);
  for (let i = 0; i < count; i++) {
    const img = imgs.nth(i);
    await expect(img).toHaveJSProperty('complete', true);
    await expect
      .poll(async () => img.evaluate((el) => /** @type {HTMLImageElement} */ (el).naturalWidth))
      .toBeGreaterThan(0);
  }
});

test('navigation anchors scroll to sections', async ({ page, isMobile }) => {
  if (isMobile) {
    await page.locator('#navToggle').click();
  }
  await page.getByRole('link', { name: /Work/ }).first().click();
  await expect(page.locator('#projects')).toBeInViewport({ ratio: 0.05 });
});

test('no console errors on load', async ({ page }) => {
  const errors = [];
  page.on('console', (msg) => {
    if (msg.type() !== 'error') return;
    const text = msg.text();
    // Ignore failures from blocked/unreachable third-party resources (e.g. Google
    // Fonts behind a network proxy). The CSS already falls back to system fonts.
    if (/Failed to load resource|ERR_|net::/.test(text)) return;
    if (/googleapis|gstatic/.test(text)) return;
    errors.push(text);
  });
  page.on('pageerror', (err) => errors.push(err.message));
  await page.reload({ waitUntil: 'networkidle' });
  expect(errors).toEqual([]);
});
