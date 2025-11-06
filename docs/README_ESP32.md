# SNES Controller Emulator - ESP32

Versión adaptada para ESP32 con Arduino IDE que permite controlar un SNES mediante comandos Serial.

## 🎮 Características

- ✅ Compatible con ESP32 y Arduino IDE
- ✅ Control via Serial usando `uint32_t` (4 bytes)
- ✅ Soporte para los 12 botones del SNES
- ✅ Opción de usar botones físicos o comandos Serial
- ✅ Sin dependencias de registros AVR

## 📋 Requisitos

- ESP32 (cualquier modelo compatible con Arduino IDE)
- Arduino IDE 2.x o superior
- Soporte para ESP32 instalado en Arduino IDE
  - Ir a `Archivo → Preferencias`
  - Agregar URL: `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
  - Ir a `Herramientas → Placa → Gestor de Placas`
  - Buscar "ESP32" e instalar

## 🔌 Conexiones

### Pines del Protocolo SNES (requeridos)

| Pin ESP32 | Función SNES | Descripción |
|-----------|--------------|-------------|
| GPIO 25   | LATCH        | Señal de sincronización |
| GPIO 26   | CLOCK        | Reloj del protocolo |
| GPIO 27   | DATA         | Datos seriales al SNES |
| GND       | GND          | Tierra común |

### Pines de Botones Físicos (opcionales)

Si quieres conectar botones físicos en lugar de usar Serial:

| Pin ESP32 | Botón        | Conexión |
|-----------|--------------|----------|
| GPIO 2    | B            | Botón a GND |
| GPIO 4    | Y            | Botón a GND |
| GPIO 5    | SELECT       | Botón a GND |
| GPIO 18   | START        | Botón a GND |
| GPIO 19   | D-Pad UP     | Botón a GND |
| GPIO 21   | D-Pad DOWN   | Botón a GND |
| GPIO 22   | D-Pad LEFT   | Botón a GND |
| GPIO 23   | D-Pad RIGHT  | Botón a GND |
| GPIO 13   | A            | Botón a GND |
| GPIO 12   | X            | Botón a GND |
| GPIO 14   | L            | Botón a GND |
| GPIO 15   | R            | Botón a GND |

> **Nota:** Los pines tienen pull-up interno activado. Conecta un lado del botón al GPIO y el otro a GND.

## 📡 Protocolo de Comunicación Serial

El ESP32 espera recibir **4 bytes** que forman un `uint32_t` en formato **little-endian**, donde cada bit representa un botón.

### Mapeo de Bits

```
bit 0  = B           bit 8  = D-Up  
bit 1  = Y           bit 9  = D-Down
bit 2  = X/Select    bit 10 = D-Left
bit 3  = Start       bit 11 = D-Right
bit 4  = (no usado)  bit 12 = A
bit 5  = (no usado)  bit 13 = (no usado)
bit 6  = L           bit 14 = (no usado)
bit 7  = R           bit 15 = (no usado)
```

### Bits Activos del SNES (12 botones)

- **Direccionales (4):** Up, Down, Left, Right
- **Acción (6):** B, Y, Select, Start, A, X
- **Auxiliares (2):** L, R

## 🚀 Instalación

1. Abre `snes_esp32.ino` en Arduino IDE
2. Selecciona tu placa ESP32 en `Herramientas → Placa`
3. Selecciona el puerto correcto en `Herramientas → Puerto`
4. Ajusta los pines en `pins_esp32.h` si es necesario
5. Compila y sube el código

## 💻 Uso

### Modo Serial (por defecto)

1. Conecta el ESP32 al SNES
2. Conecta el ESP32 a tu PC via USB
3. Abre el Monitor Serie a **115200 baudios**
4. Envía 4 bytes en formato little-endian

#### Ejemplo en Python:

```python
import serial
import struct
import time

# Conectar al ESP32
ser = serial.Serial('/dev/ttyUSB0', 115200)  # Ajusta el puerto
time.sleep(2)  # Esperar a que inicie

# Crear comando: presionar A (bit 12)
buttons = 1 << 12  # 0x00001000
data = struct.pack('<I', buttons)  # little-endian uint32

# Enviar al ESP32
ser.write(data)
print(f"Enviado: 0x{buttons:08X}")

# Presionar A + B (bits 12 y 0)
buttons = (1 << 12) | (1 << 0)  # 0x00001001
data = struct.pack('<I', buttons)
ser.write(data)
print(f"Enviado: 0x{buttons:08X}")

# Liberar todos los botones
buttons = 0x00000000
data = struct.pack('<I', buttons)
ser.write(data)
print(f"Enviado: 0x{buttons:08X}")

ser.close()
```

#### Ejemplo de Comandos:

| Acción | Valor Hex | Bytes (little-endian) |
|--------|-----------|----------------------|
| Nada presionado | 0x00000000 | 00 00 00 00 |
| B presionado | 0x00000001 | 01 00 00 00 |
| A presionado | 0x00001000 | 00 10 00 00 |
| Start presionado | 0x00000008 | 08 00 00 00 |
| D-Up presionado | 0x00000100 | 00 01 00 00 |
| A + B + Start | 0x00001009 | 09 10 00 00 |

### Modo Físico

1. Cambia `useSerial = false;` en la línea 10 de `snes_esp32.ino`
2. Conecta botones según la tabla de pines
3. Los botones físicos se leerán directamente

## 🔧 Personalización

### Cambiar Pines

Edita `pins_esp32.h` para usar diferentes GPIOs:

```cpp
#define LATCH_PIN 32  // Cambiar a GPIO32
#define CLOCK_PIN 33  // Cambiar a GPIO33
#define DATA_PIN  25  // Cambiar a GPIO25
```

### Ajustar Mapeo de Botones

Modifica la función `mapSerialToSNES()` en `snes_esp32.ino` para cambiar qué bit controla qué botón.

## 📝 Notas Técnicas

- **Baudrate:** 115200 (estándar ESP32)
- **Timeout Serial:** 1ms para lectura rápida
- **Protocolo SNES:** 12 clocks + 4 no usados
- **Lógica:** LOW = presionado, HIGH = no presionado
- **Pull-ups:** Internos activados en pines de entrada

## 🐛 Solución de Problemas

**Los botones no responden:**
- Verifica las conexiones LATCH, CLOCK, DATA
- Revisa el Monitor Serie para ver si llegan los datos
- Comprueba que el SNES esté detectando el controlador

**Datos corruptos por Serial:**
- Asegúrate de enviar exactamente 4 bytes
- Usa little-endian al empaquetar el uint32_t
- Verifica el baudrate (115200)

**Conflicto de pines:**
- Algunos GPIOs del ESP32 no deben usarse (GPIO 6-11 en la mayoría de modelos)
- Evita GPIO 0, 2, 15 durante el boot si causan problemas

## 📚 Referencias

- [SNES Protocol FAQ](http://www.gamefaqs.com/snes/916396-super-nintendo/faqs/5395)
- [Proyecto original SConE](https://github.com/ez2torta/SConE)
- [ESP32 Arduino Core](https://github.com/espressif/arduino-esp32)

## 📄 Licencia

Mismo que el proyecto original SConE.

---

**Creado por:** Adaptación para ESP32 (2025)  
**Basado en:** SConE by jtrinklein
