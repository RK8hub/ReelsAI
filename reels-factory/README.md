# reels-factory

Fábrica semiautomática de Reels/Shorts verticales (**1080×1920, 30 fps**) desde un guion.
Motor principal: **HyperFrames** (HTML + GSAP + audio → MP4 determinista).
Planificador determinista (sin LLM) y comandos auxiliares del pipeline.

## Requisitos
- Python 3.11+, Node.js 22+, FFmpeg/ffprobe.
- Python: `python -m venv .venv && .venv/bin/pip install -e .`
- Remotion (motor alternativo): `cd remotion && npm install`

## Ruta de salida
Todos los videos finales van a:

```
reels-factory/output/<nombre-del-proyecto>.mp4
```

Ejemplo: `output/2026-10-30_ia-y-vulnerabilidades-v2.mp4`.

## Flujo rápido
```bash
# 1. Crear proyecto desde un guion (crea projects/<id>/, local y no versionado)
.venv/bin/reels new --topic "tema" --script guion.txt --duration 48

# 2. Generar la composición HyperFrames (HTML + animaciones + audio)
.venv/bin/reels hf-build projects/<id>

# 3. Renderizar a output/ y normalizar audio a -15 LUFS
.venv/bin/reels hf-render projects/<id>/hyperframes --out output/<id>.mp4

# Todo en uno
.venv/bin/reels hf-build projects/<id> --render

# Preview / estado / QA
.venv/bin/reels status projects/<id>
.venv/bin/reels qa output/<id>.mp4
```

## Qué incluye la composición
- Escenas con fondo degradado, títulos, captions y partículas.
- Visuales 2D por tipo: `hook_title`, `kinetic_text`, `stat_counter`, `icon_grid`,
  `list_reveal`, `diagram_flow`, `character`, `environment`, `timeline`, `cta_end`.
- Animaciones GSAP seekables (entradas, contadores, stagger, progreso, flashes).
- Audio: cama musical + SFX reales por escena (whoosh en cortes, pop al aterrizar,
  impact en el hook, success en el CTA).
- Normalización final con FFmpeg `loudnorm` en dos pasadas + limitador
  (objetivo **-16 a -14 LUFS**, true peak ≤ -1 dBTP).

## Audio y licencias
- Música: Mixkit Free License (`assets/music/bed.mp3`).
- SFX: **CC0 1.0** de [romainsimon/uisfx](https://github.com/romainsimon/uisfx)
  (`assets/sfx/`). Uso comercial permitido.
- Puedes reemplazar `assets/music/bed.mp3` por tu propia pista.

## Estructura
```
assets/music/      cama musical
assets/sfx/        efectos reales (CC0)
src/reels/         CLI, esquemas, planificador
src/reels/stages/  plan_simple.py, sfx.py, hyperframes.py (generador HTML)
projects/<id>/     generado en runtime (scenes.json + HTML + assets), no versionado
output/            MP4 finales
remotion/          motor alternativo (composición Reel)
tools/ig/          hookscore, beats, captions (instagram-agent-skill)
vendor/            repos de referencia clonados localmente (no versionados)
```

## Estado
- Motor HyperFrames integrado y validado: `check` sin errores.
- Generador `hf-build` produce HTML + GSAP + audio desde `scenes.json`.
- Render de ejemplo con audio, animación y SFX: `output/2026-10-30_ia-y-vulnerabilidades-v2.mp4`.
- Remotion queda como motor alternativo.
- Tests: generador HyperFrames (HTML + audio + escenas) y QA de MP4 (formato/audio).

## Pendiente
- TTS/narración (requiere proveedor/API key).
- Más plantillas de personajes/entornos por nicho.
- Integrar los tests existentes en CI (GitHub Actions).

## Informe
Ver [`INFORME.md`](INFORME.md) para el estado completo, pendientes y el diseño
del modo de pago (Claude, ElevenLabs, imágenes).

## Licencia
Por definir. Revisar licencias de Remotion antes de uso comercial.
HyperFrames es Apache-2.0.
