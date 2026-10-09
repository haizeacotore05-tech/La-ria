# La Ría

El diario personal de Haizea: cada mañana, las noticias de Bilbao, Euskadi, España y el mundo, con «Hoy en 5 minutos», breves, mercados, «Sigue la historia» y, los domingos, «La semana en 10 minutos».

- `index.html` — la aplicación (instalable en el móvil, funciona sin conexión).
- `data/editions/AAAA-MM-DD.json` — una edición por día. La sube la tarea diaria.
- `scripts/build_index.py` — genera `data/index.json` y `data/threads.json`. Netlify lo ejecuta en cada despliegue.
- `sw.js`, `manifest.webmanifest`, `icons/` — lo necesario para instalarla como app.
