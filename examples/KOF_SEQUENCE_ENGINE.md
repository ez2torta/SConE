# 🎮 KOF Sequence Engine - Sistema de Ejecución Frame-Perfect

Sistema modular y extensible para ejecutar secuencias de movimientos de KOF XV con timing frame-perfect, basado en configuración JSON.

## 📋 Características

✅ **Configuración basada en JSON** - Define movimientos de manera declarativa  
✅ **Sistema de referencias** - Reutiliza movimientos en combos y drills  
✅ **Frame-perfect timing** - Ejecución precisa a 60 FPS  
✅ **Parámetros dinámicos** - Movimientos configurables (duración, botón, etc.)  
✅ **Validación automática** - Verifica integridad del archivo de configuración  
✅ **Extensible** - Fácil añadir nuevas secuencias sin modificar código  
✅ **Compatible BLE y Serial** - Funciona con ambos modos de conexión  

---

## 🚀 Inicio Rápido

### 1. Instalación de dependencias

```bash
pip install bleak pyserial
```

### 2. Validar configuración

```bash
python kof_sequence_validator.py
# Opción 1: Validar archivo JSON
```

### 3. Ejecutar motor de secuencias

```bash
python kof_sequence_engine.py
```

### 4. Menú interactivo

El motor presenta un menú con opciones:
- Listar secuencias disponibles
- Ejecutar ataques básicos
- Ejecutar combos
- Ejecutar drills de entrenamiento
- Demos automáticos

---

## 📂 Estructura del Sistema

```
examples/
├── kof_sequences.json           # Archivo de configuración (EDITABLE)
├── kof_sequence_engine.py       # Motor de ejecución principal
├── kof_sequence_validator.py   # Validador y generador
├── test_ble_input.py            # Clases de controlador BLE/Serial
└── KOF_SEQUENCE_ENGINE.md       # Este archivo
```

---

## 📄 Formato del Archivo JSON

### Estructura básica

```json
{
  "metadata": {
    "game": "KOF XV",
    "fps": 60,
    "version": "1.0"
  },
  "button_mapping": { ... },
  "basic_attacks": { ... },
  "special_motions": { ... },
  "combos": { ... },
  "training_drills": { ... }
}
```

### Definir un ataque básico

```json
"st_A": {
  "name": "Standing Light Punch",
  "category": "normal",
  "difficulty": 1,
  "frames": [
    {"input": "5", "hold": 3, "comment": "neutral, preparación"},
    {"input": "5+A", "hold": 1, "comment": "presionar A"},
    {"input": "5", "hold": 5, "comment": "animación"}
  ],
  "total_frames": 9,
  "properties": ["cancelable"]
}
```

**Campos:**
- `name`: Nombre descriptivo
- `category`: Categoría del movimiento
- `difficulty`: 1-5 (⭐ a ⭐⭐⭐⭐⭐)
- `frames`: Lista de frames con `input`, `hold` y `comment` opcional
- `total_frames`: Total de frames de la secuencia
- `properties`: Propiedades especiales (opcional)

### Definir un motion especial

```json
"QCF": {
  "name": "Quarter Circle Forward",
  "notation": "236",
  "category": "motion",
  "difficulty": 2,
  "frames": [
    {"input": "5", "hold": 3, "comment": "neutral"},
    {"input": "2", "hold": 1, "comment": "down"},
    {"input": "3", "hold": 1, "comment": "down-forward"},
    {"input": "6+{button}", "hold": 1, "comment": "forward + button"}
  ],
  "total_frames": 6
}
```

**Placeholder `{button}`**: Se reemplaza dinámicamente al ejecutar.

### Definir un combo (usando referencias)

```json
"cr_B_cr_A_QCF_A": {
  "name": "cr.B > cr.A > QCF+A",
  "category": "combo",
  "difficulty": 3,
  "sequence": [
    {"ref": "basic_attacks.cr_B"},
    {"ref": "basic_attacks.cr_A"},
    {"ref": "special_motions.QCF", "button": "A"}
  ],
  "properties": ["low_starter", "hit_confirm"]
}
```

