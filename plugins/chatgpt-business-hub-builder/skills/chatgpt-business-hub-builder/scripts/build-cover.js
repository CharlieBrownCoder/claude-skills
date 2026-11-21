#!/usr/bin/env node
// Renders a ChatGPT Business Hub cover photo and a mock of the profile card.
// Usage: node build-cover.js config.json [outDir]
// Needs Playwright with Chromium. Outputs cover.png (1200x400), cover@2x.png
// (2400x800) and card-preview.png (the cover as the card shows it, with the
// logo and the two buttons drawn over it).
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const cfgPath = process.argv[2];
if (!cfgPath) { console.error('usage: node build-cover.js config.json [outDir]'); process.exit(1); }
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const out = path.resolve(process.argv[3] || '.');
fs.mkdirSync(out, { recursive: true });
const dir = path.dirname(path.resolve(cfgPath));
const c = Object.assign({ background: '#16181d', text: '#faf9f7', accent: '#e05a2b' }, cfg.colors);
const esc = s => String(s).replace(/[&<>]/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[m]));
const dataUri = (p, mime) => `data:${mime};base64,${fs.readFileSync(path.resolve(dir, p)).toString('base64')}`;
const mimeOf = p => ({ '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp' }[path.extname(p).toLowerCase()]);

// Headline: the emphasis word or phrase is drawn in the accent colour.
let headline = esc(cfg.headline);
if (cfg.emphasis) {
  const e = esc(cfg.emphasis);
  if (!headline.includes(e)) { console.error(`emphasis "${cfg.emphasis}" is not in the headline`); process.exit(1); }
  headline = headline.replace(e, `<span class="em">${e}</span>`);
}
const sub = (cfg.subline || []).map(esc).join('<b>·</b>');
const fonts = cfg.fonts || {};
const face = (w, p) => p ? `@font-face{font-family:Cover;font-weight:${w};src:url(${dataUri(p, 'font/woff')})}` : '';

// Layout, on the 1200x400 canvas. Two corners stay empty because the card
// draws over them: the logo (x 72-270, y 314-400) and the menu and close
// buttons (x 928-1166, y 28-132). Text starts 72px in. The subline starts at
// x=300 so it clears the logo.
const html = `<!doctype html><meta charset="utf-8"><style>
${face(400, fonts.regular)}${face(700, fonts.bold)}
*{box-sizing:border-box;margin:0}
body{width:1200px;height:400px;background:${c.background};color:${c.text};font-family:Cover,system-ui,sans-serif;overflow:hidden;position:relative}
.em{color:${c.accent}}
.label{position:absolute;left:72px;top:44px;font-size:26px;letter-spacing:.14em;font-weight:700;color:${c.accent};text-transform:uppercase;white-space:nowrap}
h1{position:absolute;left:72px;top:124px;font-size:80px;font-weight:700;letter-spacing:-.035em;line-height:1;white-space:nowrap}
.sub{position:absolute;left:300px;top:268px;font-size:40px;font-weight:700;white-space:nowrap}
.sub b{color:${c.accent};padding:0 10px}
</style><div class="label">${esc(cfg.label || '')}</div><h1>${headline}</h1><div class="sub">${sub}</div>`;

(async () => {
  const browser = await chromium.launch();
  const fit = async page => page.evaluate(() => {
    const warn = [];
    const shrink = (sel, maxRight, min) => {
      const el = document.querySelector(sel);
      let size = parseFloat(getComputedStyle(el).fontSize);
      while (el.getBoundingClientRect().right > maxRight && size > min) { size -= 2; el.style.fontSize = size + 'px'; }
      if (el.getBoundingClientRect().right > maxRight) warn.push(`${sel} still runs past ${maxRight}px at ${size}px: shorten it`);
      return size;
    };
    const sizes = { headline: shrink('h1', 1128, 56), subline: shrink('.sub', 1128, 40), label: shrink('.label', 900, 22) };
    return { sizes, warn };
  });
  let report;
  for (const scale of [1, 2]) {
    const page = await browser.newPage({ viewport: { width: 1200, height: 400 }, deviceScaleFactor: scale });
    await page.setContent(html);
    await page.evaluate(() => document.fonts.ready);
    report = await fit(page);
    await page.screenshot({ path: path.join(out, scale === 1 ? 'cover.png' : 'cover@2x.png') });
    await page.close();
  }
  // The card: cover at 420x140, a fade over its lower part, the logo over the
  // bottom-left corner, the menu and close buttons over the top-right.
  const cover = dataUri(path.join(out, 'cover@2x.png'), 'image/png');
  const logo = cfg.logo ? `<img src="${dataUri(cfg.logo, mimeOf(cfg.logo))}" style="width:100%;height:100%;border-radius:12px">` : '';
  const btn = (x, t) => `<div style="position:absolute;left:${x}px;top:10px;width:36px;height:36px;border-radius:10px;background:#111;color:#fff;text-align:center;line-height:34px;font:700 16px sans-serif">${t}</div>`;
  const card = `<!doctype html><meta charset="utf-8"><body style="margin:0;background:#222;width:450px">
<div style="position:relative;width:420px;height:230px;background:#000;border-radius:18px;overflow:hidden;margin:14px">
<img src="${cover}" style="width:420px;height:140px;display:block">
<div style="position:absolute;left:0;top:90px;width:420px;height:50px;background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.45))"></div>
<div style="position:absolute;left:25px;top:110px;width:68px;height:68px;border-radius:14px;background:#16181d;border:2px solid #000">${logo}</div>
${btn(325, '…')}${btn(372, '✕')}
<div style="position:absolute;left:25px;top:192px;color:#fff;font:20px sans-serif">${esc(cfg.business || '')}</div></div>`;
  const page = await browser.newPage({ viewport: { width: 450, height: 260 }, deviceScaleFactor: 2 });
  await page.setContent(card);
  await page.screenshot({ path: path.join(out, 'card-preview.png') });
  await browser.close();
  const s = report.sizes;
  console.log(`headline ${s.headline}px, subline ${s.subline}px, label ${s.label}px on the 1200px canvas`);
  console.log(`on the 420px card: headline ${(s.headline * 0.35).toFixed(0)}px, subline ${(s.subline * 0.35).toFixed(0)}px, label ${(s.label * 0.35).toFixed(0)}px`);
  report.warn.forEach(w => console.log('WARNING: ' + w));
  console.log(`wrote cover.png, cover@2x.png, card-preview.png to ${out}`);
  if (report.warn.length) process.exit(2);
})();
