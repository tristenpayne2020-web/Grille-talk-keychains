import { Audio } from "@remotion/media";
import { LightLeak } from "@remotion/light-leaks";
import React from "react";
import { AbsoluteFill, Img, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, DISPLAY } from "./brand";
import { FROM, HEADLIGHT_SURCHARGE, N_CARS, N_COLOURS, TALON_PRICE, TALON_SIZE, WALL_FROM } from "./data";
import { EndCard } from "./EndCard";
import { Cta, ease, Logo, Post, Title, useLayout } from "./fx";
import T from "./timeline.json";

type Shot = { name: string; from: number; dur: number };
type Film = { song_start: number; frames: number; beats: number[]; drop: number; shots: Shot[] };
export const TL = T as unknown as Record<"launch" | "cutdown" | "spinner_ad" | "wall_ad", Film> & { fps: number };

const pad = (n: number) => String(n).padStart(4, "0");

// ---------------------------------------------------------------- a rendered Blender shot (JPEG sequence)
// crop: for the square cut-down the 9:16 frames are cropped around the product (it sits at 37 % of the frame height)
const Frames: React.FC<{ dir: string; avail: number; crop?: boolean }> = ({ dir, avail, crop }) => {
  const f = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const src = staticFile(`shots/${dir}/${pad(Math.min(avail - 1, Math.max(0, f)))}.jpg`);
  if (crop) {
    const h = (width * 1920) / 1080;
    const top = Math.max(height - h, Math.min(0, height / 2 - h * 0.37));
    return <Img src={src} style={{ position: "absolute", left: 0, top, width, height: h }} />;
  }
  return <Img src={src} style={{ position: "absolute", inset: 0, width, height }} />;
};

// beat punch: after the drop every beat gives the frame a small push (scale) that decays
const usePunch = (film: Film, offset: number) => {
  const f = useCurrentFrame() + offset;
  if (f < film.drop) return 1;
  const last = [...film.beats].reverse().find((b) => b <= f && b >= film.drop);
  if (last === undefined) return 1;
  return 1 + 0.018 * Math.exp(-(f - last) / 3.5);
};

const Punch: React.FC<{ film: Film; offset: number; children: React.ReactNode }> = ({ film, offset, children }) => {
  const s = usePunch(film, offset);
  return <AbsoluteFill style={{ transform: `scale(${s})` }}>{children}</AbsoluteFill>;
};

// warm flash on the drop
const DropFlash: React.FC<{ at: number }> = ({ at }) => {
  const f = useCurrentFrame();
  const o = f >= at ? Math.max(0, 0.4 * (1 - (f - at) / 6)) : 0;
  return o > 0 ? <AbsoluteFill style={{ background: "#fff2df", opacity: o, mixBlendMode: "screen" }} /> : null;
};

// ---------------------------------------------------------------- copy per shot (every number comes from the catalog)
type Copy = { lines: string[]; sub?: string; eyebrow?: string; size?: number };
const COPY: Record<string, (portrait: boolean) => Copy> = {
  hook: (p) => ({ lines: p ? ["Your keys", "should match", "your car."] : ["Your keys should", "match your car."] }),
  detail: () => ({ lines: ["Every light.", "Every intake."] }),
  headlights: () => ({ lines: ["Pick the lights."], sub: `Custom headlights ${HEADLIGHT_SURCHARGE}` }),
  colours: () => ({ lines: [`${N_COLOURS} colors.`], sub: `From ${FROM}`, size: 1.15 }),
  flip: () => ({ lines: ["Flip it."], sub: "Carbon-fibre textured back", size: 1.1 }),
  garage: () => ({ lines: [`${N_CARS} cars`, "and counting."] }),
  wall: (p) => ({ lines: p ? ["Your car,", "by the", "front door."] : ["Your car,", "by the front door."], sub: `Wall key holders from ${WALL_FROM}` }),
  spinner: (p) => ({ lines: p ? ["Talon", "keychain", "spinner."] : ["Talon keychain", "spinner."], sub: `Carbon fiber · ${TALON_PRICE}` }),
  macro: () => ({ lines: ["Topology", "optimised."], eyebrow: "Talon keychain spinner" }),
  spin: () => ({ lines: ["Carbon fiber.", "Built to last."] }),
  keys: (p) => ({ lines: p ? ["Your car,", "by the", "front door."] : ["Your car,", "by the front door."] }),
  wcolours: (p) => ({ lines: p ? ["Every body", "color."] : ["Every body color."] }),
};

// callout screen positions written by blender/shots.py (normalised, y down)
const meta = (dir: string, name: string): Record<string, [number, number]> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    return require(`../public/shots/${dir}/${name}_meta.json`);
  } catch {
    return {};
  }
};

