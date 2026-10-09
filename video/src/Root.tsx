import React from "react";
import { Composition } from "remotion";
import { Cutdown, Launch, SpinnerAd, TL, WallAd } from "./Film";
import { Oner, ONER_FRAMES } from "./Oner";

const L916: React.FC = () => <Launch tag="9x16" />;
const L169: React.FC = () => <Launch tag="16x9" />;

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Launch9x16" component={L916} durationInFrames={TL.launch.frames} fps={TL.fps} width={1080} height={1920} />
    <Composition id="Launch16x9" component={L169} durationInFrames={TL.launch.frames} fps={TL.fps} width={1920} height={1080} />
    <Composition id="Cutdown1x1" component={Cutdown} durationInFrames={TL.cutdown.frames} fps={TL.fps} width={1080} height={1080} />
    <Composition id="Spinner9x16" component={SpinnerAd} durationInFrames={TL.spinner_ad.frames} fps={TL.fps} width={1080} height={1920} />
    <Composition id="Oner9x16" component={Oner} durationInFrames={ONER_FRAMES} fps={TL.fps} width={1080} height={1920} />
    <Composition id="Wall9x16" component={WallAd} durationInFrames={TL.wall_ad.frames} fps={TL.fps} width={1080} height={1920} />
  </>
);
