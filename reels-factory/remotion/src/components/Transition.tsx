import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export const Transition: React.FC<{ kind: string; children: React.ReactNode }> = ({ kind, children }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  let opacity = 1, translate = 0, scale = 1;
  const t = Math.min(f, 8);
  if (kind === "fade") opacity = interpolate(t, [0,8],[0,1]);
  else if (kind === "slide_up") translate = interpolate(t,[0,8],[40,0]);
  else if (kind === "zoom_through") scale = interpolate(t,[0,8],[1.15,1]);
  return <div style={{width:"100%",height:"100%",opacity,transform:`translateY(${translate}px) scale(${scale})`}}>{children}</div>;
};