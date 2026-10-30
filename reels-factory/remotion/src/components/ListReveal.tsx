import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
export const ListReveal: React.FC<any> = ({ text, items }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const list = items || [text];
  return <AbsoluteFill style={{justifyContent:"center",padding:60}}>
    <div style={{display:"flex",flexDirection:"column",gap:24}}>
      {list.map((it: string, i: number) => {
        const delay = i * 6;
        const opacity = interpolate(f, [delay, delay+8],[0,1], {extrapolateLeft:"clamp",extrapolateRight:"clamp"});
        const x = interpolate(f, [delay, delay+8],[40,0], {extrapolateLeft:"clamp",extrapolateRight:"clamp"});
        return <div key={i} style={{fontSize:44,fontWeight:600,opacity,transform:`translateX(${x}px)`}}>• {it}</div>;
      })}
    </div>
  </AbsoluteFill>;
};