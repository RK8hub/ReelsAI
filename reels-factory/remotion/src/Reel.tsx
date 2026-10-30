import React from "react";
import { AbsoluteFill, Sequence, Audio, staticFile, useVideoConfig } from "remotion";
import { registry } from "./registry";
import { Transition } from "./components/Transition";
import { Camera } from "./components/Camera";

export const Reel: React.FC<any> = ({ plan }) => {
  const { fps } = useVideoConfig();
  const scenes = plan?.scenes || [];
  return (
    <AbsoluteFill style={{ background: "#0b0f1a", color: "#fff", fontFamily: "sans-serif" }}>
      {scenes.map((s: any) => {
        const C = registry[s.visual_type] || registry.kinetic_text;
        const dur = Math.max(1, Math.round((s.end - s.start) * fps));
        return (
          <Sequence key={s.id} from={Math.round(s.start * fps)} durationInFrames={dur}>
            <Transition kind={s.transition_in}>
              <Camera kind={s.camera}>
                <C text={s.on_screen_text} narration={s.narration} />
              </Camera>
            </Transition>
            {(s.sfx || []).map((sx: string, i: number) => (
              <Audio key={i} src={staticFile(`sfx/${sx}.wav`)} volume={0.6} />
            ))}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};