const Callouts: React.FC<{ items: { at: [number, number]; text: string; to: [number, number]; t0: number }[] }> = ({ items }) => {
  const f = useCurrentFrame();
  const { W, H, portrait } = useLayout();
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
      {items.map((c, i) => {
        const p = ease(f, c.t0, c.t0 + 14);
        const [x, y] = [c.at[0] * W, c.at[1] * H];
        const [tx, ty] = [c.to[0] * W, c.to[1] * H];
        return (
          <g key={i} opacity={p}>
            <circle cx={x} cy={y} r={7} fill="none" stroke={C.text} strokeWidth={2} />
            <circle cx={x} cy={y} r={2.5} fill={C.text} />
            <line x1={x} y1={y} x2={x + (tx - x) * p} y2={y + (ty - y) * p} stroke={C.text} strokeWidth={1.5} />
            <text x={tx} y={ty + (ty < y ? -16 : 36)} fill={C.text} fontFamily={DISPLAY} fontSize={portrait ? 26 : 22} letterSpacing="0.08em"
              textAnchor={tx < W * 0.35 ? "start" : tx > W * 0.65 ? "end" : "middle"} style={{ filter: "drop-shadow(0 0 10px rgba(0,0,0,0.9))" }}>{c.text}</text>
          </g>
        );
      })}
    </svg>
  );
};

// ---------------------------------------------------------------- one film
type Use = { shot: string; dir?: string; copy?: string; crop?: boolean; extra?: (dur: number) => React.ReactNode; end?: boolean; cta?: string };
const SFX: Record<string, { file: string; at: number; vol: number }[]> = {
  hook: [{ file: "snap.wav", at: 19, vol: 0.55 }],
  keys: [{ file: "keys.wav", at: 74, vol: 0.5 }],
  wall: [{ file: "keys.wav", at: 26, vol: 0.45 }],
  spinner: [{ file: "whirr_short.wav", at: 4, vol: 0.3 }],
  spin: [{ file: "whirr_short.wav", at: 6, vol: 0.3 }],
};

export const FilmComp: React.FC<{ film: keyof typeof TL; folder: string; uses: Use[]; cta?: string }> = ({ film, folder, uses, cta }) => {
  const F = TL[film] as Film;
  const { head, portrait, fps } = useLayout();
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      {F.shots.map((s, i) => {
        const u = uses[i];
        const copy = u.copy ? COPY[u.copy]?.(portrait) : undefined;
        return (
          <Sequence key={s.name} name={s.name} from={s.from} durationInFrames={s.dur}>
            <Punch film={F} offset={s.from}>
              {u.end ? <EndCard dur={s.dur} cta={u.cta ?? cta} /> : <Frames dir={`${u.dir ?? folder}/${u.shot}`} avail={availFrames(film, u.shot, s.dur, u.dir)} crop={u.crop} />}
            </Punch>
            {u.extra?.(s.dur)}
            {copy && <Title lines={copy.lines} sub={copy.sub} eyebrow={copy.eyebrow} inAt={6} outAt={s.dur - 14} size={head * (copy.size ?? 1)}
              y={u.copy === "wall" && !portrait ? 70 : undefined}
              scrim={["wall", "keys", "wcolours"].includes(u.copy ?? "") ? 0.3 : 0.78} />}
            {(SFX[u.shot] ?? []).map((x, k) => (
              <Sequence key={k} from={x.at} layout="none"><Audio src={staticFile(`sfx/${x.file}`)} volume={x.vol} /></Sequence>
            ))}
          </Sequence>
        );
      })}
      {/* light leaks: on the drop and into the end card */}
      <Sequence from={F.drop - 6} durationInFrames={22} layout="none"><AbsoluteFill style={{ mixBlendMode: "screen", opacity: 0.6 }}><LightLeak seed={3} hueShift={8} /></AbsoluteFill></Sequence>
      <Sequence from={F.shots[F.shots.length - 1].from - 10} durationInFrames={30} layout="none"><AbsoluteFill style={{ mixBlendMode: "screen", opacity: 0.7 }}><LightLeak seed={7} hueShift={20} /></AbsoluteFill></Sequence>
      <DropFlash at={F.drop} />
      <Post />
      <Audio src={staticFile("music/ritual.mp3")} trimBefore={Math.round(F.song_start * fps)}
        volume={(f) => interpolate(f, [0, 8, F.frames - 24, F.frames - 1], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} />
    </AbsoluteFill>
  );
};

// frames available for a shot (the cut-down borrows the first frames of the longer 9:16 launch shots)
const availFrames = (film: string, shot: string, dur: number, dir?: string) => {
  if (dir) {
    const src = TL.launch.shots.find((s) => s.name === shot);
    return src ? src.dur : dur;
  }
  return dur;
};

