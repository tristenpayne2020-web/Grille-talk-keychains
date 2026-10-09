import { Audio } from "@remotion/media";
import { LightLeak } from "@remotion/light-leaks";
import React from "react";
import { AbsoluteFill, Img, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, DISPLAY } from "./brand";
import { N_CARS, TALON_PRICE, WALL_FROM } from "./data";
import { EndCard } from "./EndCard";
import { ease, Post, Title, useLayout } from "./fx";
import T from "./timeline.json";

// The one-take ad: three continuous Blender acts (keychains, wall key holder, spinners) joined by "dive" transitions
// (the camera flies into the back of the product; here the frame keeps pushing, blurs and goes dark, and the next act
// arrives out of the dark), cut to the song's bars. All copy comes from the catalog.
type Shot = { name: string; from: number; dur: number };
type Edit = { song: string; scale: number; song_start: number; frames: number; drop: number };
const TT = T as unknown as { oner: { frames: number; drop: number; shots: Shot[] }; oner_edit: Edit; fps: number };
// the Blender acts are timed in "source" frames (Ritual's bar); the edit plays them SCALE x faster so the cuts land on
// the bars of the chosen song (Fresh and Frisky). All times below are output frames.
const E = TT.oner_edit;
const SC = E.scale;
const sc = (x: number) => Math.round(x / SC);
const SRC = Object.fromEntries(TT.oner.shots.map((s) => [s.name, s])) as Record<string, Shot>;
const at = (n: string) => sc(SRC[n].from);
const end = (n: string) => sc(SRC[n].from + SRC[n].dur);
const S = Object.fromEntries(TT.oner.shots.map((s) => [s.name, { name: s.name, from: at(s.name), dur: end(s.name) - at(s.name) }])) as Record<string, Shot>;
const O = { song_start: E.song_start, frames: E.frames, drop: E.drop };
const pad = (n: number) => String(n).padStart(4, "0");

const ACTS = [
  { act: "kc", from: 0, to: end("dive"), src: SRC["dive"].from + SRC["dive"].dur },
  { act: "wall", from: at("w_details"), to: end("w_dive"), src: SRC["w_dive"].from + SRC["w_dive"].dur - SRC["w_details"].from },
  { act: "spin", from: at("spin"), to: end("spin"), src: SRC["spin"].dur },
];
const DIVE = 12; // frames of the push-into-dark at the end of an act and the arrival at the start of the next

const ActFrames: React.FC<{ act: string; len: number; src: number; diveOut: boolean; diveIn: boolean }> = ({ act, len, src, diveOut, diveIn }) => {
  const f = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const o = diveOut ? ease(f, len - DIVE, len) : 0;           // 0 -> 1 over the last frames
  const i = diveIn ? 1 - ease(f, 0, DIVE) : 0;               // 1 -> 0 over the first frames
  const scale = 1 + 0.55 * o * o + 0.25 * i;
  const blur = 18 * o + 14 * i;
  const bright = 1 - 0.92 * o - 0.85 * i;
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Img src={staticFile(`shots/oner_9x16/${act}/${pad(Math.min(src - 1, Math.round(f * SC)))}.jpg`)}
        style={{ position: "absolute", inset: 0, width, height, transform: `scale(${scale})`, filter: `blur(${blur}px) brightness(${bright})` }} />
    </AbsoluteFill>
  );
};

// small caption that labels the detail the camera is on
const Caption: React.FC<{ text: string; inAt: number; outAt: number; index: string }> = ({ text, inAt, outAt, index }) => {
  const f = useCurrentFrame();
  const { W, H, portrait } = useLayout();
  const p = ease(f, inAt, inAt + 12) * (1 - ease(f, outAt - 8, outAt));
  if (p <= 0) return null;
  return (
    <div style={{ position: "absolute", left: 64, right: 64, top: portrait ? H * 0.68 : H * 0.72, display: "flex", alignItems: "center", gap: 18,
      opacity: p, transform: `translateY(${(1 - p) * 16}px)`, width: W - 128 }}>
      <span style={{ fontFamily: DISPLAY, fontSize: 22, color: "#cfcdc8", letterSpacing: "0.3em" }}>{index}</span>
      <span style={{ width: 70 * p, height: 1, background: C.text }} />
      <span style={{ fontFamily: DISPLAY, fontSize: portrait ? 40 : 32, color: C.text, letterSpacing: "0.08em", textTransform: "uppercase",
        textShadow: "0 0 18px rgba(0,0,0,0.9)" }}>{text}</span>
    </div>
  );
};

