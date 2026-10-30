"""Genera SFX basicos (whoosh, pop, hit, riser) como WAV usando solo stdlib.
shortcut: tonos sinteticos simples; reemplazar por archivos reales de un banco de SFX para calidad."""
import math, wave, struct, os
from pathlib import Path

SR = 44100

def _write(path: Path, samples):
    clamped = [max(-32768, min(32767, int(s))) for s in samples]
    with wave.open(str(path), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(struct.pack("<" + "h" * len(clamped), *clamped))

def whoosh(dur=0.4):
    n = int(SR * dur); out = []
    for i in range(n):
        t = i / SR
        freq = 200 + 1200 * (t / dur)
        env = math.sin(math.pi * t / dur)
        out.append(int(32767 * 0.6 * env * math.sin(2 * math.pi * freq * t)))
    return out

def pop(dur=0.12):
    n = int(SR * dur); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 40)
        out.append(int(32767 * 0.8 * env * math.sin(2 * math.pi * 600 * t)))
    return out

def hit(dur=0.15):
    n = int(SR * dur); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 25)
        out.append(int(32767 * 0.9 * env * (math.sin(2 * math.pi * 80 * t) + 0.5 * math.sin(2 * math.pi * 160 * t))))
    return out

def riser(dur=0.6):
    n = int(SR * dur); out = []
    for i in range(n):
        t = i / SR
        freq = 150 + 900 * (t / dur) ** 2
        env = (t / dur)
        out.append(int(32767 * 0.5 * env * math.sin(2 * math.pi * freq * t)))
    return out

def ding(dur=0.2):
    n = int(SR * dur); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 18)
        out.append(int(32767 * 0.7 * env * (math.sin(2*math.pi*880*t) + 0.4*math.sin(2*math.pi*1320*t))))
    return out

def swoosh(dur=0.35):
    n = int(SR * dur); out = []
    for i in range(n):
        t = i / SR
        freq = 300 + 2000 * (t/dur)
        env = math.sin(math.pi * t / dur)
        out.append(int(32767 * 0.5 * env * math.sin(2*math.pi*freq*t)))
    return out

def bass(dur=0.25):
    n = int(SR * dur); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 12)
        out.append(int(32767 * 0.9 * env * math.sin(2*math.pi*60*t)))
    return out

def sparkle(dur=0.25):
    n = int(SR * dur); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 20)
        out.append(int(32767 * 0.4 * env * math.sin(2*math.pi*(1200+800*t)*t)))
    return out

GENS = {"whoosh": whoosh, "pop": pop, "hit": hit, "riser": riser, "ding": ding, "swoosh": swoosh, "bass": bass, "sparkle": sparkle}

def generate_all(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, fn in GENS.items():
        _write(out_dir / f"{name}.wav", fn())
    return list(GENS.keys())