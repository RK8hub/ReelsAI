import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
export const ImagePanZoom: React.FC<any> = ({ text }) => {
  const f = useCurrentFrame(); const { durationInFrames } = useVideoConfig();
  const scale = interpolate(f, [0,durationInFrames],[1,1.15]);
  const tx = interpolate(f, [0,durationInFrames],[0,-20]);
  return <AbsoluteFill style={{overflow:"hidden",background:"linear-gradient(135deg,#1e3a8a,#0f172a)"}}>
    <div style={{width:"100%",height:"100%",transform:`scale(${scale}) translateX(${tx}px)`,display:"flex",justifyContent:"center",alignItems:"center"}}>
      <div style={{fontSize:52,fontWeight:700,textAlign:"center",padding:60,color:"#fff"}}>{text}</div>
    </div>
  </AbsoluteFill>;
};