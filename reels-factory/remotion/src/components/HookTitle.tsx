import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
export const HookTitle: React.FC<any> = ({ text, accent }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const s = spring({ frame: f, fps, config: { damping: 8, stiffness: 200 } });
  const scale = interpolate(s, [0,1],[1.4,1]);
  // shake ligero los primeros 6 frames
  const shake = f < 6 ? Math.sin(f * 4) * 6 : 0;
  const opacity = interpolate(f, [0,4],[0,1], {extrapolateRight:"clamp"});
  return <AbsoluteFill style={{justifyContent:"center",alignItems:"center",padding:60,opacity}}>
    <div style={{fontSize:76,fontWeight:900,textAlign:"center",transform:`scale(${scale}) translateX(${shake}px)`,color: accent || "#fff",textShadow:"0 4px 20px rgba(0,0,0,0.6)"}}>{text}</div>
  </AbsoluteFill>;
};