# ⚡ Referencia Rápida - ESP32 SNES Emulator

Hoja de referencia de una página para desarrollo rápido.

## 🔌 Pines (por defecto)

| Señal | GPIO | Color Típico |
|-------|------|--------------|
| LATCH | 25 | Naranja |
| CLOCK | 26 | Amarillo |
| DATA | 27 | Rojo |
| GND | GND | Negro/Blanco |

## 🎮 Mapeo de Bits Serial → SNES

| Bit | Botón | Hex | Python | SNES Clock |
|-----|-------|-----|--------|------------|
| 0 | B | 0x0001 | `1<<0` | 1 |
| 1 | Y | 0x0002 | `1<<1` | 2 |
| 2 | SELECT/X | 0x0004 | `1<<2` | 3/10 |
| 3 | START | 0x0008 | `1<<3` | 4 |
| 6 | L | 0x0040 | `1<<6` | 11 |
| 7 | R | 0x0080 | `1<<7` | 12 |
| 8 | ⬆️ UP | 0x0100 | `1<<8` | 5 |
| 9 | ⬇️ DOWN | 0x0200 | `1<<9` | 6 |
| 10 | ⬅️ LEFT | 0x0400 | `1<<10` | 7 |
| 11 | ➡️ RIGHT | 0x0800 | `1<<11` | 8 |
| 12 | A | 0x1000 | `1<<12` | 9 |

## 💻 Código Python Esencial

```python
import serial, struct

ser = serial.Serial('/dev/ttyUSB0', 115200)

# Enviar comando
def press(bits):
    ser.write(struct.pack('<I', bits))

# Botones individuales
press(1 << 12)  # A
press(1 << 0)   # B
press(1 << 8)   # UP
press(0)        # Soltar todo

# Combinaciones
press((1<<12) | (1<<8))  # A + UP (salto)
```

## 🔧 Código Arduino/ESP32 Esencial

```cpp
// Enviar desde otro micro
void sendSNES(uint32_t cmd) {
    Serial.write((uint8_t)(cmd & 0xFF));
    Serial.write((uint8_t)((cmd >> 8) & 0xFF));
    Serial.write((uint8_t)((cmd >> 16) & 0xFF));
    Serial.write((uint8_t)((cmd >> 24) & 0xFF));
}

sendSNES(1 << 12);  // Presionar A
```

## 📋 Comandos Comunes

| Acción | Valor | Código |
|--------|-------|--------|
| A | 0x00001000 | `1<<12` |
| B | 0x00000001 | `1<<0` |
| A+B | 0x00001001 | `(1<<12)\|(1<<0)` |
| START | 0x00000008 | `1<<3` |
| SELECT | 0x00000004 | `1<<2` |
| UP | 0x00000100 | `1<<8` |
| DOWN | 0x00000200 | `1<<9` |
| LEFT | 0x00000400 | `1<<10` |
| RIGHT | 0x00000800 | `1<<11` |
| L | 0x00000040 | `1<<6` |
| R | 0x00000080 | `1<<7` |
| START+SELECT | 0x0000000C | `(1<<3)\|(1<<2)` |
| UP+A | 0x00001100 | `(1<<8)\|(1<<12)` |

## 🐍 Script Python Completo Mínimo

```python
#!/usr/bin/env python3
import serial, struct, time

# Conectar
s = serial.Serial('/dev/ttyUSB0', 115200)
time.sleep(2)

# Presionar A
s.write(struct.pack('<I', 1 << 12))
time.sleep(0.5)

# Soltar
s.write(struct.pack('<I', 0))
s.close()
```

## 🔍 Debug Serial Monitor

```cpp
// En ESP32: añade a loop()
if (Serial.available()) {
    Serial.print("RX: ");
    Serial.println(buttonState, HEX);
}
```

## ⚙️ Configuración Arduino IDE

```
Placa: ESP32 Dev Module
Puerto: /dev/ttyUSB0 (Linux) o COM# (Windows)
Upload Speed: 921600
Baudrate Serial: 115200
```

## 📂 Estructura de Archivos

```
SConE/
├── src/snes_esp32/
│   ├── snes_esp32.ino     ← Abrir este
│   └── pins_esp32.h
├── test_snes_serial.py    ← Script de prueba
└── README_ESP32.md        ← Documentación
```

## 🚀 Instalación 3 Pasos

```bash
1. Abrir: src/snes_esp32/snes_esp32.ino
2. Tools → Board → ESP32 Dev Module
3. Upload (Ctrl+U)
```

## 🐛 Solución Rápida

| Problema | Solución |
|----------|----------|
| No compila | Instalar ESP32 en Board Manager |
| No sube | Presionar BOOT al subir |
| No hay Serial | Baudrate 115200 |
| SNES no responde | Verificar 4 cables |

## 📞 Valores Útiles

- **Baudrate:** 115200
- **Timeout:** 1 ms
- **Frecuencia SNES:** 60 Hz
- **Bytes por comando:** 4
- **Botones SNES:** 12
- **Voltaje ESP32:** 3.3V
- **Voltaje SNES:** 5V (compatible)

## 🎯 Test Rápido

```python
# test.py
import serial, struct
s = serial.Serial('/dev/ttyUSB0', 115200)

for i in range(12):
    s.write(struct.pack('<I', 1 << i))
    input(f"Bit {i} presionado. Enter para siguiente...")
    s.write(struct.pack('<I', 0))

s.close()
```

## 🔗 Links Importantes

- [README completo](README_ESP32.md)
- [Mapeo de botones](BUTTON_MAPPING.md)
- [Pinout SNES](PINOUT_SNES.md)
- [Flujo de datos](FLUJO_DATOS.md)

---

**¡Guarda esta página!** Es todo lo que necesitas para desarrollo rápido. 📌
