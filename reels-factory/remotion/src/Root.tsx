import React from "react";
import { Composition } from "remotion";
import { Reel } from "./Reel";

export const Root: React.FC = () => (
  <Composition id="Reel" component={Reel}
    calculateMetadata={async ({ props }: any) => {
      const scenes = props?.plan?.scenes || [];
      const last = scenes.reduce((m: number, s: any) => Math.max(m, s.end || 0), 0);
      return { durationInFrames: Math.max(30, Math.round((last || 1) * 30)) };
    }}
    durationInFrames={30}
    fps={30} width={1080} height={1920} defaultProps={{ plan: { scenes: [] } }} />
);