"""Genera una composicion HyperFrames (HTML + GSAP + audio) desde scenes.json.

Salida: <proyecto>/hyperframes/index.html y assets copiados.
Render: `reels hf-render <proyecto>/hyperframes --out output/<id>.mp4`.
"""
import functools
import html
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets"


@functools.lru_cache
def _media_dur(path: Path) -> float:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, check=True).stdout.strip()
        return float(out)
    except Exception:
        return 0.6

PALETTES = [
    ("#0d6b80", "#041c26", "#38e8c6"),
    ("#7a3d10", "#210d04", "#ffb454"),
    ("#0f7a5c", "#06241c", "#4ade80"),
    ("#4b3a9a", "#150e33", "#a78bfa"),
    ("#0f6f93", "#0a2c40", "#5ad1ff"),
    ("#7a1d33", "#25060e", "#ff7a6b"),
    ("#11866a", "#052d24", "#4ade80"),
]

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#04131a;
  font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;color:#fff}
.scene{position:absolute;inset:0;opacity:0}
.bg{position:absolute;inset:0}
.blob{position:absolute;border-radius:50%;filter:blur(70px);opacity:.35}
.title{position:absolute;top:130px;left:70px;right:70px;font-size:80px;font-weight:900;
  line-height:1.02;text-align:center;letter-spacing:-2px;text-shadow:0 8px 0 rgba(0,0,0,.28)}
.visual{position:absolute;left:0;right:0;top:25%;height:54%;display:flex;align-items:center;
  justify-content:center;flex-direction:column;gap:36px}
