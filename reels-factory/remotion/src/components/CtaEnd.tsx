import React from "react";
import { AbsoluteFill } from "remotion";
export const CtaEnd: React.FC<any> = ({ text }) => (
  <AbsoluteFill style={{justifyContent:"center",alignItems:"center",padding:60}}>
    <div style={{fontSize:60,fontWeight:800,textAlign:"center"}}>{text}</div>
  </AbsoluteFill>
);