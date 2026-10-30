import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
// Personaje SVG simple (cabeza + cuerpo) con animacion de entrada y parpadeo
export const Character: React.FC<any> = ({ text }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const s = spring({ frame: f, fps, config: { damping: 10 } });
  const y = interpolate(s, [0,1],[60,0]);
  const opacity = interpolate(s, [0,1],[0,1]);
  const blink = (f % 90) < 6 ? 0.15 : 1; // parpadeo cada ~3s
  return <AbsoluteFill style={{justifyContent:"center",alignItems:"center",padding:60,opacity}}>
    <svg width="260" height="320" viewBox="0 0 260 320" style={{transform:`translateY(${y}px)`}}>
      <circle cx="130" cy="90" r="60" fill="#fbbf24" />
      <ellipse cx="110" cy="80" rx="8" ry={8*blink} fill="#111" />
      <ellipse cx="150" cy="80" rx="8" ry={8*blink} fill="#111" />
      <path d="M110 110 Q130 130 150 110" stroke="#111" strokeWidth="4" fill="none" />
      <rect x="95" y="150" width="70" height="120" rx="12" fill="#3b82f6" />
      <rect x="70" y="170" width="25" height="90" rx="10" fill="#3b82f6" />
      <rect x="165" y="170" width="25" height="90" rx="10" fill="#3b82f6" />
    </svg>
    <div style={{fontSize:36,fontWeight:700,textAlign:"center",marginTop:20,maxWidth:900}}>{text}</div>
  </AbsoluteFill>;
};