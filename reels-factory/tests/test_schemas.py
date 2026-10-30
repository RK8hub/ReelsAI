import sys; sys.path.insert(0,"src")
from reels.schemas import Scene, ScenesPlan
from reels.stages.plan_simple import plan_from_text

def test_plan_roundtrip():
    p = plan_from_text("t", "Hola mundo. Esto es una prueba.", "es")
    j = p.model_dump_json()
    p2 = ScenesPlan.model_validate_json(j)
    assert p2 == p

def test_text_too_long():
    try:
        Scene(id="s", start=0, end=1, narration="x", on_screen_text="a b c d e f g h", visual_type="kinetic_text")
        assert False
    except Exception:
        pass