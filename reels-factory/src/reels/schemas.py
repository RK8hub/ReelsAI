from typing import Literal
from pydantic import BaseModel, Field, model_validator

VisualType = Literal[
    "hook_title", "kinetic_text", "stat_counter", "bar_chart", "line_chart",
    "icon_grid", "timeline", "comparison_split", "map_highlight", "quote_card",
    "image_pan_zoom", "generated_clip", "list_reveal", "diagram_flow", "cta_end",
    "character", "environment",
]

Transition = Literal["cut","fade","slide_up","slide_left","zoom_through","glitch","wipe"]
Camera = Literal["static","push_in","pull_out","pan_left","pan_right","shake_light"]

class Brief(BaseModel):
    mode: Literal["A","B","C","D"] = "A"
    topic: str = ""
    language: str = "es"
    audience: str = "publico general"
    tone: str = "curioso y claro"
    target_duration_seconds: int = Field(default=40, ge=10, le=120)
    aspect_ratio: str = "9:16"
    resolution: tuple[int,int] = (1080,1920)
    fps: int = 30
    brand_profile: str = "default"
    visual_mode: Literal["vector","hybrid"] = "vector"
    voice_provider: str = "local"
    draft_voice_provider: str = "local"
    voice_profile: str = "es_narrador_1"
    cta: str = "Siguenme para mas"
    budget_usd_max: float = 2.0

class Scene(BaseModel):
    id: str
    start: float = Field(ge=0)
    end: float
    narration: str = Field(min_length=3)
    on_screen_text: str = Field(default="", max_length=60)
    visual_type: VisualType
    visual_props: dict = {}
    animation: str = ""
    transition_in: Transition = "cut"
    camera: Camera = "static"
    sfx: list[str] = []
    asset_requests: list[dict] = []
    emphasis_words: list[str] = []
    notes: str = ""

    @model_validator(mode="after")
    def check(self):
        if self.end <= self.start:
            raise ValueError("duracion negativa")
        if len(self.on_screen_text.split()) > 7:
            raise ValueError("texto en pantalla demasiado largo (>7 palabras)")
        return self

class ScenesPlan(BaseModel):
    title: str
    language: str = "es"
    scenes: list[Scene]

    @model_validator(mode="after")
    def check_continuity(self):
        s = sorted(self.scenes, key=lambda x: x.start)
        for i in range(1, len(s)):
            if s[i].start < s[i-1].end - 1e-6:
                raise ValueError(f"solape entre {s[i-1].id} y {s[i].id}")
        return self