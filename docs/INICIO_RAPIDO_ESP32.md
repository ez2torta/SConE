# 🚀 Inicio Rápido - SNES Controller ESP32

Guía rápida para usar el emulador de controlador SNES con ESP32.

## 📦 Archivos Principales

| Archivo | Descripción |
|---------|-------------|
| `src/snes_esp32/snes_esp32.ino` | **Código principal para ESP32** |
| `src/snes_esp32/pins_esp32.h` | Definiciones de pines GPIO |
| `README_ESP32.md` | Documentación completa |
| `BUTTON_MAPPING.md` | Referencia de mapeo de botones |
| `test_snes_serial.py` | Script de prueba Python |
| `examples/send_commands_example.ino` | Ejemplo para enviar comandos |

## ⚡ Instalación Rápida (3 pasos)

### 1️⃣ Preparar Arduino IDE

```
1. Instalar Arduino IDE 2.x
2. Añadir soporte ESP32:
   - File → Preferences → Additional Boards URLs
   - Pegar: https://espressif.github.io/arduino-esp32/package_esp32_index.json
3. Tools → Board → Boards Manager → Buscar "ESP32" → Install
```

### 2️⃣ Abrir el Proyecto

```
1. Ir a: src/snes_esp32/
2. Abrir: snes_esp32.ino en Arduino IDE
3. Seleccionar tu placa ESP32 (Tools → Board)
4. Seleccionar puerto USB (Tools → Port)
```

### 3️⃣ Subir y Probar

```
1. Click en "Upload" (→) en Arduino IDE
2. Abrir Serial Monitor (Ctrl+Shift+M o Tools → Serial Monitor)
3. Configurar baudrate: 115200
4. ¡Listo! Verás el mensaje de inicio
```

## 🔌 Conexiones Mínimas

Solo necesitas 4 cables para conectar al SNES:

```
ESP32 → SNES Controller Port
────────────────────────────
GPIO 25 → LATCH (pin 3)
GPIO 26 → CLOCK (pin 2)
GPIO 27 → DATA  (pin 4)
GND     → GND   (pin 1)
```

> ⚠️ **NO conectes +5V del SNES al ESP32** - puede dañarlo

## 📡 Enviar Comandos por Serial

### Opción A: Con Python (recomendado)

```bash
# Instalar pyserial
pip install pyserial

# Ejecutar script de prueba
python test_snes_serial.py /dev/ttyUSB0
# En Windows: python test_snes_serial.py COM3
```

### Opción B: Código Python Mínimo

```python
import serial
import struct

# Conectar
ser = serial.Serial('/dev/ttyUSB0', 115200)

# Presionar botón A (bit 12)
comando = 1 << 12  # 0x00001000
bytes_comando = struct.pack('<I', comando)  # little-endian
ser.write(bytes_comando)

# Soltar todo
ser.write(struct.pack('<I', 0))
ser.close()
```

### Opción C: Desde otro Arduino/ESP32

```cpp
void sendSNESCommand(uint32_t buttons) {
    Serial.write((uint8_t)(buttons & 0xFF));
    Serial.write((uint8_t)((buttons >> 8) & 0xFF));
    Serial.write((uint8_t)((buttons >> 16) & 0xFF));
    Serial.write((uint8_t)((buttons >> 24) & 0xFF));
}

// Ejemplo: Presionar A
sendSNESCommand(1 << 12);
```

## 🎮 Tabla de Comandos Rápida

| Botón | Valor Hex | Comando Python |
|-------|-----------|----------------|
| B | `0x00000001` | `1 << 0` |
| Y | `0x00000002` | `1 << 1` |
| SELECT | `0x00000004` | `1 << 2` |
| START | `0x00000008` | `1 << 3` |
| L | `0x00000040` | `1 << 6` |
| R | `0x00000080` | `1 << 7` |
| ⬆️ UP | `0x00000100` | `1 << 8` |
| ⬇️ DOWN | `0x00000200` | `1 << 9` |
| ⬅️ LEFT | `0x00000400` | `1 << 10` |
| ➡️ RIGHT | `0x00000800` | `1 << 11` |
| A | `0x00001000` | `1 << 12` |
| X | `0x00000004` | `1 << 2` |

### Combinaciones Comunes

