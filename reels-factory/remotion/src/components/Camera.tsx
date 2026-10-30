import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export const Camera: React.FC<{ kind: string; children: React.ReactNode }> = ({ kind, children }) => {
  const f = useCurrentFrame(); const { fps, durationInFrames } = useVideoConfig();
  let scale = 1, tx = 0;
  if (kind === "push_in") scale = interpolate(f,[0,durationInFrames],[1,1.08]);
  else if (kind === "pull_out") scale = interpolate(f,[0,durationInFrames],[1.08,1]);
  else if (kind === "pan_left") tx = interpolate(f,[0,durationInFrames],[0,-30]);
  else if (kind === "pan_right") tx = interpolate(f,[0,durationInFrames],[0,30]);
  return <div style={{width:"100%",height:"100%",transform:`translateX(${tx}px) scale(${scale})`}}>{children}</div>;
};