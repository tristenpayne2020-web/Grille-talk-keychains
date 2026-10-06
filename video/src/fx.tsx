import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BODY, C, DISPLAY, EASE_IN, EASE_OUT, safe } from "./brand";

export const useLayout = () => {
  const { width: W, height: H, fps } = useVideoConfig();
  const portrait = H > W;
  const square = H === W;
  const landscape = W / H > 1.2;
  const head = portrait ? 78 : square ? 62 : 66;
  return { W, H, fps, portrait, square, landscape, head };
};

export const ease = (frame: number, a: number, b: number, from = 0, to = 1) =>
  interpolate(frame, [a, b], [from, to], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE_IN });

// ---------------------------------------------------------------- post: grain + vignette (on top of everything)
export const Post: React.FC<{ vignette?: number }> = ({ vignette = 0.5 }) => {
  const frame = useCurrentFrame();
  const seed = frame % 24;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ background: `radial-gradient(120% 90% at 50% 45%, transparent 55%, rgba(0,0,0,${vignette}) 100%)` }} />
      <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, opacity: 0.28, mixBlendMode: "overlay" }}>
        <filter id={`g${seed}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={3} seed={seed} stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter={`url(#g${seed})`} opacity={0.55} />
      </svg>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- type with aura
// characters resolve out of a soft blur with a staggered rise and a letter-spacing settle, a faint warm glow behind
// them; the exit drifts up into blur. One easing family for the whole film.
export const Title: React.FC<{
  lines: string[];
  inAt: number;
  outAt: number;
  size: number;
  align?: "left" | "center";
  y?: number;
  eyebrow?: string;
  sub?: string;
  scrim?: number;
}> = ({ lines, inAt, outAt, size, align = "left", y, eyebrow, sub, scrim = 0.78 }) => {
  const frame = useCurrentFrame();
  const { W, H } = useLayout();
  const S = safe(W, H);
  if (frame < inAt - 1 || frame > outAt + 14) return null;
  const top = y ?? H - S.bottom - lines.length * size * 1.14 - (sub ? size * 0.95 : 0) - (eyebrow ? size * 0.7 : 0) - 24;
  const exit = interpolate(frame, [outAt, outAt + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE_OUT });
  let idx = 0;
  const nChars = lines.join('').length;
  const stagger = Math.min(0.9, 12 / Math.max(1, nChars));   // long titles still resolve in about 0.5 s
  return (
    <div style={{ position: "absolute", left: S.side, right: S.side, top, textAlign: align, color: C.text,
      filter: `blur(${exit * 10}px)`, opacity: 1 - exit, transform: `translateY(${-exit * 24}px)` }}>
      <div style={{ position: "absolute", left: -S.side, right: align === "center" ? -S.side : "25%", top: -size, bottom: -size, zIndex: -1,
        background: `radial-gradient(65% 70% at ${align === "center" ? 50 : 26}% 50%, rgba(7,7,8,${scrim}), transparent 78%)` }} />
      {eyebrow && (
        <div style={{ fontFamily: DISPLAY, fontSize: Math.max(20, size * 0.28), letterSpacing: "0.32em", color: "#cfcdc8", textTransform: "uppercase", textShadow: "0 0 12px rgba(0,0,0,0.9)",
          marginBottom: size * 0.38, opacity: ease(frame, inAt, inAt + 12) }}>{eyebrow}</div>
      )}
      {lines.map((l, li) => (
        <div key={li} style={{ fontFamily: DISPLAY, fontSize: size, lineHeight: 1.14, textTransform: "uppercase", whiteSpace: "nowrap",
          letterSpacing: `${interpolate(frame, [inAt + li * 4, inAt + li * 4 + 28], [0.18, 0.035], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE_IN })}em`,
          textShadow: "0 0 28px rgba(255,236,210,0.28)" }}>
          {l.split("").map((ch, ci) => {
            const t0 = inAt + (idx++) * stagger + li * 2;
            const p = ease(frame, t0, t0 + 14);
            return (
              <span key={ci} style={{ display: "inline-block", opacity: p, filter: `blur(${(1 - p) * 9}px)`, transform: `translateY(${(1 - p) * 0.35}em)`, whiteSpace: "pre" }}>
                {ch}
              </span>
            );
          })}
        </div>
      ))}
      {sub && (
        <div style={{ fontFamily: DISPLAY, fontSize: size * 0.42, letterSpacing: "0.12em", color: "#d9d7d2", textTransform: "uppercase", marginTop: size * 0.38,
          opacity: ease(frame, inAt + 12, inAt + 26), filter: `blur(${(1 - ease(frame, inAt + 12, inAt + 26)) * 6}px)` }}>{sub}</div>
      )}
    </div>
  );
};

export const Cta: React.FC<{ label: string; at: number; size?: number }> = ({ label, at, size = 26 }) => {
  const frame = useCurrentFrame();
  const p = ease(frame, at, at + 14);
  return (
    <div style={{ display: "inline-flex", alignItems: "center", gap: 14, padding: `${size * 0.85}px ${size * 1.5}px`, background: C.text, color: C.bg,
      fontFamily: DISPLAY, fontSize: size, letterSpacing: "0.14em", textTransform: "uppercase", opacity: p, transform: `translateY(${(1 - p) * 24}px)`,
      boxShadow: `0 0 ${40 * p}px rgba(255,236,210,0.25)` }}>
      {label}
    </div>
  );
};

export const Small: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ fontFamily: BODY, color: C.dim, fontSize: 15, letterSpacing: "0.02em", ...style }}>{children}</div>
);

export const Logo: React.FC<{ width: number; style?: React.CSSProperties }> = ({ width, style }) => (
  <Img src={staticFile("img/logo-metal-1600.webp")} style={{ width, ...style }} />
);
