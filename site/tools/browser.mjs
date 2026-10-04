// Shared Chromium launcher: CHROMIUM_PATH if set, else the installed Google Chrome, else Playwright's own browser.
import { chromium } from 'playwright';
import fs from 'node:fs';

const CANDIDATES = [
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  '/usr/bin/google-chrome',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
];

export function chromiumPath() {
  if (process.env.CHROMIUM_PATH) return process.env.CHROMIUM_PATH;
  return CANDIDATES.find((p) => fs.existsSync(p));
}

export function launch(opts = {}) {
  return chromium.launch({ executablePath: chromiumPath(), ...opts });
}
