"""QA de un MP4: formato, resolución, duración, audio y loudness."""
import json
import subprocess
from pathlib import Path


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), {})
    return {
        "duration": float(d["format"].get("duration", 0)),
        "width": v.get("width"),
        "height": v.get("height"),
        "fps": v.get("avg_frame_rate"),
        "video": v.get("codec_name"),
        "audio": a.get("codec_name"),
        "channels": a.get("channels"),
        "sample_rate": a.get("sample_rate"),
    }


def loudness(path: Path) -> dict:
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-af", "loudnorm=print_format=json",
         "-f", "null", "-"], capture_output=True, text=True).stderr
    raw = out[out.rfind("{"):out.rfind("}") + 1]
    d = json.loads(raw)
    return {"lufs": float(d["input_i"]), "true_peak": float(d["input_tp"])}


def check(path: Path, min_duration: float = 5) -> tuple[list[str], dict]:
    p = probe(path)
    problems = []
    if (p["width"], p["height"]) != (1080, 1920):
        problems.append(f"resolucion {p['width']}x{p['height']} != 1080x1920")
    if p["duration"] < min_duration:
        problems.append(f"duracion {p['duration']:.1f}s < {min_duration}s")
    if not p["audio"]:
        problems.append("sin pista de audio")
    else:
        l = loudness(path)
        if not -17 <= l["lufs"] <= -13:
            problems.append(f"loudness {l['lufs']:.1f} LUFS fuera de -17..-13")
        if l["true_peak"] > -1.0:
            problems.append(f"true peak {l['true_peak']:.1f} dBTP > -1.0")
        p.update(l)
    return problems, p
