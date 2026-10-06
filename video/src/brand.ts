import { Easing } from "remotion";
import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

export const C = {
  bg: "#070708",
  panel: "#0b0b0c",
  panel2: "#141416",
  text: "#f2f1ee",
  muted: "#9b9a97",
  dim: "#5d5c59",
  light: "#fff8ee",
};

export const DISPLAY = "Michroma";
export const BODY = "'Segoe UI', system-ui, sans-serif";

loadFont({ family: DISPLAY, url: staticFile("michroma-latin-400.woff2") });

// one easing family for the whole film: entrances and their matching exit
export const EASE_IN = Easing.bezier(0.16, 1, 0.3, 1);
export const EASE_OUT = Easing.bezier(0.7, 0, 0.84, 0);

export const FPS = 30;
export const BEAT = 15; // 120 BPM grid at 30 fps

// platform UI safe zones (9:16): top 220, bottom 380, sides 64. Scaled for the other shapes.
export const safe = (w: number, h: number) => {
  if (h > w) return { top: 220, bottom: 380, side: 64 };
  if (h === w) return { top: 110, bottom: 120, side: 64 };
  return { top: 90, bottom: 110, side: 110 };
};

export const LEGAL =
  "Grille Talk is an independent maker, not affiliated with or endorsed by any vehicle manufacturer.";
