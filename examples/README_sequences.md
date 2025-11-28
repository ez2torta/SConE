# Módulos de Test para Secuencias Frame-by-Frame SNES

Este directorio contiene módulos para crear y reproducir secuencias de inputs de SNES con timing preciso basado en frames.

## Archivos

- `sequences.py`: Define secuencias de inputs y funciones para crear combos predefinidos
- `sequence_player.py`: Reproductor de secuencias con diferentes modos de ejecución
- `sequence_examples.py`: Ejemplos de uso de los módulos

## Uso Básico

### Crear una Secuencia

```python
from app.sequences import InputSequence, SNESButton

# Crear secuencia
seq = InputSequence("Mi Combo", "Un combo personalizado")

# Agregar inputs
seq.add_button_press(0, SNESButton.A, 3)    # A por 3 frames
seq.add_combo(5, [SNESButton.UP, SNESButton.A], 2)  # UP+A por 2 frames
```

### Reproducir con Controlador

```python
from app.controllers.controller import SNESController
from app.sequence_player import SequencePlayer

controller = SNESController()
player = SequencePlayer(controller, fps=60)
player.play_sequence(seq)
controller.close()
```

### Secuencias Predefinidas

```python
from app.sequences import (
    create_hadouken_sequence,
    create_shoryuken_sequence,
    create_konami_code_sequence
)

hadouken = create_hadouken_sequence()
player.play_sequence(hadouken)
```

## Modos de Reproducción

### Automático
```python
player.play_sequence(sequence)  # Reproduce automáticamente
```

### Frame-by-Frame Interactivo
```python
player.play_frame_by_frame(sequence)  # Presiona Enter por cada frame
```

### Modo Interactivo Completo
```bash
python -m app.sequence_player interactive
```

Comandos disponibles:
- `hadouken`, `shoryuken`, `konami`, `combo`, `jump`
- `custom` - Crear secuencia personalizada
- `save <file>` - Guardar secuencia
- `load <file>` - Cargar secuencia
- `frame` - Modo frame-by-frame
- `quit` - Salir

## Guardar/Cargar Secuencias

```python
# Guardar
player.save_sequence(seq, "mi_combo.json")

# Cargar
loaded_seq = player.load_sequence("mi_combo.json")
```

## Formato JSON de Secuencias

```json
{
  "name": "Mi Secuencia",
  "description": "Descripción",
  "total_frames": 10,
  "frames": [
    {
      "frame": 0,
      "buttons": ["A"],
      "duration_frames": 3
    }
  ]
}
```

## Timing

- **FPS por defecto**: 60 (SNES estándar)
- **Frame time**: ~16.67ms por frame
- Los inputs se mantienen por la duración especificada
- Entre inputs consecutivos, se liberan todos los botones

## Ejemplos

Ejecuta los ejemplos:

```bash
cd /path/to/SConE
python examples/sequence_examples.py
```

Elige una opción del menú para ver diferentes ejemplos.

## Notas Técnicas

- Requiere conexión serial con ESP32
- Puerto configurable via `SNES_SERIAL_PORT` env var
- Compatible con Python 3.7+
- Usa pyserial para comunicación serial