**Sistema de referencias:**
- `ref`: Ruta a otra secuencia (formato `categoria.nombre`)
- `button`: Parámetro para reemplazar `{button}` en motions
- `params`: Parámetros adicionales (ej: duración)

### Definir movimiento con parámetros

```json
"walk_forward": {
  "name": "Walk Forward",
  "category": "movement",
  "difficulty": 1,
  "frames": [
    {"input": "6", "hold": "{duration}"}
  ],
  "parameters": {
    "duration": {
      "type": "int",
      "default": 30,
      "min": 1,
      "max": 300
    }
  }
}
```

**Uso:**
```python
await engine.execute_sequence('walk_forward', params={'duration': 60})
```

### Definir drill de entrenamiento

```json
"neutral_game_loop": {
  "name": "Neutral Game Loop",
  "category": "drill",
  "description": "Práctica de movimiento básico",
  "sequence": [
    {"ref": "movement.walk_forward", "params": {"duration": 30}},
    {"ref": "movement.walk_backward", "params": {"duration": 20}},
    {"ref": "movement.dash_forward"},
    {"ref": "movement.backdash"},
    {"ref": "advanced_sequences.reset_training"}
  ],
  "total_frames": 181,
  "loop": true
}
```

---

## 💻 Uso Programático

### Inicializar motor

```python
from kof_sequence_engine import SequenceEngine
from test_ble_input import SNESControllerBLE

# Conectar controlador
controller = SNESControllerBLE()
await controller.connect()

# Crear motor
engine = SequenceEngine('kof_sequences.json', controller)
```

### Ejecutar secuencia simple

```python
# Ejecutar ataque básico
await engine.execute_sequence('cr_B', category='basic_attacks')

# Ejecutar motion especial
await engine.execute_sequence('QCF', category='special_motions')
```

### Ejecutar combo

```python
await engine.execute_combo('cr_B_cr_A_QCF_A')
```

### Ejecutar drill con loops

```python
# 3 repeticiones
await engine.execute_drill('neutral_game_loop', loops=3)

# Loop infinito (Ctrl+C para detener)
await engine.execute_drill('neutral_game_loop', loops=-1)
```

### Ejecutar con parámetros personalizados

```python
# Caminar por 60 frames
await engine.execute_sequence(
    'walk_forward',
    category='movement',
    params={'duration': 60}
)
```

### Listar secuencias

```python
# Todas las secuencias
engine.list_sequences()

# Solo una categoría
engine.list_sequences(category='combos')

# Filtrar por dificultad (1-3 estrellas)
engine.list_sequences(filter_difficulty=3)
```

---

## 🎯 Notación de Inputs

### Direcciones (Numpad Notation)

```
 7  8  9     ↖  ↑  ↗
 4  5  6  =  ←  N  →
 1  2  3     ↙  ↓  ↘
```

| Input | Dirección | Descripción |
|-------|-----------|-------------|
| `5` | Neutral | Sin dirección |
| `6` | Right | → |
| `4` | Left | ← |
| `2` | Down | ↓ |
| `8` | Up | ↑ |
| `7` | Up-Left | ↖ |
| `9` | Up-Right | ↗ |
| `1` | Down-Left | ↙ |
| `3` | Down-Right | ↘ |

### Botones

| Input | Botón | Descripción |
|-------|-------|-------------|
| `A` | A | Light Punch |
| `B` | B | Light Kick |
| `C` | C | Strong Punch |
| `D` | D | Strong Kick |
| `AB` | A+B | Roll |
| `CD` | C+D | Blowback |
| `SELECT` | Select | Menú/Reset |
| `START` | Start | Pausa |

### Combinaciones

| Input | Descripción | Ejemplo |
|-------|-------------|---------|
| `5+A` | Neutral + A | Standing A |
| `2+B` | Down + B | Crouch B |
| `6+C` | Forward + C | Forward C |
| `9+D` | Up-Forward + D | Jump D |

---

## 🔧 Validación de Secuencias

### Validar archivo JSON

```bash
python kof_sequence_validator.py
# Opción 1: Validar archivo JSON
```