export const Oner: React.FC = () => {
  const { head, portrait, fps } = useLayout();
  const d0 = at("w_details"), dd = S["w_details"].dur / 3;
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      {ACTS.map((a, k) => (
        <Sequence key={a.act} name={a.act} from={a.from} durationInFrames={a.to - a.from}>
          <ActFrames act={a.act} len={a.to - a.from} src={a.src} diveOut={k < ACTS.length - 1} diveIn={k > 0} />
        </Sequence>
      ))}
      <Sequence name="end" from={at("end")} durationInFrames={S["end"].dur}>
        <EndCard dur={S["end"].dur} cta="Find your car" />
      </Sequence>

      {/* copy */}
      <Sequence from={0} durationInFrames={end("intro")} layout="none">
        <Title lines={portrait ? ["Your keys", "should match", "your car."] : ["Your keys should", "match your car."]} inAt={8} outAt={end("intro") - 12} size={head} />
      </Sequence>
      <Sequence from={at("burst") + 30} durationInFrames={S["burst"].dur} layout="none">
        <Title lines={[`${N_CARS} cars`, "and counting."]} inAt={0} outAt={S["burst"].dur - 40} size={head} />
      </Sequence>
      <Sequence from={at("flip") + 14} durationInFrames={end("back") - at("flip") - 14} layout="none">
        <Title lines={["Flip it."]} sub="Carbon-fibre textured back" inAt={0} outAt={end("back") - at("flip") - 40} size={head * 1.1} />
      </Sequence>
      <Sequence from={d0} durationInFrames={S["w_details"].dur} layout="none">
        <Caption index="01" text="Light signature" inAt={DIVE} outAt={dd} />
        <Caption index="02" text="Grille" inAt={dd + 6} outAt={2 * dd} />
        <Caption index="03" text="Four key hooks" inAt={2 * dd + 6} outAt={3 * dd} />
      </Sequence>
      <Sequence from={at("w_out")} durationInFrames={end("w_home") - at("w_out")} layout="none">
        <Title lines={portrait ? ["Your car,", "by the", "front door."] : ["Your car,", "by the front door."]} sub={`Wall key holders from ${WALL_FROM}`}
          inAt={4} outAt={end("w_home") - at("w_out") - 16} size={head} />
      </Sequence>
      <Sequence from={at("spin") + 20} durationInFrames={S["spin"].dur - 20} layout="none">
        <Title lines={portrait ? ["Three", "keychain", "spinners."] : ["Three keychain", "spinners."]} sub={`${TALON_PRICE} each`}
          eyebrow={"Talon · Karambit · Shield"} inAt={0} outAt={S["spin"].dur - 34} size={head} />
      </Sequence>

      {/* light: a leak on the drop and into the end card */}
      <Sequence from={O.drop - 6} durationInFrames={22} layout="none">
        <AbsoluteFill style={{ mixBlendMode: "screen", opacity: 0.55 }}><LightLeak seed={3} hueShift={8} /></AbsoluteFill>
      </Sequence>
      <Sequence from={at("end") - 10} durationInFrames={30} layout="none">
        <AbsoluteFill style={{ mixBlendMode: "screen", opacity: 0.65 }}><LightLeak seed={7} hueShift={20} /></AbsoluteFill>
      </Sequence>
      <Post />
      <Audio src={staticFile(E.song)} trimBefore={Math.round(O.song_start * fps)}
        volume={(f) => interpolate(f, [0, 8, O.frames - 30, O.frames - 1], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} />
    </AbsoluteFill>
  );
};

export const ONER_FRAMES = O.frames;
