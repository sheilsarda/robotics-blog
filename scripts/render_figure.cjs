// Screenshot #figure of a page at the post's 720 px column, 2x for retina, after web fonts load.
// Usage: NODE_PATH=_substack/node_modules node scripts/render_figure.cjs <page.html> <out.png>
const path = require("path");
const puppeteer = require("puppeteer-core");
(async () => {
  const [pagePath, outPath] = process.argv.slice(2);
  const browser = await puppeteer.launch({ executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", headless: true, args: ["--use-mock-keychain"] });
  const page = await browser.newPage();
  await page.setViewport({ width: 760, height: 1200, deviceScaleFactor: 2 });
  await page.goto("file://" + path.resolve(pagePath), { waitUntil: "networkidle0" });
  await page.evaluate(() => document.fonts.ready);
  const fig = await page.$("#figure");
  const info = await fig.evaluate(el => ({ w: el.scrollWidth, cw: el.clientWidth, h: el.scrollHeight, font: getComputedStyle(el).fontFamily, loaded: document.fonts.check("12px Inter") }));
  if (info.w > info.cw) throw new Error("figure overflows horizontally");
  await fig.screenshot({ path: outPath });
  console.log(JSON.stringify(info));
  await browser.close();
})();
