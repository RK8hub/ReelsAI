# Pipeline automatizada para producir Reels explicativos con IA

> Documento de intención, investigación inicial y plan técnico.  
> Estado: propuesta para prototipo.  
> Objetivo: producir videos verticales originales, narrados y animados, con un flujo híbrido de agentes premium, modelos económicos/gratuitos y herramientas deterministas.

## 1. Resumen ejecutivo

Construir una línea de producción audiovisual asistida por agentes para crear Reels/Shorts explicativos de 30–90 segundos. El estilo principal será **motion graphics y animación vectorial programática**, no la generación de cada fotograma mediante un modelo de video.

El sistema recibirá un tema, preparará un guion con fuentes, lo dividirá en escenas, generará o reutilizará audio, creará una composición animada mediante plantillas, renderizará MP4 y ejecutará controles automáticos de calidad. El resultado pasará por revisión humana antes de publicarse.

La idea central de costes es:

1. **Claude Pro / Claude Code**: arquitectura, implementación inicial, skills, debugging difícil y revisiones complejas.
2. **GPT**: revisión editorial o razonamiento puntual cuando realmente aporte valor. La suscripción de ChatGPT y la API son productos/facturación distintos; no asumir que una incluye la otra.
3. **OpenCode + OpenRouter**: agente y acceso a modelos económicos/gratuitos para tareas secundarias. OpenCode es el agente; OpenRouter es un proveedor/enrutador de modelos.
4. **Código convencional**: extracción, normalización, conversiones, subtítulos, validaciones, ensamblaje y renderizado deben ejecutarse con Python/Node/FFmpeg cuando sean tareas deterministas.
5. **TTS local o API**: voz sintética. Comenzar con un motor local o de bajo coste; cambiar a un proveedor premium solo si la calidad lo justifica.
6. **Revisión humana**: controlar exactitud factual, ritmo, legibilidad, calidad visual, licencias y derechos de uso.

No se fija una cuota garantizada de videos por mes: dependerá de los límites de las suscripciones, duración, complejidad, regeneraciones y hardware.

---

## 2. Objetivos y límites del primer prototipo

### Objetivos

- Crear un Reel vertical 9:16, inicialmente de 30–60 segundos.
- Producir guion, voz, escenas, subtítulos y MP4 desde un tema de entrada.
- Utilizar plantillas y componentes reutilizables para mantener una identidad visual consistente.
- Guardar los datos de cada producción y poder reanudar trabajos fallidos.
- Mantener los modelos premium fuera del camino crítico de cada video cuando sea posible.
- Registrar el coste aproximado, duración de cada etapa, errores y número de regeneraciones.
- Poder sustituir modelos/proveedores sin rehacer el pipeline completo.

### Fuera del alcance inicial

- Publicación automática sin revisión.
- Clonación de voces de personas sin autorización.
- Generar todas las escenas con modelos de video generativo.
- Automatizar evasión de límites de plataformas o extracción que infrinja condiciones de uso.
- Prometer monetización en Instagram: el acceso a herramientas de monetización depende del país, cuenta y reglas vigentes.

---

## 3. Arquitectura propuesta

```text
Entrada: tema + audiencia + tono + duración objetivo
                      |
                      v
           Orquestador (Python/CLI)
                      |
        +-------------+--------------+
        |                            |
        v                            v
 Investigación y fuentes       Configuración de marca
        |                            |
        v                            |
 Guion estructurado (JSON) <----------+
        |
        v
 Validación del guion y de las fuentes
        |
        v
 Plan de escenas (scene plan JSON)
        |
        +-------------------+
        |                   |
        v                   v
   Voz TTS              Recursos visuales
        |                SVG/iconos/gráficas/
        |                imágenes autorizadas
        +---------+---------+
                  |
                  v
       Remotion / React / SVG
                  |
                  v
       Render MP4 + audio/subtítulos
                  |
                  v
      QA automático + revisión humana
                  |
          aprobado / corregir
                  |
                  v
       Exportación y publicación manual
```

### Agentes y herramientas

