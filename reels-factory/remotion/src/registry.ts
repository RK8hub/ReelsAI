import React from "react";
import { HookTitle } from "./components/HookTitle";
import { KineticText } from "./components/KineticText";
import { CtaEnd } from "./components/CtaEnd";
import { StatCounter } from "./components/StatCounter";
import { ListReveal } from "./components/ListReveal";
import { DiagramFlow } from "./components/DiagramFlow";
import { IconGrid } from "./components/IconGrid";
import { ImagePanZoom } from "./components/ImagePanZoom";
import { Character } from "./components/Character";
import { Environment } from "./components/Environment";

export const registry: Record<string, React.FC<any>> = {
  hook_title: HookTitle,
  kinetic_text: KineticText,
  stat_counter: StatCounter,
  list_reveal: ListReveal,
  diagram_flow: DiagramFlow,
  icon_grid: IconGrid,
  image_pan_zoom: ImagePanZoom,
  character: Character,
  environment: Environment,
  cta_end: CtaEnd,
};