# Entrada HID vs pygame para SConE

## ¿Por qué abandonar pygame?
`pygame` (SDL) es práctico para prototipos, pero en macOS puede presentar:
- Lecturas inestables: eventos perdidos o estados pegados entre frames.
- Mapeos erróneos: botones reportados con índices inconsistentes (START apareciendo como L, etc.).
- Dificultad para calibración precisa: SDL abstrae el dispositivo y a veces mezcla hats, ejes y botones.

La API HID (Human Interface Device) permite leer directamente los reportes crudos que el controlador envía por USB. Esto da:
- Visibilidad completa del paquete de 32/64 bytes por frame.
- Control fino sobre la detección de cambios (byte y bit exactos).
- Calibración reproducible: el JSON mapea directamente "byte" y "bit".
- Independencia de SDL y sus capas de traducción.

## Conceptos básicos de HID
Un dispositivo HID envía "reportes" periódicos (o al cambiar el estado). Cada reporte es un arreglo de bytes donde:
- Ciertos bytes representan ejes analógicos (0–255 típico). El valor central suele ser ~128.
- Ciertos bits dentro de un byte representan botones digitales (0 = suelto, 1 = presionado).
- Algunos controladores usan un "hat" o POV que codifica direcciones en un nibble o en un byte separado.

En lugar de deducir todo vía eventos, leemos el paquete y detectamos qué se movió.

## Herramientas añadidas
| Archivo | Propósito |
|---------|-----------|
| `examples/x360_hid_reader.py` | Lista dispositivos HID y muestra reportes crudos (hex). |
| `examples/hid_snes_recorder.py` | Calibra, graba y reproduce secuencias usando HID directo y Serial. |

## Instalación de dependencias
```bash
pip install hid pyserial
# macOS
brew install hidapi
```
Si `import hid` falla, asegúrate de que `hidapi` esté instalado con Homebrew.

## Listar y verificar el dispositivo
```bash
python examples/x360_hid_reader.py --list
```
Salida esperada (ejemplo):
```
- Brook Controller vid=0x045e pid=0x028e path=DevSrvsID:4294990992
```
Luego prueba lectura cruda:
```bash
python examples/x360_hid_reader.py --vendor 0x045e --product 0x028e
```
Presiona botones y verifica que los reportes cambian.

## Calibración interactiva (HID)
Genera tu mapeo JSON:
```bash
python examples/hid_snes_recorder.py \
  --calibrate hid_mapping.json \
  --vendor 0x045e --product 0x028e
```
Flujo:
1. Se captura un baseline de reportes.
2. Para cada objetivo (RIGHT, LEFT, UP, DOWN, A, B, X, Y, L, R, SELECT, START):
   - Mantén presionada la dirección/botón indicado.
   - El script identifica el primer byte estable que cambia (y el bit si es digital).
   - Ejes se reconocen si el delta supera el umbral (`AXIS_THRESHOLD`).
3. Se guarda `hid_mapping.json` con secciones:
```json
{
  "digital": [{"name": "A", "byte": 3, "bit": 4}, ...],
  "axes": [{"byte": 1, "center": 128}, {"byte": 2, "center": 128}]
}
```

### Sugerencias de calibración
- Mantén únicamente el botón/dirección solicitada; evita presionar extras.
- Si una dirección se detecta como digital pero es analógica (stick), repite la calibración moviendo suavemente el stick sólo hacia esa dirección.
- Recalibra si tus ejes muestran inversión (LEFT activa RIGHT). Se puede ajustar luego en código añadiendo campos como `invert: true` si es necesario (extensión futura).

## Grabación de secuencia
```bash
python examples/hid_snes_recorder.py \
  --record seq.json \
  --mapping hid_mapping.json \
  --port /dev/cu.usbserial-2120 \
  --vendor 0x045e --product 0x028e
```
- Ejecuta ~60 FPS.
- Envía cada frame como bitmask al puerto Serial usando `SNESControllerSerial`.
- Para detener: mantén START + SELECT (si están mapeados) durante ~0.5s.

## Reproducción
```bash
python examples/hid_snes_recorder.py \
  --play seq.json \
  --mapping hid_mapping.json \
  --port /dev/cu.usbserial-2120
```

## Ventajas claves frente a pygame
- Menos ambigüedad: cada botón mapeado una sola vez (byte/bit exacto).
- Mejor estabilidad temporal: lectura directa evita eventos perdidos.
- Ajustes deterministas: cambiar umbrales o invertir ejes sin depender de capas SDL.

## Limitaciones actuales
- Heurística de ejes simple (`AXIS_THRESHOLD`). Podría ampliarse para soportar rango dinámico y normalización.
- No se detecta hat específico si codifica direcciones como valores discretos (extensión posible: tabla de valores).
- No hay GUI; todo es CLI. Se puede agregar un modo verbose que imprima los bytes cambiados por objetivo.

## Próximas mejoras sugeridas
- `--axis-threshold` configurable.
- `invert` por eje en el mapeo.
- Detección de hat con valores enumerados (ej. 0x0=neutral, 0x1=up...).
- Export a CSV de reportes para análisis offline.

## Solución de problemas
| Problema | Causa común | Acción |
|----------|-------------|--------|
| Botón no se registra | Mapeo equivocado del bit | Recalibra sólo ese botón; edita JSON manualmente. |
| Direcciones invertidas | Eje reporta 255 para izquierda | Agregar futuro campo `invert` o ajustar lógica. |
| Stick muerto (sin cambio) | Delta < umbral | Baja `AXIS_THRESHOLD` en el script. |
| Reportes vacíos | Dispositivo no en modo non-blocking | Verifica versión de `hid` y reinstala. |

## Editar manualmente el mapeo
Puedes abrir `hid_mapping.json` y ajustar:
- `byte`: índice del array de reporte.
- `bit`: de 0 a 7 (si es botón digital).
- `center`: valor central de un eje (normalmente ~128).

Ejemplo para invertir eje horizontal (añadir campo opcional futuro):
```json
{
  "axes": [
    {"byte": 1, "center": 128, "invert": true},
    {"byte": 2, "center": 128}
  ],
  "digital": [ {"name": "A", "byte": 3, "bit": 4} ]
}
```
*(La lógica de `invert` aún no implementada: se puede añadir rápido si lo necesitas.)*

## Conclusión
El enfoque HID brinda precisión y estabilidad para construir secuencias reproducibles en el ESP32/SNES. Recomiendo migrar todos los flujos críticos (grabación/validación) al backend HID y dejar pygame únicamente para pruebas simples si se desea.

---
¿Necesitas añadir inversión de ejes, soporte hat, o export a CSV? Avísame y lo incorporo.