- **Claude Code**: implementar la arquitectura, crear componentes, escribir pruebas, depurar errores difíciles y mantener el proyecto.
- **GPT**: revisor opcional para guiones, razonamiento complejo o una segunda opinión. Usar API solo si el coste está justificado.
- **OpenCode**: agente alternativo para tareas de código y ejecución de herramientas.
- **OpenRouter**: acceso a modelos por API; seleccionar modelos concretos por tarea y permitir fallback. Los modelos gratuitos cambian y tienen límites.
- **Python**: orquestación, schemas, validaciones, extracción y utilidades.
- **Node.js + Remotion**: composiciones animadas, timeline, texto, gráficos y render.
- **FFmpeg**: conversión, normalización de audio, muxing, recorte y controles de medios.
- **TTS**: inicialmente local si la calidad/idioma es suficiente; proveedor externo como alternativa.
- **Almacenamiento**: estructura de carpetas local al principio; base de datos solo cuando haya necesidad real de colas, métricas o varios usuarios.

### Principio de escalamiento

1. Intentar primero una función determinista.
2. Si la tarea requiere interpretación, llamar a un modelo económico/gratuito.
3. Validar su respuesta con un schema y reglas.
4. Reintentar una vez o usar un segundo modelo si la validación falla.
5. Escalar a Claude/GPT solo en tareas complejas o fallos persistentes.
6. Guardar resultados para evitar llamadas repetidas.

Los modelos no deben controlar comandos arbitrarios ni ejecutar acciones externas sin permisos. El pipeline debe tratar el contenido recuperado de páginas como datos no confiables, no como instrucciones.

---

## 4. Pipeline de producción por etapas

### Etapa 0 — Brief del video

Entrada mínima:

```json
{
  "topic": "Por qué el cielo se ve azul",
  "audience": "público general",
  "language": "es",
  "tone": "curioso y claro",
  "target_duration_seconds": 50,
  "aspect_ratio": "9:16",
  "brand_profile": "default"
}
```

Validar que haya tema, idioma, duración y formato. Guardar el brief en el directorio del proyecto.

### Etapa 1 — Investigación y fuentes

- Buscar fuentes fiables y registrar URL, título, fecha de consulta y afirmaciones respaldadas.
- Separar hechos comprobados de analogías, opiniones y recursos narrativos.
- Evitar presentar la salida de un LLM como fuente primaria.
- Para temas científicos, médicos, legales o financieros, exigir revisión de fuentes y revisión humana adicional.
- Respetar términos de servicio, robots/limitaciones técnicas, copyright y derechos sobre imágenes.

Salida: `research.json` y una lista de fuentes legibles.

### Etapa 2 — Guion

Generar un guion breve con:
- Hook inicial.
- Una idea principal.
- Explicación en secuencia lógica.
- Ejemplo visual o analogía.
- Cierre y, si procede, llamada a la acción.
- Fuentes enlazadas para las afirmaciones factuales.

El guion debe ajustarse a la duración por ritmo de habla estimado, no solo por número de palabras. El guion final se aprueba antes de producir activos costosos.

### Etapa 3 — Guion estructurado / plan de escenas

Convertir el guion en JSON validado, con escenas y tiempos aproximados. Ejemplo de estructura:

```json
{
  "title": "Por qué el cielo es azul",
  "language": "es",
  "scenes": [
    {
      "id": "scene_01",
      "narration": "Mira el cielo en un día despejado...",
      "visual_type": "title_card",
      "visual_prompt": "Sol, atmósfera y cielo en estilo vectorial limpio",
      "duration_hint_seconds": 5,
      "on_screen_text": "¿Por qué es azul?"
    }
  ]
}
```

El sistema debe rechazar JSON mal formado, escenas sin narración, duración negativa, textos demasiado largos o tipos visuales no admitidos.

### Etapa 4 — Audio

- Generar voz desde el guion aprobado.
- Si el proveedor permite timestamps o alineación, conservarlos.
- Si no, obtener duración por escena y alinear subtítulos mediante herramienta de transcripción/alineación.
- Normalizar volumen y comprobar que el audio no esté vacío, saturado o truncado.
- Música opcional, a volumen bajo y con licencia adecuada.

No clonar voces sin consentimiento y no usar música o activos de terceros sin derechos comerciales apropiados.

### Etapa 5 — Visuales

Prioridad:
1. Componentes vectoriales reutilizables.
2. Diagramas, iconos y gráficos creados desde datos.
3. Imágenes propias o con licencia compatible.
4. Generación de imágenes solo cuando el recurso añada valor.
5. Clips generativos de video como opción excepcional, debido a su coste y variabilidad.

Crear un pequeño sistema de diseño: paleta, tipografías, márgenes seguros, tamaños de texto, estilos de iconos, animaciones de entrada/salida y reglas para el área de interfaz de Instagram.

### Etapa 6 — Render

