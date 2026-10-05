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

// WebGL on the real GPU when there is one (headless software GL stalls frames and makes timing checks meaningless);
// set GT_SOFTWARE_GL=1 to force SwiftShader, e.g. on a machine without a GPU.
const GL_ARGS = process.env.GT_SOFTWARE_GL
  ? ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']
  : (process.platform === 'win32' ? ['--use-angle=d3d11', '--ignore-gpu-blocklist'] : ['--use-angle=default', '--ignore-gpu-blocklist']);

export function launch(opts = {}) {
  return chromium.launch({ executablePath: chromiumPath(), ...opts, args: [...GL_ARGS, ...(opts.args || []).filter((a) => !/angle|swiftshader/.test(a))] });
}
