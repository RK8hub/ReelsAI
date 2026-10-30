# Informe de estado — reels-factory

**Fecha:** 2026-10-30
**Commit actual:** `dd912e1`
**Estado:** MVP funcional, sin integraciones de IA de pago todavía.

---

## 1. Resumen ejecutivo

El proyecto ya produce un Reel vertical completo y verificable:

- Guion → escenas → HTML animado → MP4 con música y SFX reales.
- Formato **1080×1920, 30 fps, H.264 + AAC 48 kHz estéreo**.
- Render de referencia: `output/2026-10-30_ia-y-vulnerabilidades-v2.mp4` (48 s).
- QA técnico medido: **-16.1 LUFS**, true peak **-4.1 dBTP**, sin clipping.
- Tests: **4 passed**.

Lo que **no** existe aún: planificador con LLM, narración TTS, subtítulos,
imágenes/clips generados y cualquier llamada a APIs de pago. El modo de pago
está diseñado en este informe, no implementado.

---

## 2. Cómo funciona

### 2.1 Flujo actual

```
guion (.txt/.md)
   │
   ▼
reels new  ──────────────►  projects/<id>/scenes.json   (plan_simple, determinista)
   │
   ▼
reels hf-build ──────────►  projects/<id>/hyperframes/index.html + assets/
   │
   ▼
reels hf-render ─────────►  HyperFrames (Chrome headless + FFmpeg)
   │                         └─ loudnorm 2 pasadas + limitador
   ▼
output/<id>.mp4
   │
   ▼
reels qa output/<id>.mp4  (formato, duración, audio, loudness)
```

### 2.2 Comandos disponibles

| Comando | Qué hace |
|---|---|
| `reels new` | Crea `projects/<id>/` y genera `scenes.json` con el planificador determinista. |
| `reels hf-build <project>` | Genera la composición HyperFrames (HTML + GSAP + audio). |
| `reels hf-build <project> --render` | Genera y renderiza todo en uno. |
| `reels hf-render <dir> --out <mp4>` | Renderiza HTML → MP4 y normaliza audio. |
| `reels qa <mp4>` | Valida resolución, duración, pista de audio y loudness. |
| `reels status <project>` | Muestra `project.json`. |
| `reels hookscore <txt>` | Score de hook (script de `instagram-agent-skill`). |
| `reels beats <txt>` | Análisis de beats/ritmo. |
| `reels sfx <project>` | Generador legado de SFX sintéticos (WAV). Ya no es el camino principal. |
| `reels render <project>` | Motor alternativo Remotion (no es el principal). |

### 2.3 Módulos

| Archivo | Responsabilidad |
|---|---|
| `src/reels/cli.py` | CLI Typer, orquesta build/render/QA. |
| `src/reels/schemas.py` | `Brief`, `Scene`, `ScenesPlan`; valida duración, solapes y textos ≤ 7 palabras. |
| `src/reels/state.py` | Crea `projects/<id>/` y actualiza `project.json`. |
| `src/reels/stages/plan_simple.py` | Guion → escenas. Ritmo 2.7 palabras/s; `visual_type` por palabras clave. |
| `src/reels/stages/hyperframes.py` | Generador HTML: paletas, visuales 2D, timeline GSAP, música y SFX por escena. |
| `src/reels/stages/qa.py` | `ffprobe` + `loudnorm` para QA técnico. |
| `src/reels/stages/sfx.py` | SFX sintéticos de respaldo (stdlib). |
| `src/reels/safezone.py` | Zonas seguras 1080×1920 portadas de `reels-af`. |
| `src/reels/providers/` | **Vacío**: reservado para LLM/TTS/imágenes de pago. |
| `tools/ig/` | `hookscore`, `beats`, `caption`, `humanize`, `detect` (copiados de `instagram-agent-skill`). |
| `assets/music/bed.mp3` | Cama musical (Mixkit Free License). |
| `assets/sfx/*.ogg` | SFX reales CC0 de `romainsimon/uisfx`. |
| `remotion/` | Motor alternativo; composición `Reel`. |

### 2.4 Cómo se construye el video

`hyperframes.py` emite un `index.html` con:

- `<div id="root" data-duration="...">` y una `<section class="scene clip">` por escena.
- Visuales según `visual_type`: `hook_title`, `kinetic_text`, `stat_counter`,
  `icon_grid`, `list_reveal`, `diagram_flow`, `character`, `environment`,
  `timeline`, `cta_end`.
- Timeline GSAP **pausada** registrada en `window.__timelines["main"]`, para que
  HyperFrames pueda hacer *seek* frame a frame de forma determinista.
- Audio: `<audio id="music" ...>` + un `<audio>` por SFX, con `data-start`,
  `data-duration`, `data-track-index` y `data-volume`.
- Barra de progreso y flashes de transición.

`hf-render` ejecuta HyperFrames, luego normaliza con FFmpeg en dos pasadas
(`loudnorm` + `alimiter`) y deja el MP4 en `output/`.

