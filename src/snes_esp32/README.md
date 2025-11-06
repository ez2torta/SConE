# SNES Controller Emulator - ESP32 con Bluetooth BLE

## ⚡ Versiones Disponibles

### `snes_esp32.ino` ← **USAR ESTE**
**Archivo principal** - Versión completa con soporte para:
- ✅ USB Serial (115200 baud)
- ✅ **Bluetooth BLE** (GATT Service)
- ✅ Lectura de pines físicos (modo tradicional)

### Backup (fuera de esta carpeta)
La versión original solo-Serial está guardada en:
- `../snes_esp32_BACKUP_SOLO_SERIAL.ino.txt`

⚠️ **IMPORTANTE**: El archivo backup fue movido FUERA de esta carpeta porque Arduino IDE compila todos los archivos `.ino` juntos, causando errores de redefinición.

---

## 🚀 Inicio Rápido

### 1. Cargar en Arduino IDE

1. Abre **Arduino IDE**
2. Abre `snes_esp32.ino`
3. Selecciona tu placa ESP32 (Tools → Board → ESP32 Dev Module)
4. Selecciona el puerto (Tools → Port)
5. Sube el sketch (→ Upload)

### 2. Verificar en Serial Monitor

```
==============================================
SNES Controller Emulator - ESP32 with BLE
==============================================

Modos de comunicación:
  1. USB Serial (115200 baud)
  2. Bluetooth BLE (GATT Service)

BLE Device Name: SNES-Controller
Esperando conexión...
```

---

## 📡 Uso

### Opción A: USB Serial

```bash
# Desde Python
python examples/test_serial_input.py /dev/cu.usbserial-2140 test
```

### Opción B: Bluetooth BLE

```bash
# Instalar dependencia
pip install bleak

# Ejecutar
python examples/test_ble_input.py
```

### Opción C: Código Python

```python
# Ver ejemplos completos en:
examples/example_ble_usage.py
examples/test_ble_input.py
examples/test_serial_input.py
```

---

## 🎮 Protocolo

Ambos modos (USB Serial y BLE) usan el mismo protocolo:
- **Formato**: `uint32_t` (4 bytes en little-endian)
- **Cada bit** = un botón (1 = presionado, 0 = soltado)

### Mapeo de Bits:

| Bit | Botón    | Hex    | Bit | Botón     | Hex    |
|-----|----------|--------|-----|-----------|--------|
| 0   | B        | 0x0001 | 8   | D-Up      | 0x0100 |
| 1   | Y        | 0x0002 | 9   | D-Down    | 0x0200 |
| 2   | Select   | 0x0004 | 10  | D-Left    | 0x0400 |
| 3   | Start    | 0x0008 | 11  | D-Right   | 0x0800 |
| 6   | L        | 0x0040 | 12  | A         | 0x1000 |
| 7   | R        | 0x0080 | 13  | X         | 0x2000 |

---

## 📶 Bluetooth BLE

### Información del Servicio

- **Device Name**: `SNES-Controller`
- **Service UUID**: `4fafc201-1fb5-459e-8fcc-c5c9c331914b`
- **Characteristic UUID**: `beb5483e-36e1-4688-b7f5-ea07361b26a8`

### Conectarse desde:
- 🐍 Python (usando librería `bleak`)
- 📱 Apps móviles (Android/iOS con nRF Connect)
- 💻 Otros dispositivos BLE

---

## 🔌 Conexiones Hardware

```
ESP32 → SNES Console
────────────────────
GPIO 25 → LATCH
GPIO 26 → CLOCK
GPIO 27 → DATA
GND     → GND
```

Ver diagrama completo: `../../docs/PINOUT_SNES.md`

---

## ⚙️ Configuración

### Cambiar pines GPIO:

Editar `pins_esp32.h`:
```cpp
#define LATCH_PIN 25  // Cambiar aquí
#define CLOCK_PIN 26
#define DATA_PIN  27
```

### Usar botones físicos en vez de Serial/BLE:

En `snes_esp32.ino`, línea ~25:
```cpp
volatile bool useSerial = false;  // Cambiar a false
```

---

## � Troubleshooting

### Error: "redefinition of setup/loop/buttonState..."

**Causa**: Múltiples archivos `.ino` en la misma carpeta.

**Solución**: Arduino IDE compila TODOS los archivos `.ino` juntos. Solo debe haber uno activo.

✅ Correcto: `snes_esp32.ino` + `pins_esp32.h`  
❌ Error: `snes_esp32.ino` + `snes_esp32_BACKUP_SOLO_SERIAL.ino`

**Cómo arreglar**:
```bash
# Renombrar el backup para que no sea .ino
mv snes_esp32_BACKUP_SOLO_SERIAL.ino snes_esp32_BACKUP_SOLO_SERIAL.txt
```

### Bluetooth no se conecta

1. ✅ Verifica Serial Monitor: debe mostrar "BLE: Servicio iniciado"
2. 📱 Usa app de escaneo BLE (ej: nRF Connect) para ver si aparece `SNES-Controller`
3. 🍎 En macOS: Da permisos de Bluetooth a Terminal/Python en Preferencias del Sistema

### Serial muestra basura

- Baud rate debe ser **115200**
- Verifica el puerto correcto con `ls /dev/cu.*`

### No compila

```bash
# Instalar soporte ESP32 en Arduino IDE:
# File → Preferences → Additional Board Manager URLs:
https://dl.espressif.com/dl/package_esp32_index.json

# Luego:
# Tools → Board → Boards Manager → Buscar "esp32" → Install
```

---

## 📚 Más Información

### Documentación Detallada

- `../../docs/INICIO_RAPIDO_BLE.md` - Guía rápida Bluetooth
- `../../docs/README_BLE.md` - Documentación BLE completa
- `../../docs/INSTALACION_LIBRERIAS_BLE.md` - Instalación librerías
- `../../docs/README_ESP32.md` - Documentación ESP32 general
- `../../docs/BUTTON_MAPPING.md` - Mapeo de botones detallado

### Scripts de Ejemplo

- `../../examples/test_ble_input.py` - Test interactivo BLE
- `../../examples/test_serial_input.py` - Test interactivo Serial
- `../../examples/example_ble_usage.py` - Ejemplos de uso BLE

---

## 📊 Comparación de Versiones

| Característica | Solo Serial (backup) | Con BLE (actual) |
|----------------|---------------------|------------------|
| USB Serial     | ✅                  | ✅               |
| Bluetooth BLE  | ❌                  | ✅               |
| Pines físicos  | ✅                  | ✅               |
| Librerías extra| Ninguna             | BLE (incluido)   |
| RAM usada      | ~30KB               | ~60KB            |
| Alcance        | Cable USB           | ~10m wireless    |

---

**¿Problemas?** Abre un issue en GitHub o consulta la documentación en `/docs/`
