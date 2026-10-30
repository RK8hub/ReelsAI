import React from "react";
import { AbsoluteFill } from "remotion";
export const KineticText: React.FC<any> = ({ text }) => (
  <AbsoluteFill style={{justifyContent:"center",alignItems:"center",padding:60}}>
    <div style={{fontSize:56,fontWeight:700,textAlign:"center",lineHeight:1.2}}>{text}</div>
  </AbsoluteFill>
);