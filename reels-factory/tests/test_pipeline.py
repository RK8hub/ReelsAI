import shutil
import subprocess

import pytest

from reels.stages.hyperframes import build
from reels.stages.qa import check


def _scenes():
    return {
        "title": "Prueba",
        "language": "es",
        "scenes": [
            {"id": "s0", "start": 0, "end": 3, "narration": "Uno",
             "on_screen_text": "Uno", "visual_type": "hook_title", "visual_props": {}},
            {"id": "s1", "start": 3, "end": 6, "narration": "Dos",
             "on_screen_text": "Dos", "visual_type": "stat_counter",
             "visual_props": {"value": 3, "label": "capas"}},
        ],
    }


def test_build_genera_html_con_audio_y_escenas(tmp_path):
    out = tmp_path / "hyperframes" / "index.html"
    build(_scenes(), out)
    html = out.read_text()

    assert 'data-duration="6.00"' in html
    assert 'class="scene clip"' in html
    assert 'id="s0"' in html and 'id="s1"' in html
    assert 'id="music"' in html
    assert "assets/music/bed.mp3" in html
    assert "assets/sfx/" in html
    assert 'data-count="3"' in html
    assert "window.__timelines" in html
    assert "None" not in html
    assert (out.parent / "assets" / "music" / "bed.mp3").exists()
    assert any((out.parent / "assets" / "sfx").glob("*.ogg"))


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="requiere ffmpeg")
def test_qa_detecta_formato_y_audio(tmp_path):
    silent = tmp_path / "silent.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=108x192:d=1",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(silent)],
        check=True, capture_output=True)

    problems, _ = check(silent, min_duration=0.5)
    assert "sin pista de audio" in problems
    assert any("resolucion" in p for p in problems)

    with_audio = tmp_path / "audio.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=108x192:d=1",
         "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
         "-shortest", str(with_audio)],
        check=True, capture_output=True)

    problems, info = check(with_audio, min_duration=0.5)
    assert "sin pista de audio" not in problems
    assert info["audio"] == "aac"