// ---------------------------------------------------------------- the five films
export const Launch: React.FC<{ tag: "9x16" | "16x9" }> = ({ tag }) => (
  <FilmComp film="launch" folder={`launch_${tag}`} uses={[
    { shot: "hook", copy: "hook" }, { shot: "detail", copy: "detail" }, { shot: "headlights", copy: "headlights" },
    { shot: "colours", copy: "colours" }, { shot: "flip", copy: "flip" }, { shot: "garage", copy: "garage" },
    { shot: "wall", copy: "wall" }, { shot: "spinner", copy: "spinner" }, { shot: "end", end: true, cta: "Find your car" },
  ]} />
);

export const Cutdown: React.FC = () => (
  <FilmComp film="cutdown" folder="launch_9x16" uses={[
    { shot: "hook", copy: "hook", crop: true, dir: "launch_9x16" }, { shot: "headlights", copy: "headlights", crop: true, dir: "launch_9x16" },
    { shot: "garage", copy: "garage", crop: true, dir: "launch_9x16" }, { shot: "wall", copy: "wall", crop: true, dir: "launch_9x16" },
    { shot: "spinner", copy: "spinner", crop: true, dir: "launch_9x16" }, { shot: "end", end: true, cta: "Find your car" },
  ]} />
);

const SpecsExtra: React.FC = () => {
  const m = meta("spinner_ad_9x16/specs", "specs");
  if (!m.hole) return null;
  return (
    <Callouts items={[
      { at: m.bearing_edge, text: "6804 bearing", to: [m.bearing_edge[0], m.bearing_edge[1] - 0.12], t0: 8 },
      { at: m.hole, text: "20 mm finger hole", to: [Math.min(0.8, m.hole[0] + 0.28), m.hole[1] - 0.2], t0: 20 },
      { at: [(m.left[0] + m.right[0]) / 2, m.left[1] + 0.035], text: TALON_SIZE, to: [(m.left[0] + m.right[0]) / 2, m.left[1] + 0.075], t0: 34 },
    ]} />
  );
};

const PriceExtra: React.FC<{ dur: number }> = () => {
  const { portrait, head, W, H } = useLayout();
  return (
    <>
      <div style={{ position: "absolute", top: portrait ? 240 : 80, left: 0, right: 0, textAlign: "center", width: W }}>
        <Logo width={portrait ? 400 : 300} style={{ margin: "0 auto" }} />
      </div>
      <Title lines={[TALON_PRICE]} eyebrow="Talon keychain spinner" inAt={4} outAt={500} size={head * 1.3} align="center" y={portrait ? H - 740 : H - 360} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: portrait ? 410 : 100, textAlign: "center" }}><Cta label="Get the Talon" at={14} size={portrait ? 28 : 22} /></div>
    </>
  );
};

export const SpinnerAd: React.FC = () => (
  <FilmComp film="spinner_ad" folder="spinner_ad_9x16" uses={[
    { shot: "macro", copy: "macro" }, { shot: "spin", copy: "spin" }, { shot: "specs", extra: () => <SpecsExtra /> },
    { shot: "price", extra: (d) => <PriceExtra dur={d} /> },
  ]} />
);

const MountExtra: React.FC = () => {
  const m = meta("wall_ad_9x16/mount", "mount");
  const { head, portrait } = useLayout();
  if (!m.hole_l) return null;
  return (
    <>
      <Callouts items={[
        { at: m.hole_l, text: "Two countersunk screws", to: [0.08, m.hole_l[1] - 0.16], t0: 10 },
        { at: m.hole_r, text: "or double-sided tape", to: [0.92, m.hole_r[1] + 0.14], t0: 22 },
      ]} />
      <Title lines={portrait ? ["Tape", "or screws."] : ["Tape or screws."]} inAt={6} outAt={62} size={head} y={portrait ? 240 : undefined} />
    </>
  );
};

const LineupExtra: React.FC = () => {
  const { head, portrait } = useLayout();
  return (
    <>
      <Title lines={[`From ${WALL_FROM}`]} inAt={4} outAt={500} size={head} align="center" y={portrait ? 230 : 80} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: portrait ? 410 : 100, textAlign: "center" }}><Cta label="Shop wall key holders" at={12} size={portrait ? 26 : 22} /></div>
    </>
  );
};

export const WallAd: React.FC = () => (
  <FilmComp film="wall_ad" folder="wall_ad_9x16" uses={[
    { shot: "keys", copy: "keys" }, { shot: "colours", copy: "wcolours" }, { shot: "mount", extra: () => <MountExtra /> },
    { shot: "lineup", extra: () => <LineupExtra /> },
  ]} />
);
