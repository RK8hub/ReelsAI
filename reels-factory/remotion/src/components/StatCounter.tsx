import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
export const StatCounter: React.FC<any> = ({ text, value, unit, label }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const s = spring({ frame: f, fps, config: { damping: 14 } });
  const num = Math.round(interpolate(s, [0,1],[0, value || 0]));
  return <AbsoluteFill style={{justifyContent:"center",alignItems:"center",padding:60,flexDirection:"column",gap:20}}>
    <div style={{fontSize:120,fontWeight:900}}>{num}{unit || ""}</div>
    <div style={{fontSize:36,opacity:0.8,textAlign:"center"}}>{label || text}</div>
  </AbsoluteFill>;
};