import json
from pathlib import Path
import typer
from rich.console import Console
from reels.schemas import Brief
from reels.state import new_project, set_state
from reels.stages.plan_simple import plan_from_text

app = typer.Typer(help="Reels factory MVP")
console = Console()
ROOT = Path(__file__).resolve().parents[2]

@app.command()
def new(topic: str = typer.Option("", help="Tema"),
        script: Path = typer.Option(None, help="Archivo .md/.txt con guion"),
        duration: int = typer.Option(40, help="Duracion objetivo s"),
        lang: str = typer.Option("es", help="Idioma")):
    brief = Brief(topic=topic or (script.stem if script else "proyecto"),
                  language=lang, target_duration_seconds=duration)
    proj = new_project(ROOT, brief)
    console.print(f"Proyecto creado: {proj}")
    text = script.read_text() if script else f"{topic}. " * 5
    plan = plan_from_text(brief.topic, text, lang)
    (proj / "scenes.json").write_text(plan.model_dump_json(indent=2))
    set_state(proj, "planning")
    console.print(f"Escenas: {len(plan.scenes)} -> {proj/'scenes.json'}")
    console.print("Siguiente: reels render " + str(proj))

@app.command()
def render(project: Path, preview: bool = typer.Option(False, "--preview")):
    import subprocess, shutil
    proj = project
    scenes = json.loads((proj / "scenes.json").read_text())
    resolved = proj / "scenes.resolved.json"
    resolved.write_text(json.dumps(scenes, indent=2))
    # Remotion recibe {plan: ...}
    (proj / "inputProps.json").write_text(json.dumps({"plan": scenes}, indent=2))
    import shutil
    remotion = ROOT / "remotion"
    sfx_src = proj / "assets" / "sfx"
    sfx_dst = remotion / "public" / "sfx"
    if sfx_src.exists():
        sfx_dst.mkdir(parents=True, exist_ok=True)
        for f in sfx_src.iterdir():
            shutil.copy2(f, sfx_dst / f.name)
    out = proj / "renders" / ("preview.mp4" if preview else "final.mp4")
    out.parent.mkdir(exist_ok=True)
    if not (remotion / "node_modules").exists():
        console.print("[yellow]Instalando deps remotion...[/yellow]")
        subprocess.run(["npm","install"], cwd=remotion, check=True)
    cmd = ["npx","remotion","render","src/index.tsx","Reel", str(out.absolute()),
           "--props", str((proj / "inputProps.json").absolute())]
    if preview:
        cmd += ["--scale","0.5"]
    console.print(" ".join(cmd))
    subprocess.run(cmd, cwd=remotion, check=True, timeout=600)
    set_state(proj, "ready")
    console.print(f"[green]Video: {out}[/green]")

@app.command()
def hookscore(file: Path):
    import subprocess, sys
    subprocess.run([sys.executable, str(ROOT / "tools/ig/hookscore.py"), str(file)], check=False)

@app.command()
def beats(file: Path, target: int = typer.Option(30, help="duracion objetivo s")):
    import subprocess, sys
    subprocess.run([sys.executable, str(ROOT / "tools/ig/beats.py"), str(file), "--target", str(target)], check=False)

@app.command()
def sfx(project: Path):
    from reels.stages.sfx import generate_all
    d = project / "assets" / "sfx"
    generate_all(d)
    console.print(f"SFX generados en {d}")

@app.command()
def hf_build(project: Path, render: bool = typer.Option(False, "--render")):
    """Genera la composicion HyperFrames (HTML + GSAP + audio) desde scenes.json."""
    from reels.stages.hyperframes import build
    scenes = json.loads((project / "scenes.json").read_text())
    out = project / "hyperframes"
    out.mkdir(exist_ok=True)
    build(scenes, out / "index.html")
    console.print(f"HyperFrames: {out/'index.html'}")
    if render:
        hf_render(out, ROOT / "output" / f"{project.name}.mp4")

@app.command()
def hf_render(dir: Path, out: Path = typer.Option(None, "--out", help="MP4 de salida")):
    """Renderiza un proyecto HyperFrames (HTML -> MP4)."""
    import subprocess
    out = out or ROOT / "output" / f"{dir.resolve().parent.name}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["npx", "--yes", "hyperframes@0.8.222", "render", "-o", str(out.resolve())]
    console.print(" ".join(cmd))
    subprocess.run(cmd, cwd=dir, check=True)
    # Normaliza a -15 LUFS en dos pasadas + limitador (evita picos inter-muestra).
    probe = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(out), "-af",
         "loudnorm=I=-15:TP=-3:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    m = json.loads(probe[probe.rfind("{"):probe.rfind("}") + 1])
    af = (f"loudnorm=I=-15:TP=-3:LRA=11:measured_I={m['input_i']}:"
          f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
          f"alimiter=limit=0.5:level=false")
    norm = out.with_name(out.stem + ".norm" + out.suffix)
    subprocess.run(["ffmpeg", "-y", "-i", str(out), "-c:v", "copy",
                    "-af", af, "-ar", "48000", str(norm)],
                   check=True, capture_output=True)
    norm.replace(out)
    console.print(f"[green]Video: {out}[/green]")

@app.command()
def qa(file: Path):
    """Valida formato, duracion, audio y loudness de un MP4."""
    from reels.stages.qa import check
    problems, info = check(file)
    console.print(info)
    if problems:
        for p in problems:
            console.print(f"[red]✗ {p}[/red]")
        raise typer.Exit(1)
    console.print("[green]✓ QA OK[/green]")

@app.command()
def status(project: Path):
    console.print((project / "project.json").read_text())

if __name__ == "__main__":
    app()