- Renderizar con Remotion en resolución vertical (por ejemplo, 1080×1920).
- Componer narración, música, subtítulos y escenas.
- Usar FFmpeg para normalizar, inspeccionar y convertir el resultado cuando sea necesario.
- Guardar un render de baja resolución para revisión rápida antes del render final.

### Etapa 7 — Control de calidad

Controles automáticos mínimos:
- Archivo MP4 existe y se puede decodificar.
- Resolución y relación de aspecto correctas.
- Duración dentro de tolerancia.
- Audio presente y duración coherente con el video.
- Subtítulos no vacíos y sin desbordes de pantalla.
- No hay escenas negras o vacías por encima de un umbral.
- Fuentes y activos usados registrados.
- El render no contiene marcadores, rutas locales ni texto de depuración.

Control humano:
- Exactitud del guion y de los datos.
- Voz natural y pronunciación de nombres.
- Ritmo, legibilidad y contraste.
- Coherencia visual y ausencia de artefactos.
- Cumplimiento de derechos, licencias y reglas de plataforma.

### Etapa 8 — Exportación y registro

Guardar cada proyecto en un directorio independiente con:
- `brief.json`
- `research.json`
- `script.md`
- `scenes.json`
- `project.json`
- `assets/`
- `audio/`
- `renders/preview.mp4`
- `renders/final.mp4`
- `qa-report.json`
- `cost-report.json`
- `sources.md`

No publicar automáticamente al inicio. Primero acumular una muestra de videos revisados y medir calidad y tiempo real.

---

## 5. Repositorios y proyectos de referencia

Los siguientes proyectos son puntos de partida y referencias de implementación. “Popular” se usa aquí en el sentido de adopción visible, estrellas/actividad de GitHub o relevancia del ecosistema; los números cambian. Revisar siempre README, licencia, dependencias y commits antes de instalar.

### A. Motor de video y skills

1. **Remotion — crear videos mediante React**
   - Repo: https://github.com/remotion-dev/remotion
   - Web: https://www.remotion.dev/
   - Uso: escenas programáticas, animaciones, audio, subtítulos, composición y render en lote.
   - Por qué importa: permite convertir datos/JSON en videos consistentes y reutilizables.
   - Advertencia: revisar la licencia actual; Remotion tiene condiciones comerciales específicas para ciertos usos empresariales.

2. **Remotion Agent Skills — skills oficiales**
   - Repo: https://github.com/remotion-dev/skills
   - Uso: buenas prácticas para que agentes como Claude Code, Codex, Kimi Code o Cursor creen composiciones, rendericen, trabajen con captions y consulten la documentación.
   - Instalación documentada por el proyecto: `npx skills add remotion-dev/skills`
   - Recomendación: empezar por `remotion-best-practices`, `remotion-create`, `remotion-captions` y `remotion-render`.

3. **Claude Code Video Toolkit**
   - Repo: https://github.com/digitalsamba/claude-code-video-toolkit
   - Uso: workspace de producción con skills, comandos, componentes, transiciones, perfiles de marca, plantillas y ciclo de vida por proyecto.
   - Su README documenta un flujo de guion → activos → revisión de escenas → audio → preview → render → publicación.
   - Incluye ejemplos de videos explicativos verticales, demos de producto y generación de voz/activos. Los costes anunciados por el autor son estimaciones de su configuración, no garantías universales.
   - Es probablemente la referencia más cercana a la idea de una “fábrica de videos” gestionada por un agente.

4. **Awesome Agent Video Skills**
   - Repo: https://github.com/clonn/awesome-agent-video-skills
   - Uso: catálogo para descubrir skills, plugins, MCP servers y toolkits relacionados con creación y edición de video mediante agentes.
   - Recomendación: usarlo para explorar opciones, no instalar todas las herramientas a la vez. Verificar licencias y seguridad de cada repositorio.

5. **Manim Community Edition**
   - Repo: https://github.com/ManimCommunity/manim
   - Uso: animaciones matemáticas y científicas precisas mediante código.
   - Conviene si el canal se centra en matemáticas, física o diagramas explicativos; para motion graphics generalistas, Remotion suele integrarse mejor con HTML/React y texto de redes sociales.

### B. Modelos, agentes y procesamiento

6. **OpenCode**
   - Repo: https://github.com/anomalyco/opencode
   - Web: https://opencode.ai/
   - Uso: agente de código que puede trabajar con distintos proveedores/modelos.
   - Papel en esta arquitectura: ejecutar tareas de desarrollo o mantenimiento con un modelo económico. No reemplaza el motor de video.