.cap{position:absolute;left:70px;right:70px;bottom:250px;text-align:center;font-size:46px;
  font-weight:800;line-height:1.16;-webkit-text-stroke:3px #04131a;paint-order:stroke fill}
.col{display:flex;flex-direction:column;align-items:center;gap:34px}
.big span{font-size:210px;font-weight:900;line-height:1;letter-spacing:-6px;
  text-shadow:0 12px 0 rgba(0,0,0,.28)}
.big small{display:block;font-size:40px;font-weight:800;margin-top:14px;text-align:center;max-width:900px}
.headline{font-size:96px;font-weight:900;line-height:1.02;text-align:center;letter-spacing:-3px;
  max-width:920px;text-shadow:0 8px 0 rgba(0,0,0,.28)}
.headline em{font-style:normal;padding:0 10px;border-radius:12px}
.tiles{display:flex;gap:24px;flex-wrap:wrap;justify-content:center;max-width:920px}
.tile{width:190px;height:190px;border-radius:34px;background:rgba(255,255,255,.13);
  border:3px solid rgba(255,255,255,.22);display:flex;flex-direction:column;align-items:center;
  justify-content:center;font-size:76px;backdrop-filter:blur(4px)}
.tile b{font-size:28px;margin-top:10px;font-weight:800;text-align:center;padding:0 6px}
.tl{position:relative;width:820px;height:26px;background:rgba(255,255,255,.22);border-radius:12px;margin-top:54px}
.tl i{position:absolute;left:0;top:0;bottom:0;width:0;border-radius:12px}
.dot{position:absolute;top:-74px;left:0;font-size:74px;transform:translateX(-50%)}
.yrs{display:flex;justify-content:space-between;width:820px;font-weight:800;font-size:34px}
.chips{display:flex;flex-direction:column;gap:24px;align-items:center}
.chips span{background:rgba(255,255,255,.14);border:4px solid;border-radius:99px;
  padding:18px 46px;font-size:40px;font-weight:800}
.flow{display:flex;flex-direction:column;gap:16px;align-items:center}
.node{font-size:36px;font-weight:800;padding:20px 34px;border:4px solid;border-radius:18px;
  max-width:900px;text-align:center;background:rgba(0,0,0,.22)}
.arrow{font-size:40px;opacity:.7}
.heart{font-size:210px}
.progress{position:absolute;top:0;left:0;right:0;height:10px;background:rgba(255,255,255,.12);z-index:9}
.progress i{display:block;height:100%;width:0}
.flash{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none;z-index:8}
.particle{position:absolute;border-radius:50%;background:#fff;opacity:.25}
"""


def _esc(s: str) -> str:
    return html.escape(str(s))


def _visual(vt: str, text: str, props: dict, accent: str) -> str:
    if vt == "stat_counter":
        label = _esc(props.get("label", text))
        return (f'<div class="col"><div class="big">'
                f'<span data-count="{int(props.get("value", 0))}" style="color:{accent}">0</span>'
                f'<small>{label}</small></div></div>')
    if vt == "icon_grid":
        items = props.get("items") or [{"icon": "✨", "label": text}]
        out = []
        for it in items:
            if isinstance(it, dict):
                out.append(f'<div class="tile">{_esc(it.get("icon", "✨"))}'
                           f'<b>{_esc(it.get("label", ""))}</b></div>')
            else:
                out.append(f'<div class="tile">{_esc(it)}</div>')
        return '<div class="tiles">' + "".join(out) + "</div>"
    if vt == "list_reveal":
        items = props.get("items") or [text]
        return ('<div class="chips">'
                + "".join(f'<span style="border-color:{accent}">{_esc(i)}</span>' for i in items)
                + "</div>")
    if vt == "diagram_flow":
        nodes = props.get("nodes") or [text]
        parts = []
        for i, n in enumerate(nodes):
            if i:
                parts.append(f'<div class="arrow" style="color:{accent}">↓</div>')
            parts.append(f'<div class="node" style="border-color:{accent}">{_esc(n)}</div>')
        return '<div class="flow">' + "".join(parts) + "</div>"
    if vt == "timeline":
        year = _esc(props.get("year", "1832"))
        return (f'<div class="col"><div class="big"><span data-count="{int(props.get("value", 0))}" '
                f'style="color:{accent}">0</span><small>{_esc(props.get("label", text))}</small></div>'
                f'<div class="tl"><i class="bar" style="background:{accent}"></i>'
                f'<div class="dot">🐢</div></div>'
                f'<div class="yrs"><span>{year}</span><span>hoy</span></div></div>')
    if vt == "character":
        return ('<svg viewBox="0 0 280 340" width="320" height="390">'
                '<circle cx="140" cy="92" r="62" fill="#fbbf24"/>'
                '<circle cx="118" cy="82" r="9" fill="#111"/><circle cx="162" cy="82" r="9" fill="#111"/>'
                '<path d="M118 114 Q140 136 162 114" stroke="#111" stroke-width="5" fill="none" stroke-linecap="round"/>'
                '<rect x="102" y="152" width="76" height="128" rx="16" fill="#3b82f6"/>'
                '<rect x="70" y="176" width="28" height="96" rx="12" fill="#3b82f6"/>'
                '<rect x="182" y="176" width="28" height="96" rx="12" fill="#3b82f6"/>'
                '<rect x="112" y="280" width="22" height="52" rx="10" fill="#1e3a8a"/>'
                '<rect x="146" y="280" width="22" height="52" rx="10" fill="#1e3a8a"/></svg>')
    if vt == "environment":
        buildings = "".join(
            f'<rect x="{i*138}" y="{860-(220+(i*47)%380)}" width="118" '
            f'height="{220+(i*47)%380}" rx="6" fill="#334155" opacity=".65"/>'
            for i in range(8))
        windows = "".join(
            f'<circle cx="{(i*97)%1080}" cy="{120+(i*131)%760}" r="4" fill="{accent}" opacity=".8"/>'
            for i in range(16))
        return (f'<svg viewBox="0 0 1080 900" width="1080" height="900">'
                f'{buildings}{windows}</svg>')
    if vt == "cta_end":
        return ('<div class="col"><div class="heart">💚</div>'
                '<div class="chips"><span style="border-color:#4ade80">Sígueme</span>'
                '<span style="border-color:#4ade80">Guarda esto</span></div></div>')
    if vt == "hook_title":
        return f'<div class="headline">{_esc(text)}</div>'
    return f'<div class="headline">{_esc(text)}</div>'


def _sfx_tag(src: str, start: float, track: int, vol: float = 0.7) -> str:
    dur = _media_dur(ASSETS / "sfx" / src)
    return (f'<audio id="sfx_{track}_{int(start * 1000)}" data-start="{start:.3f}" '
            f'data-duration="{dur:.3f}" data-track-index="{track}" '
            f'src="assets/sfx/{src}" data-volume="{vol}"></audio>')


def build(scenes: dict, out: Path) -> Path:
    sc = scenes["scenes"]
    total = max(s["end"] for s in sc) if sc else 5.0

    # assets
    adir = out.parent / "assets"
    (adir / "sfx").mkdir(parents=True, exist_ok=True)
    (adir / "music").mkdir(parents=True, exist_ok=True)
    for f in (ASSETS / "sfx").glob("*.ogg"):
        shutil.copy2(f, adir / "sfx" / f.name)
    for f in (ASSETS / "music").glob("*.mp3"):
        shutil.copy2(f, adir / "music" / f.name)

    parts, tl, audio = [], [], []
    audio.append(f'<audio id="music" data-start="0" data-duration="{total:.3f}" data-track-index="1" '
                 f'src="assets/music/bed.mp3" data-volume="0.42" data-fade-in="1" '
                 f'data-fade-out="2"></audio>')

    for i, s in enumerate(sc):
        c0, c1, accent = PALETTES[i % len(PALETTES)]
        vt = s.get("visual_type", "kinetic_text")
        props = s.get("visual_props", {})
        text = s.get("on_screen_text") or s.get("narration", "")
        dur = s["end"] - s["start"]
        particles = "".join(
            f'<div class="particle" style="left:{(i*137+j*211)%1040}px;top:{(i*97+j*173)%1800}px;'
            f'width:{4+(j%4)*3}px;height:{4+(j%4)*3}px"></div>' for j in range(6))
        parts.append(
            f'<section class="scene clip" id="s{i}" data-start="{s["start"]}" '
            f'data-duration="{dur}" data-track-index="0" data-track-kind="graphics">'
            f'<div class="bg" style="background:linear-gradient(165deg,{c0},{c1})"></div>'
            f'<div class="blob" data-layout-allow-overflow style="width:620px;height:620px;left:-160px;top:-120px;background:{accent}"></div>'
            f'<div class="blob" data-layout-allow-overflow style="width:520px;height:520px;right:-180px;bottom:120px;background:{accent}"></div>'
            f'{particles}'
            f'<h2 class="title" id="t{i}">{_esc(s.get("on_screen_text") or scenes.get("title", ""))}</h2>'
            f'<div class="visual" id="v{i}">{_visual(vt, text, props, accent)}</div>'
            f'<div class="cap">{_esc(s.get("narration", ""))}</div></section>'
        )

        st = s["start"]
        tl.append(f'tl.set("#s{i}",{{opacity:1}},{st});')
        tl.append(f'tl.from("#t{i}",{{scale:.55,rotate:-3,opacity:0,duration:.55,'
                  f'ease:"back.out(1.7)"}},{st});')
        tl.append(f'tl.from("#v{i}",{{y:70,opacity:0,scale:.72,duration:.7,'
                  f'ease:"back.out(1.4)"}},{st+0.18});')
        tl.append(f'tl.from("#s{i} .particle",{{scale:0,opacity:0,duration:.5,stagger:.05,'
                  f'ease:"power2.out"}},{st+0.1});')
        if vt in ("stat_counter", "timeline"):
            tl.append(f'counter("s{i}",{int(props.get("value", 0))},{st+0.4},2.0);')
        if vt == "timeline":
            tl.append(f'tl.to("#s{i} .bar",{{width:820,duration:{max(1.2, dur-2):.2f},'
                      f'ease:"none"}},{st+0.4});')
            tl.append(f'tl.to("#s{i} .dot",{{left:820,duration:{max(1.2, dur-2):.2f},'
                      f'ease:"none"}},{st+0.4});')
        if vt == "icon_grid":
            tl.append(f'tl.from("#s{i} .tile",{{scale:0,opacity:0,duration:.45,stagger:.12,'
                      f'ease:"back.out(1.8)"}},{st+0.3});')
        if vt == "list_reveal":
            tl.append(f'tl.from("#s{i} .chips span",{{x:-60,opacity:0,duration:.45,stagger:.15,'
                      f'ease:"power3.out"}},{st+0.3});')
        if vt == "diagram_flow":
            tl.append(f'tl.from("#s{i} .node",{{y:30,opacity:0,duration:.45,stagger:.2,'
                      f'ease:"power2.out"}},{st+0.3});')
        if vt == "cta_end":
            tl.append(f'tl.from("#s{i} .heart",{{scale:0,rotate:-25,duration:.7,'
                      f'ease:"back.out(2.2)"}},{st+0.25});')

        # audio: whoosh on cut, pop on landing, special accents
        if i > 0:
            audio.append(_sfx_tag(f"whoosh{1 + i % 3}.ogg", st, 2, 0.8))
        if vt in ("stat_counter", "timeline"):
            audio.append(_sfx_tag(f"pop{1 + i % 3}.ogg", st + 0.4, 3, 0.9))
        elif vt in ("icon_grid", "list_reveal", "diagram_flow"):
            audio.append(_sfx_tag(f"pop{1 + i % 3}.ogg", st + 0.3, 3, 0.75))
        elif vt == "cta_end":
            audio.append(_sfx_tag("success.ogg", st + 0.25, 3, 0.95))
        elif i == 0:
            audio.append(_sfx_tag("impact.ogg", st, 3, 0.9))
        if s.get("visual_type") == "diagram_flow" and i >= 4:
            audio.append(_sfx_tag("impact.ogg", st + 0.5, 4, 0.6))

    # progress bar over the whole film
    tl.append(f'tl.to("#prog",{{width:1080,duration:{total:.2f},ease:"none"}},0);')
    for s in sc:
        tl.append(f'tl.set("#flash",{{opacity:.5}},{s["start"]});')
        tl.append(f'tl.to("#flash",{{opacity:0,duration:.45,ease:"power1.out"}},{s["start"]});')

    timeline = "\n".join(tl)
    audios = "\n".join(audio)
    doc = f"""<!doctype html><html lang="es"><head><meta charset="UTF-8"/>
<meta name="viewport" content="width=1080,height=1920"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}"
 data-width="1080" data-height="1920">
<div class="progress"><i id="prog"></i></div>
{''.join(parts)}
<div class="flash" id="flash"></div>
{audios}
</div>
<script>
const tl=gsap.timeline({{paused:true}});
window.__timelines=window.__timelines||{{}};window.__timelines["main"]=tl;
function counter(sceneId,to,at,dur){{
  const root=document.getElementById(sceneId);
  const el=root&&root.querySelector("[data-count]");
  if(!el)return;
  const o={{v:0}};
  tl.to(o,{{v:to,duration:dur,ease:"power2.out",
    onUpdate:()=>{{el.textContent=Math.round(o.v);}}}},at);
}}
{timeline}
tl.seek(0);
</script></body></html>"""
    out.write_text(doc)
    return out
