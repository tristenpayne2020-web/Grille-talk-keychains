import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { BODY, C, DISPLAY, LEGAL, safe } from "./brand";
import { Cta, ease, Logo, Small, useLayout } from "./fx";

// The owner's halftone G80 artwork carries the wordmark in the middle of its bumper. It is scaled and placed so its
// wordmark sits exactly under the metallic logo: the logo reveals over its own halftone print, with a light sweep.
const ART_W = 2000, ART_H = 1125;
const ART_LOGO = { cx: 995 / ART_W, cy: 552 / ART_H, w: 780 / ART_W };

export const EndCard: React.FC<{ dur: number; cta?: string }> = ({ dur, cta = "Find your car" }) => {
  const f = useCurrentFrame();
  const { W, H, portrait, square } = useLayout();
  const S = safe(W, H);
  const k = dur / 90;
  const logoW = portrait ? 820 : square ? 700 : 760;
  const logoY = portrait ? H * 0.4 : H * 0.4; // logo centre
  const drift = interpolate(f, [0, dur], [1.06, 1.0]);
  const artW = (logoW / ART_LOGO.w) * drift;
  const artH = artW * (ART_H / ART_W);
  const art = ease(f, 0, 18) * 0.62;
  const reveal = ease(f, 6, 26);
  const sweep = interpolate(f, [14, 40], [-0.4, 1.4], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const logoH = logoW * (262 / 1600);
  return (
    <AbsoluteFill style={{ background: C.bg, overflow: "hidden" }}>
      <Img src={staticFile("img/hero_halftone_g80.webp")}
        style={{ position: "absolute", width: artW, height: artH, left: W / 2 - artW * ART_LOGO.cx + (drift - 1) * 300, top: logoY - artH * ART_LOGO.cy, opacity: art }} />
      <AbsoluteFill style={{ background: `radial-gradient(${portrait ? "95% 45%" : "70% 75%"} at 50% ${(logoY / H) * 100}%, transparent 35%, ${C.bg} 92%)` }} />
      {/* the artwork's own printed wordmark is hidden under a dark plate, so the drift never doubles the logo */}
      <div style={{ position: "absolute", left: W / 2 - logoW * 0.74, top: logoY - logoH * 1.6, width: logoW * 1.48, height: logoH * 3.2,
        background: `radial-gradient(50% 50% at 50% 50%, ${C.bg} 62%, transparent 100%)` }} />
      <div style={{ position: "absolute", left: W / 2 - logoW / 2, top: logoY - logoH / 2, width: logoW, clipPath: `inset(0 ${(1 - reveal) * 100}% 0 0)` }}>
        <Logo width={logoW} />
        <div style={{ position: "absolute", inset: 0, mixBlendMode: "screen",
          background: `linear-gradient(100deg, transparent ${sweep * 100 - 10}%, rgba(255,248,238,0.85) ${sweep * 100}%, transparent ${sweep * 100 + 10}%)`,
          WebkitMaskImage: `url(${staticFile("img/logo-metal-1600.webp")})`, WebkitMaskSize: "100% 100%", maskImage: `url(${staticFile("img/logo-metal-1600.webp")})`, maskSize: "100% 100%" }} />
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: logoY + (portrait ? 330 : square ? 230 : 190), display: "flex", flexDirection: "column", alignItems: "center", gap: portrait ? 44 : 28 }}>
        <Cta label={cta} at={Math.round(34 * k)} size={portrait ? 32 : 24} />
        <div style={{ fontFamily: DISPLAY, color: C.text, fontSize: portrait ? 36 : 26, letterSpacing: "0.12em", opacity: ease(f, 40 * k, 52 * k) }}>
          grilletalk.shop
        </div>
      </div>
      <div style={{ position: "absolute", left: S.side, right: S.side, bottom: portrait ? S.bottom : 36, textAlign: "center", opacity: ease(f, 44 * k, 56 * k) }}>
        <Small style={{ fontFamily: BODY, fontSize: portrait ? 19 : 15 }}>{LEGAL}</Small>
      </div>
    </AbsoluteFill>
  );
};
