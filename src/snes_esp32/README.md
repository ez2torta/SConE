# SNES Controller Emulator for ESP32

Este es el código principal del emulador de controlador SNES para ESP32.

## 🚀 Inicio Rápido

1. **Abrir este archivo en Arduino IDE:**
   - Hacer doble clic en `snes_esp32.ino`
   - Arduino IDE abrirá automáticamente ambos archivos (.ino y .h)

2. **Configurar la placa:**
   - Tools → Board → ESP32 Dev Module
   - Tools → Port → Seleccionar tu ESP32

3. **Subir el código:**
   - Click en "Upload" (→) o Ctrl+U

4. **Abrir Serial Monitor:**
   - Tools → Serial Monitor (Ctrl+Shift+M)
   - Configurar baudrate: **115200**

## 📁 Archivos

- `snes_esp32.ino` - Código principal
- `pins_esp32.h` - Configuración de pines GPIO

## 🔌 Conexiones Mínimas

```
ESP32 → SNES
─────────────
GPIO 25 → LATCH
GPIO 26 → CLOCK
GPIO 27 → DATA
GND     → GND
```

## 📡 Uso

### Enviar comandos desde Python:

```python
import serial, struct

ser = serial.Serial('/dev/ttyUSB0', 115200)
ser.write(struct.pack('<I', 1 << 12))  # Presionar A
ser.write(struct.pack('<I', 0))         # Soltar
ser.close()
```

### Desde otro Arduino/ESP32:

```cpp
Serial.begin(115200);
uint32_t cmd = 1 << 12;  // A
Serial.write((uint8_t)(cmd & 0xFF));
Serial.write((uint8_t)((cmd >> 8) & 0xFF));
Serial.write((uint8_t)((cmd >> 16) & 0xFF));
Serial.write((uint8_t)((cmd >> 24) & 0xFF));
```

## 🎮 Mapeo de Bits

| Bit | Botón | Hex |
|-----|-------|-----|
| 0 | B | 0x0001 |
| 1 | Y | 0x0002 |
| 2 | SELECT/X | 0x0004 |
| 3 | START | 0x0008 |
| 6 | L | 0x0040 |
| 7 | R | 0x0080 |
| 8 | UP | 0x0100 |
| 9 | DOWN | 0x0200 |
| 10 | LEFT | 0x0400 |
| 11 | RIGHT | 0x0800 |
| 12 | A | 0x1000 |

## ⚙️ Configuración

### Cambiar pines GPIO:

Editar `pins_esp32.h`:
```cpp
#define LATCH_PIN 25  // Cambiar aquí
#define CLOCK_PIN 26
#define DATA_PIN  27
```

### Usar botones físicos en vez de Serial:

En `snes_esp32.ino`, línea 10:
```cpp
volatile bool useSerial = false;  // Cambiar a false
```

## 📚 Documentación Completa

Para documentación detallada, ver archivos en la carpeta `docs/` del proyecto:

- `../../docs/INICIO_RAPIDO_ESP32.md` - Guía de inicio
- `../../docs/README_ESP32.md` - Documentación completa
- `../../docs/REFERENCIA_RAPIDA.md` - Referencia rápida
- `../../docs/BUTTON_MAPPING.md` - Mapeo de botones
- `../../docs/PINOUT_SNES.md` - Diagrama de conexiones
- `../../test_snes_serial.py` - Script de prueba
- `../../examples/test_serial_input.py` - Script de prueba interactivo

## 🐛 Problemas Comunes

**No compila:**
- Instalar soporte ESP32 en Boards Manager

**No sube:**
- Presionar botón BOOT al subir
- Verificar puerto seleccionado

**Serial muestra basura:**
- Verificar baudrate: 115200

**SNES no responde:**
- Revisar 4 conexiones (LATCH, CLOCK, DATA, GND)

---

**¿Necesitas ayuda?** Lee `../../docs/INICIO_RAPIDO_ESP32.md` para instrucciones detalladas.