**El validador verifica:**
- Sintaxis JSON correcta
- Campos requeridos presentes
- Tipos de datos correctos
- Referencias válidas
- Rangos de valores (difficulty 1-5, etc.)

### Ver estadísticas

```bash
python kof_sequence_validator.py
# Opción 2: Mostrar estadísticas
```

**Muestra:**
- Total de secuencias
- Secuencias por categoría
- Distribución por dificultad

---

## ✏️ Añadir Nuevas Secuencias

### 1. Editar JSON directamente

```json
"my_new_combo": {
  "name": "Mi Combo Personalizado",
  "category": "combo",
  "difficulty": 3,
  "sequence": [
    {"ref": "basic_attacks.cr_B"},
    {"ref": "basic_attacks.cl_C"},
    {"ref": "special_motions.DP", "button": "A"}
  ]
}
```

### 2. Usando notación compacta del markdown

**En `trabajo para mañana.md`:**
```markdown
**Secuencia compacta**: `[5×3][5+A][5×5]`
```

**Generar frames:**
```bash
python kof_sequence_validator.py
# Opción 4: Parsear notación compacta
# Input: [5×3][5+A][5×5]
```

**Output:**
```json
[
  {"input": "5", "hold": 3},
  {"input": "5+A", "hold": 1},
  {"input": "5", "hold": 5}
]
```

### 3. Generar plantilla

```bash
python kof_sequence_validator.py
# Opción 3: Generar plantilla de secuencia
```

---

## 🎓 Ejemplos Avanzados

### Combo con timing personalizado

```json
"advanced_combo": {
  "name": "Combo con esperas",
  "category": "combo",
  "difficulty": 4,
  "sequence": [
    {"ref": "basic_attacks.cl_C"},
    {"wait": 5, "comment": "esperar hit confirm"},
    {"ref": "special_motions.QCF", "button": "C"},
    {"wait": 10, "comment": "esperar recovery"},
    {"ref": "special_motions.DP", "button": "A"}
  ]
}
```

**`wait`**: Pausa en frames sin input.

### Drill con variaciones

```json
"pressure_drill": {
  "name": "Drill de Presión",
  "category": "drill",
  "sequence": [
    {"ref": "advanced_sequences.hop_forward_attack"},
    {"ref": "basic_attacks.cr_B"},
    {"ref": "basic_attacks.cr_B"},
    {"ref": "basic_attacks.cr_A"},
    {"ref": "special_motions.QCF", "button": "A"},
    {"wait": 30},
    {"ref": "advanced_sequences.reset_training"}
  ],
  "loop": true
}
```

### Secuencia con frame directo

```json
"custom_sequence": {
  "name": "Secuencia Custom",
  "category": "sequence",
  "sequence": [
    {"ref": "movement.dash_forward"},
    {"input": "6+C", "hold": 1, "comment": "attack durante dash"},
    {"input": "6", "hold": 5},
    {"input": "5", "hold": 3}
  ]
}
```

**Mezcla referencias y frames directos.**

---

## 📊 Categorías de Secuencias

| Categoría | Descripción | Ejemplos |
|-----------|-------------|----------|
| `basic_attacks` | Ataques normales | st.A, cr.B, cl.C |
| `special_motions` | Motions de especiales | QCF, DP, HCB |
| `movement` | Movimiento | walk, dash, jump, hop |
| `aerial_attacks` | Ataques aéreos | j.A, j.D |
| `combos` | Combinaciones | cr.B>cr.A>QCF+A |
| `advanced_sequences` | Secuencias complejas | walk>grab, run>attack |
| `training_drills` | Rutinas de práctica | neutral_game_loop |

---

## 🎮 Propiedades Especiales

### Ataques

- `cancelable`: Se puede cancelar en special
- `low`: Pega bajo (debe bloquear agachado)
- `overhead`: Pega alto (debe bloquear de pie)
- `knockdown`: Derriba al oponente
- `unsafe`: Vulnerable si bloqueado
- `invincible`: Frames de invencibilidad
- `close`: Solo funciona cerca
- `priority`: Alta prioridad de ejecución

### Motions

- `command_grab`: Command grab (no bloqueable)
- `unblockable`: No se puede bloquear
- `invincible`: Tiene frames invencibles