7. **OpenRouter — catálogo de modelos**
   - Web: https://openrouter.ai/models
   - Modelos gratuitos: https://openrouter.ai/collections/free-models
   - Uso: un endpoint para acceder a modelos de distintos proveedores.
   - Advertencia: disponibilidad, calidad, privacidad y límites varían por modelo/proveedor. Los modelos gratuitos tienen restricciones y pueden cambiar; no usarlos como dependencia crítica sin fallback.

8. **FFmpeg**
   - Repo: https://github.com/FFmpeg/FFmpeg
   - Web: https://ffmpeg.org/
   - Uso: conversión, corte, mezcla, normalización, extracción de metadatos y codificación final.
   - Recomendación: usarlo como herramienta determinista, no pedirle a un LLM que realice operaciones que ya están resueltas por comandos reproducibles.

9. **MoviePy**
   - Repo: https://github.com/Zulko/moviepy
   - Uso: composición de video desde Python y automatización de clips.
   - Puede ser útil si el equipo prefiere Python, aunque no conviene mantener dos motores de composición en el MVP sin necesidad clara.

10. **Qwen3-TTS**
    - Repositorio/modelo: https://github.com/QwenLM/Qwen3-TTS
    - Uso: generación de voz; comprobar compatibilidad de hardware, idiomas, licencia y modo de despliegue antes de elegirlo.
    - Alternativa: seleccionar un proveedor TTS comercial si la naturalidad en español o la latencia local no son suficientes.

### C. Ejemplos de producción documentados

11. **Showcase oficial de Remotion**
    - https://www.remotion.dev/showcase
    - Muestra casos como videos meteorológicos generados desde datos, campañas de video personalizado, demos de producto y videos instructivos generados programáticamente.
    - Valor de referencia: prueba que el enfoque de composición mediante código se utiliza para aplicaciones y campañas reales, no solo para experimentos.

12. **Ejemplos del Claude Code Video Toolkit**
    - https://github.com/digitalsamba/claude-code-video-toolkit
    - El README incluye ejemplos del propio proyecto, como un explicador vertical “Why is the sky blue?”, videos de lanzamiento y demos de producto. Son demos del autor del repositorio, no una auditoría independiente de sus resultados ni una garantía de coste.

---

## 6. ¿Cómo se construyen estos sistemas en la práctica?

Los sistemas fiables no suelen ser un único prompt enorme. Separan el proceso en archivos, fases y contratos de datos.

### Patrón recomendado

- **Skills**: instrucciones reutilizables para que el agente siga un procedimiento de guion, composición, subtítulos o render.
- **MCP**: conecta el agente a herramientas externas cuando se necesita acceso a funciones/datos estructurados.
- **Comandos/CLI**: operaciones reproducibles que se pueden probar sin conversación.
- **Plantillas**: estructuras visuales que reciben contenido como datos.
- **Proyecto por video**: archivos de estado para retomar la tarea después de una interrupción.
- **Schemas**: contratos JSON para que una etapa no dependa de texto libre impredecible.
- **Validadores**: pruebas para rechazar resultados incorrectos antes de avanzar.
- **Logs y métricas**: registrar errores, duración, coste y regeneraciones.

El toolkit de Digital Samba documenta un ciclo de proyecto con estados como `planning`, `assets`, `review`, `audio`, `editing`, `rendering` y `complete`, además de un `project.json` que registra escenas, audio, sesiones y fase. Es un patrón útil para reanudar trabajos en distintas sesiones.

### Recomendación de diseño

No empezar construyendo un sistema multiagente complejo. Primero crear un único pipeline reproducible que produzca un video de calidad. Después añadir un agente separado solo cuando haya una razón medible: por ejemplo, revisión de fuentes, selección de activos o QA visual.

---

## 7. Gestión de coste y límites

Mantener métricas por video:
- llamadas a Claude/GPT/modelos de OpenRouter;
- tokens estimados cuando estén disponibles;
- coste de TTS, imágenes, música y GPU;
- tiempo de render;
- cantidad de reintentos;
- proporción de videos aprobados a la primera.

Política de coste:
- no llamar al LLM para conversiones mecánicas;
- reutilizar assets y plantillas;
- cachear resultados de investigación y generación;
- no regenerar voz si solo cambió un elemento visual;
- no regenerar todo el video si solo falla una escena;
- fijar un presupuesto máximo por proyecto;
- registrar la licencia y condiciones comerciales de cada servicio.

