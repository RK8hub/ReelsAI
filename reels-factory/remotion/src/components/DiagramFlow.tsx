import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
export const DiagramFlow: React.FC<any> = ({ text, nodes }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const ns = nodes || [text];
  return <AbsoluteFill style={{justifyContent:"center",alignItems:"center",padding:60}}>
    <div style={{display:"flex",flexDirection:"column",gap:30,alignItems:"center"}}>
      {ns.map((n: string, i: number) => {
        const delay = i * 10;
        const s = spring({ frame: f - delay, fps, config: { damping: 12 } });
        const scale = interpolate(s, [0,1],[0.6,1]);
        const opacity = interpolate(s, [0,1],[0,1]);
        return <div key={i} style={{fontSize:40,fontWeight:700,padding:"16px 28px",border:"3px solid #4ade80",borderRadius:12,opacity,transform:`scale(${scale})`,textAlign:"center",maxWidth:900}}>{n}</div>;
      })}
    </div>
  </AbsoluteFill>;
};