### Combos

- `low_starter`: Comienza con ataque bajo
- `overhead_starter`: Comienza con overhead
- `hit_confirm`: Requiere confirmación visual
- `jump_in`: Comienza con salto

---

## 🔄 Sistema de Referencias

### Formato de referencia

```
"categoria.nombre"
```

**Ejemplos:**
- `basic_attacks.cr_B`
- `special_motions.QCF`
- `movement.dash_forward`
- `advanced_sequences.reset_training`

### Referencias con parámetros

```json
{
  "ref": "special_motions.QCF",
  "button": "A"
}
```

```json
{
  "ref": "movement.walk_forward",
  "params": {"duration": 60}
}
```

### Referencias con timing

```json
{
  "ref": "aerial_attacks.j_D",
  "timing": "apex"  // Comentario para timing óptimo
}
```

---

## 🐛 Debugging

### Ver frames ejecutados

El motor imprime cada frame:

```
🎮 Ejecutando: Crouch Light Kick [basic_attacks] ⭐⭐
   [2f] 2: mantener down
   [1f] 2+B: down + B
   [4f] 2: mantener durante hit
   [2f] 5: recovery
✅ Completado (9 frames)
```

### Modo verbose

```python
# Con información detallada
await engine.execute_sequence('cr_B', verbose=True)

# Sin información
await engine.execute_sequence('cr_B', verbose=False)
```

### Validar antes de ejecutar

```bash
python kof_sequence_validator.py
```

**Reporta:**
- ❌ Errores: Problemas que impiden ejecución
- ⚠️ Advertencias: Problemas menores

---

## 📈 Rendimiento

- **FPS**: 60 frames por segundo
- **Frame duration**: 16.67ms por frame
- **Precisión**: ±1ms (limitado por Python asyncio)
- **Overhead**: ~0.5ms por frame (negligible)

**Recomendaciones:**
- Ejecutar en máquina sin carga alta
- Usar BLE en lugar de Serial para mejor latencia
- Evitar loops infinitos con secuencias muy largas

---

## 🆘 Solución de Problemas

### El motor no encuentra el JSON

```
❌ No se encontró el archivo: kof_sequences.json
```

**Solución**: Asegúrate de que `kof_sequences.json` esté en el mismo directorio que `kof_sequence_engine.py`.

### Error de referencia no encontrada

```
❌ Referencia no encontrada: basic_attacks.cr_B
```

**Solución**: Verifica que la secuencia exista en el JSON y la ruta sea correcta.

### BLE no conecta

```
❌ Error al conectar BLE: Device not found
```

**Solución**:
1. Verifica que el ESP32 esté encendido
2. Verifica que el nombre del dispositivo sea "SNES Controller"
3. Aumenta el timeout de scan en `test_ble_input.py`

### Timing incorrecto

**Problema**: Los movimientos se ejecutan muy rápido o lento.

**Solución**:
1. Verifica que `fps` en metadata sea 60
2. Verifica que `hold` en frames sea correcto
3. Usa `await asyncio.sleep()` en lugar de `time.sleep()` con BLE

---

## 🚀 Próximas Características

- [ ] Soporte para macros personalizados
- [ ] Grabación de inputs para generar JSON
- [ ] Integración con vision AI para hit confirms
- [ ] Export a otros formatos (YAML, TOML)
- [ ] GUI para edición de secuencias
- [ ] Análisis de frame data desde replays
- [ ] Soporte para múltiples juegos (SF6, GGST, etc.)

---

## 📚 Referencias

- **Documentación base**: `trabajo para mañana.md`
- **Notación**: Numpad notation estándar de fighting games
- **Frame data**: 60 FPS (KOF XV estándar)

---

## 🤝 Contribuir

Para añadir nuevas secuencias al JSON:

1. Crear la secuencia en el JSON
2. Validar con `kof_sequence_validator.py`
3. Probar con `kof_sequence_engine.py`
4. Documentar en comentarios

---

## 📝 Licencia

Mismo que el proyecto SConE principal.

---

**¡Disfruta de tu entrenamiento frame-perfect en KOF XV! 🎮⭐**