Los precios y límites de servicios cambian. Antes de estimar capacidad mensual, hacer una prueba con 5–10 videos y medir el coste real de extremo a extremo.

---

## 8. Licencias, seguridad y publicación

Antes de usar un repositorio o modelo:
- leer la licencia del código y de los pesos/modelos;
- confirmar que el uso comercial está permitido;
- revisar atribución, restricciones de redistribución y términos de las APIs;
- no asumir que “open source” significa que todos los activos generados pueden usarse sin condiciones;
- no enviar secretos/API keys a prompts ni subir `.env` a Git;
- ejecutar scripts y MCP servers de terceros en un entorno controlado;
- revisar permisos y comandos antes de instalar herramientas de agentes.

Para publicar:
- confirmar derechos de música, imágenes, voces y marcas;
- comprobar las reglas vigentes de Instagram para contenido sintético, originalidad y monetización;
- etiquetar contenido de IA cuando la plataforma lo exija;
- evitar contenido engañoso presentado como noticia o hecho real;
- mantener una revisión humana antes de subirlo.

---

## 9. Plan de implementación

### Fase 1 — Prueba de concepto
- Instalar Remotion y sus Agent Skills oficiales.
- Crear una plantilla vertical con hook, tres escenas explicativas, subtítulos y cierre.
- Usar un guion fijo de prueba.
- Renderizar sin API externa y comprobar calidad visual.

**Criterio de salida:** un MP4 vertical reproducible a partir de un JSON.

### Fase 2 — Audio y escenas
- Integrar TTS.
- Dividir el guion por escenas.
- Alinear subtítulos y duración.
- Añadir componentes SVG reutilizables.

**Criterio de salida:** un Reel narrado con timing razonable y texto legible.

### Fase 3 — Orquestación híbrida
- Crear un CLI en Python que gestione fases y estado.
- Añadir un proveedor de modelo económico vía OpenRouter.
- Configurar validación JSON y reintentos.
- Reservar Claude/GPT para fallos o tareas de mayor dificultad.

**Criterio de salida:** el flujo puede procesar un tema nuevo sin editar manualmente el código de composición.

### Fase 4 — Calidad y métricas
- QA de audio, video, subtítulos, duración y fuentes.
- Registrar coste y duración de cada etapa.
- Añadir preview de baja resolución.
- Revisión humana antes del render final.

**Criterio de salida:** informe de QA por cada video y coste medible.

### Fase 5 — Lotes pequeños
- Producir 5–10 videos de un mismo nicho.
- Medir cuánto tarda cada uno, cuántos requieren corrección y cuáles resultan visualmente repetitivos.
- Mejorar la plantilla antes de aumentar volumen.

**Criterio de salida:** pipeline estable y un coste real por video documentado.

---

## 10. Decisiones pendientes

- Nicho editorial y audiencia.
- Duración objetivo y frecuencia de publicación.
- Estilo gráfico: vectorial, personajes, mapas, diagramas o combinación.
- TTS: motor local frente a API.
- Si la máquina local puede renderizar a una velocidad aceptable.
- Política de fuentes y revisión factual.
- Qué etapas necesitan realmente agentes.
- Si se publicará manualmente o se integrará más adelante una herramienta de publicación.

## 11. Fuentes principales

- Remotion: https://github.com/remotion-dev/remotion
- Remotion Agent Skills: https://github.com/remotion-dev/skills
- Remotion Showcase: https://www.remotion.dev/showcase
- Claude Code Video Toolkit: https://github.com/digitalsamba/claude-code-video-toolkit
- Awesome Agent Video Skills: https://github.com/clonn/awesome-agent-video-skills
- Manim Community: https://github.com/ManimCommunity/manim
- OpenCode: https://github.com/anomalyco/opencode
- OpenRouter Free Models: https://openrouter.ai/collections/free-models
- FFmpeg: https://github.com/FFmpeg/FFmpeg
- MoviePy: https://github.com/Zulko/moviepy
- Qwen3-TTS: https://github.com/QwenLM/Qwen3-TTS

### Nota de investigación

Esta es una propuesta técnica basada en la documentación pública de los proyectos enlazados. Los showcases y costes publicados por los autores sirven como ejemplos de implementación, pero no son una auditoría independiente. Verificar los repositorios, licencias, versiones y límites vigentes antes de usarlos en producción.