```python
# A + B (ambos botones)
comando = (1 << 12) | (1 << 0)  # 0x00001001

# Arriba + A (salto)
comando = (1 << 8) | (1 << 12)  # 0x00001100

# Start + Select (pausa/reset en muchos juegos)
comando = (1 << 3) | (1 << 2)   # 0x0000000C

# L + R (combo de hombros)
comando = (1 << 6) | (1 << 7)   # 0x000000C0
```

## 🔧 Personalización

### Cambiar Pines GPIO

Edita `pins_esp32.h`:

```cpp
#define LATCH_PIN 32  // Cambia estos números
#define CLOCK_PIN 33  // según tu hardware
#define DATA_PIN  25
```

### Usar Botones Físicos en vez de Serial

En `snes_esp32.ino`, línea 10:

```cpp
volatile bool useSerial = false;  // Cambiar a false
```

Luego conecta botones a los GPIO definidos en `pins_esp32.h`.

## 🐛 Problemas Comunes

| Problema | Solución |
|----------|----------|
| No compila | Verifica que ESP32 está instalado en Board Manager |
| No sube | Presiona el botón BOOT en el ESP32 al subir |
| No responde Serial | Verifica baudrate 115200 en Serial Monitor |
| SNES no detecta | Revisa conexiones LATCH/CLOCK/DATA y GND |
| Botones erróneos | Consulta `BUTTON_MAPPING.md` para el mapeo |

## 📚 Siguientes Pasos

1. **Lee la documentación completa:** `README_ESP32.md`
2. **Consulta el mapeo de bits:** `BUTTON_MAPPING.md`
3. **Prueba el script:** `test_snes_serial.py`
4. **Ve ejemplos:** `examples/send_commands_example.ino`

## 💡 Ejemplos de Uso

### Simular el Konami Code

```python
import serial, struct, time

ser = serial.Serial('/dev/ttyUSB0', 115200)
time.sleep(2)

konami = [
    1<<8, 1<<8, 1<<9, 1<<9,  # ↑↑↓↓
    1<<10, 1<<11, 1<<10, 1<<11,  # ←→←→
    1<<0, 1<<12  # BA
]

for cmd in konami:
    ser.write(struct.pack('<I', cmd))
    time.sleep(0.3)
    ser.write(struct.pack('<I', 0))
    time.sleep(0.2)

ser.close()
```

### Control en Tiempo Real

```python
import serial, struct, keyboard  # pip install keyboard

ser = serial.Serial('/dev/ttyUSB0', 115200)

mapping = {
    'up': 8, 'down': 9, 'left': 10, 'right': 11,
    'z': 12, 'x': 0, 'a': 1, 's': 2,  # Teclado → SNES
    'enter': 3, 'shift': 2, 'q': 6, 'w': 7
}

while True:
    cmd = 0
    for key, bit in mapping.items():
        if keyboard.is_pressed(key):
            cmd |= (1 << bit)
    
    ser.write(struct.pack('<I', cmd))
    time.sleep(0.01)  # 100Hz update rate
```

## ✅ Checklist de Verificación

- [ ] Arduino IDE instalado con soporte ESP32
- [ ] Archivos `snes_esp32.ino` y `pins_esp32.h` en la misma carpeta
- [ ] ESP32 conectado por USB y seleccionado en Tools → Port
- [ ] Placa ESP32 correcta seleccionada en Tools → Board
- [ ] Código compilado sin errores
- [ ] Serial Monitor muestra mensaje de inicio a 115200 baudios
- [ ] Conexiones físicas al SNES verificadas (4 cables)
- [ ] Script de prueba Python funciona (opcional)

## 🎯 Resultado Esperado

Al abrir el Serial Monitor deberías ver:

```
SNES Controller Emulator - ESP32
Esperando datos uint32_t (4 bytes little-endian)
Mapeo de bits:
  bit 0  = B      bit 8  = D-Up
  bit 1  = Y      bit 9  = D-Down
  bit 2  = Select bit 10 = D-Left
  bit 3  = Start  bit 11 = D-Right
  bit 4  = (n/a)  bit 12 = A
  bit 5  = (n/a)  bit 13 = X
  bit 6  = L      bit 14 = (n/a)
  bit 7  = R      bit 15 = (n/a)
```

¡Y listo! Tu ESP32 está actuando como controlador SNES 🎮

---

**¿Preguntas?** Consulta `README_ESP32.md` o revisa el código fuente comentado.
