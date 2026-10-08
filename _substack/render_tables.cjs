// Screenshots each .shot element of a page to <out dir>/<element id>.png at Substack's 728 px column, 2x for retina.
// Usage: node render_tables.cjs <page.html> <out dir>
const path = require("path");
const puppeteer = require("puppeteer-core");

(async () => {
  const [pagePath, outDir] = process.argv.slice(2);
  const browser = await puppeteer.launch({
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless: true,
    args: ["--use-mock-keychain"],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 728, height: 1000, deviceScaleFactor: 2 });
  await page.goto("file://" + path.resolve(pagePath), { waitUntil: "load" });
  for (const shot of await page.$$(".shot")) {
    const { id, overflow } = await shot.evaluate((el) => ({ id: el.id, overflow: el.scrollWidth > el.clientWidth }));
    if (overflow) throw new Error(`${id} is wider than the 728 px column`);
    await shot.screenshot({ path: path.join(outDir, `${id}.png`) });
  }
  await browser.close();
})();
