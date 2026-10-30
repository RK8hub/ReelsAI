"""Planificador determinista minimo: convierte un guion (texto) en ScenesPlan.
shortcut: sin LLM ni validacion semantica; un visual_type por defecto; tiempos por ritmo 2.7 wps. Usar planner LLM en fases posteriores."""
import re
from reels.schemas import Scene, ScenesPlan

WPS = 2.7

def plan_from_text(title: str, text: str, lang: str = "es") -> ScenesPlan:
    # Split en frases
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    scenes = []
    t = 0.0
    for i, s in enumerate(sentences, 1):
        words = len(s.split())
        dur = max(1.5, words / WPS)
        # hook la primera, cta la ultima
        low = s.lower()
        if i == 1:
            vt = "hook_title"; sfx = ["hit"]; trans = "cut"; cam = "push_in"; props = {}
        elif i == len(sentences):
            vt = "cta_end"; sfx = ["riser"]; trans = "fade"; cam = "pull_out"; props = {}
        elif any(k in low for k in ["php","node","codigo","vulnerab","servidor"]):
            vt = "diagram_flow"; sfx = ["bass"]; trans = "slide_up"; cam = "static"
            props = {"nodes": [s]}
        elif any(k in low for k in ["ia","modelo","inteligencia","avanza"]):
            vt = "character"; sfx = ["sparkle"]; trans = "zoom_through"; cam = "push_in"
            props = {}
        elif any(k in low for k in ["octubre","actualiza","riesgo","revision"]):
            vt = "environment"; sfx = ["swoosh"]; trans = "fade"; cam = "pan_right"
            props = {}
        else:
            vt = "kinetic_text"; sfx = ["whoosh"]; trans = "slide_up"; cam = "static"; props = {}
        onscreen = " ".join(s.split()[:7])
        scenes.append(Scene(
            id=f"scene_{i:02d}",
            start=round(t, 2),
            end=round(t + dur, 2),
            narration=s,
            on_screen_text=onscreen,
            visual_type=vt,
            visual_props=props,
            animation=f"Entrada por defecto para {vt}",
            transition_in=trans,
            camera=cam,
            sfx=sfx,
        ))
        t += dur
    return ScenesPlan(title=title or "Sin titulo", language=lang, scenes=scenes)