---

## 3. Estado actual (implementado)

- [x] Pipeline vertical 1080×1920@30fps.
- [x] Generador HyperFrames con 10 tipos de visuales 2D.
- [x] Animaciones GSAP seekables (entradas, contadores, stagger, timeline, progreso).
- [x] Música + SFX reales por escena.
- [x] Normalización de audio a rango social.
- [x] QA técnico (`reels qa`).
- [x] Tests del generador y del QA.
- [x] README, `.gitignore` y commits.
- [x] Ruta de salida única: `output/<id>.mp4`.

---

## 4. Limitaciones y pendientes

### 4.1 Contenido
- El planificador es **determinista y por palabras clave**: puede elegir un
  visual que no corresponde y corta el texto en pantalla a 7 palabras.
- Las escenas duran lo que dicta el ritmo de lectura (2.7 palabras/s), no una
  narración real.
- No hay narración (voz), subtítulos ni sincronización voz/imagen.
- Los SFX se asignan por tipo de escena, no por acción concreta en pantalla.

### 4.2 Técnico
- `src/reels/providers/` está vacío.
- El motor Remotion quedó como alternativo y sin mantenimiento activo.
- `reels sfx` genera tonos sintéticos; el camino real usa `assets/sfx/`.
- No hay CI ni tests de render completo (los tests usan fixtures cortos).
- No hay portada/thumbnail, ni export multi-formato (solo MP4 vertical).

### 4.3 Prioridad sugerida

| Prioridad | Tarea | Impacto | Esfuerzo |
|---|---|---|---|
| P0 | Planificador con Claude + validación pydantic | Escenas y visuales coherentes | 1-2 días |
| P0 | TTS con ElevenLabs + duración real de escenas | Voz y ritmo reales | 1-2 días |
| P1 | Subtítulos sincronizados | Retención y accesibilidad | 1 día |
| P1 | Ducking de música bajo voz | Calidad de audio | 0.5 día |
| P2 | Imágenes generadas para `image_pan_zoom` | Riqueza visual | 1-2 días |
| P2 | CI con tests + QA del render final | Robustez | 0.5 día |
| P3 | HeyGen (avatar/clips) y música generada | Producción premium | 2-4 días |

---

## 5. Cómo implementar el modo de pago

### 5.1 Principios

1. **Nada de claves en el repo.** Variables de entorno + `.env` ignorado por git.
2. **Capa de proveedores** para no acoplar el pipeline a una marca.
3. **Caché por hash** de prompt/texto para no pagar dos veces lo mismo.
4. **Presupuesto duro** por proyecto (`Brief.budget_usd_max`, hoy 2.0 USD).
5. **Fallback local**: si no hay clave o falla la API, seguir con el modo actual.
6. **Determinismo en render**: los assets pagados se generan antes y se guardan;
   el render nunca llama a una API.

### 5.2 Estructura propuesta

```
src/reels/providers/
  __init__.py
  base.py          # Protocols: LLMProvider, TTSProvider, ImageProvider
  factory.py       # get_provider(name) según env/config
  anthropic.py     # Claude: guion + plan de escenas
  elevenlabs.py    # TTS por escena + timestamps
  openai.py        # imágenes (opcional)
  heygen.py        # avatar/clips (opcional)
src/reels/stages/
  plan_llm.py      # reemplaza plan_simple cuando hay proveedor
  voice.py         # TTS + reflow de duraciones
  captions.py      # subtítulos desde timestamps
  assets.py        # imágenes/clips generados
```

Configuración recomendada (`config/providers.yaml`, sin secretos):

```yaml
llm:
  provider: anthropic
  model: claude-sonnet-latest   # fijar versión exacta al implementar
  max_usd: 0.30
tts:
  provider: elevenlabs
  voice_id: ${ELEVENLABS_VOICE_ID}
  model: eleven_multilingual_v2
  max_usd: 0.50
images:
  provider: none                # openai | none
  max_images: 4
  max_usd: 0.40
```

Variables de entorno:

```bash
ANTHROPIC_API_KEY=...
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...
OPENAI_API_KEY=...        # solo si se usan imágenes
```

### 5.3 Claude para guion y plan de escenas

**Objetivo:** convertir un brief + guion en un `ScenesPlan` válido, con visuales
coherentes, en lugar del matching por palabras clave.

**Implementación:**
1. `providers/anthropic.py` con el SDK oficial (`anthropic`).
2. Forzar salida estructurada con *tool use* / JSON schema y validar con
   `ScenesPlan.model_validate`.
3. Si la validación falla, reintentar incluyendo el error (máx. 2).
4. Guardar el resultado en `scenes.json` y registrar tokens/costo en
   `project.json`.
5. Fallback a `plan_simple` si no hay clave o se agota el presupuesto.

Esquema conceptual del prompt:

- Sistema: director de Reels verticales; reglas de 7 palabras, duración,
  tipos de visual permitidos, zonas seguras, tono.
- Usuario: brief, guion, score de hook, idioma y CTA.
- Salida: JSON `ScenesPlan` (mismo esquema que ya valida pydantic).

CLI propuesto:

```bash
reels new --topic "..." --script guion.txt --planner claude --budget 0.50
```

Costo orientativo: un reel típico gasta pocos miles de tokens de entrada y
~1-2k de salida; suele ser **centavos por reel**. Verificar precios vigentes.

### 5.4 ElevenLabs para narración

**Objetivo:** una voz por escena, con duración real que mande sobre el montaje.

**Implementación:**
1. `providers/elevenlabs.py`: POST a `/v1/text-to-speech/{voice_id}` con
   `httpx`, guardando `assets/voice/scene_XX.mp3`.
2. Medir cada MP3 con `ffprobe` y **reflow** de `start`/`end` de las escenas.
3. `hyperframes.py` añade un `<audio>` de voz por escena en una pista propia
   (`data-track-index="5"`), volumen 1.
4. Bajar la música a ~0.14–0.2 y aplicar *ducking* con `data-automation`
   (lane de volumen) o simplemente un volumen bajo constante al principio.
5. Subtítulos: usar los timestamps de ElevenLabs (o Whisper) y renderizar una
   capa de captions con GSAP.

CLI propuesto:

```bash
reels voice projects/<id> --provider elevenlabs --voice "$ELEVENLABS_VOICE_ID"
reels hf-build projects/<id> --voice
```

Costo orientativo: se cobra por caracteres; un reel de 45-60 s suele quedar en
**centavos**. Verificar el precio del plan contratado.

### 5.5 Imágenes y clips de pago (opcional)

- `image_pan_zoom` y fondos: OpenAI Images / Flux / Ideogram.
- Guardar en `assets/generated/<hash>.png`, con seed fijo y caché.
- Insertar `<img class="clip" data-start ...>` y animar pan/zoom con GSAP.
- HeyGen: avatar o clips generados; el repo ya trae la skill de HyperFrames
  (`/media-use`) para integrarlo.
- Límite duro: `max_images` y `max_usd` por reel.

### 5.6 Música de pago (opcional)

Se puede mantener Mixkit (gratis) o integrar ElevenLabs Music / Suno.
Recomendación: no pagar música hasta que la voz y el guion estén resueltos.

### 5.7 Control de costos y seguridad

- `project.json` con ledger: `{provider, operacion, tokens/chars, usd_estimado}`.
- `--dry-run` que muestra el costo estimado sin llamar a la API.
- Caché `cache/<sha256>.json|mp3|png`.
- Reintentos con backoff solo en errores 429/5xx.
- Nunca loggear claves; redactar headers.
- Añadir `.env` y `cache/` al `.gitignore`.

### 5.8 Flujo final propuesto

```bash
reels run \
  --topic "IA y vulnerabilidades" \
  --script guion.txt \
  --planner claude \
  --voice elevenlabs \
  --budget 1.00
# → plan → voz → assets → hf-build → render → qa
```

---

## 6. Cambios de datos necesarios

- `Scene`: añadir `voice_file`, `caption_words`, `asset_files`.
- `ScenesPlan`: permitir duraciones derivadas de la voz (reflow).
- `project.json`: añadir `costs` y `providers_used`.
- `Brief`: ya tiene `voice_provider`, `draft_voice_provider`, `voice_profile`
  y `budget_usd_max`; solo falta conectarlos.

---

## 7. Roadmap

| Fase | Entrega |
|---|---|
| 2 | `plan_llm` con Claude + validación + fallback + caché. |
| 3 | `voice` con ElevenLabs + reflow + subtítulos + ducking. |
| 4 | Imágenes generadas y clips opcionales (OpenAI/HeyGen). |
| 5 | CI, ledger de costos, `reels run` y documentación de operación. |

---

## 8. Riesgos

- **Precios y modelos cambian**: fijar versiones y revisar tarifas oficiales.
- **Licencias**: Remotion tiene condiciones comerciales; Mixkit requiere
  revisar términos para monetización; SFX son CC0.
- **Voz clonada**: requiere consentimiento y cumplimiento de la plataforma.
- **Determinismo**: si se generan assets, hacerlo antes del render y cachear.
- **Privacidad**: no enviar datos sensibles a APIs externas sin necesidad.

---

## 9. Conclusión

El proyecto está en un MVP sólido y reproducible: ya hay video vertical con
animación, música, SFX y QA. El siguiente salto de calidad no es más código de
render, sino **conectar proveedores de pago** en este orden:

1. **Claude** para pensar las escenas.
2. **ElevenLabs** para la voz y el ritmo.
3. **Subtítulos** y *ducking*.
4. Imágenes/clips solo cuando 1-3 estén estables.

La carpeta `src/reels/providers/` ya está reservada para eso.
