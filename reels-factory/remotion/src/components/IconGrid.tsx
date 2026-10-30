import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
const ICONS: Record<string,string> = { brain:"🧠", code:"💻", lock:"🔒", gear:"⚙️", rocket:"🚀", shield:"🛡️" };
export const IconGrid: React.FC<any> = ({ text, items }) => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const list = items || [text];
  return <AbsoluteFill style={{justifyContent:"center",alignItems:"center",padding:60}}>
    <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:40,textAlign:"center"}}>
      {list.map((it: string, i: number) => {
        const delay = i * 8;
        const s = spring({ frame: f - delay, fps, config: { damping: 14 } });
        const scale = interpolate(s,[0,1],[0,1]);
        const icon = ICONS[it] || "✨";
        return <div key={i} style={{transform:`scale(${scale})`,fontSize:64}}>{icon}<div style={{fontSize:20,marginTop:8}}>{it}</div></div>;
      })}
    </div>
  </AbsoluteFill>;
};