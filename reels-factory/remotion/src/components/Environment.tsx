import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
// Fondo con edificios/codigo animados (estilo cyber)
export const Environment: React.FC<any> = ({ text }) => {
  const f = useCurrentFrame(); const { durationInFrames } = useVideoConfig();
  const tx = interpolate(f, [0,durationInFrames],[0,-60]);
  return <AbsoluteFill style={{background:"linear-gradient(180deg,#0f172a,#1e293b)",overflow:"hidden"}}>
    <svg width="1080" height="1920" style={{transform:`translateX(${tx}px)`}}>
      {[...Array(8)].map((_,i) => {
        const h = 200 + (i*37)%400;
        const x = i*140;
        return <rect key={i} x={x} y={1920-h} width="120" height={h} fill="#334155" opacity="0.6" />;
      })}
      {[...Array(12)].map((_,i) => {
        const x = (i*90 + f*2) % 1080;
        const y = 200 + (i*130) % 1200;
        return <circle key={i} cx={x} cy={y} r="3" fill="#4ade80" opacity="0.8" />;
      })}
    </svg>
    <div style={{position:"absolute",bottom:500,left:60,right:60,fontSize:44,fontWeight:700,textAlign:"center",color:"#fff"}}>{text}</div>
  </AbsoluteFill>;
};