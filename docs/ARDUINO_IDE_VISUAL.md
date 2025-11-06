# 🖥️ Guía Visual Arduino IDE - ESP32 SNES

Instrucciones paso a paso con capturas conceptuales para usar Arduino IDE.

## 📥 Instalación Arduino IDE

### Paso 1: Descargar Arduino IDE

```
1. Ir a: https://www.arduino.cc/en/software
2. Descargar la versión 2.x para tu sistema operativo:
   - Windows: Arduino IDE 2.x (installer .exe)
   - macOS: Arduino IDE 2.x (.dmg)
   - Linux: Arduino IDE 2.x (AppImage)
3. Instalar siguiendo el asistente
```

### Paso 2: Añadir Soporte para ESP32

```
┌─────────────────────────────────────────────┐
│ Arduino IDE                              [×]│
├─────────────────────────────────────────────┤
│ File  Edit  Sketch  Tools  Help             │
│  │                                           │
│  └─→ Preferences...                          │
└─────────────────────────────────────────────┘

En la ventana de Preferences:

┌──────────────────────────────────────────────────────────┐
│ Preferences                                           [×]│
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Settings                                                 │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Additional Boards Manager URLs:                    │  │
│ │ ┌──────────────────────────────────────────────┐   │  │
│ │ │https://espressif.github.io/arduino-esp32/... │   │  │
│ │ └──────────────────────────────────────────────┘   │  │
│ │                                                 🔗 │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│                    [Cancel]  [OK]                        │
└──────────────────────────────────────────────────────────┘

URL a copiar:
https://espressif.github.io/arduino-esp32/package_esp32_index.json
```

### Paso 3: Instalar ESP32 Board

```
┌─────────────────────────────────────────────┐
│ Arduino IDE                              [×]│
├─────────────────────────────────────────────┤
│ Tools                                        │
│  │                                           │
│  └─→ Board: "..."                            │
│       └─→ Boards Manager...                  │
└─────────────────────────────────────────────┘

En Boards Manager:

┌──────────────────────────────────────────────────────────┐
│ Boards Manager                                        [×]│
├──────────────────────────────────────────────────────────┤
│ 🔍 Search: esp32                                         │
│ ┌────────────────────────────────────────────────────┐  │
│ │ esp32 by Espressif Systems              v3.0.0    │  │
│ │ Arduino support for ESP32/ESP32-S2/ESP32-C3       │  │
│ │                                                    │  │
│ │                                    [INSTALL] ◄──── │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│                                      [Close]             │
└──────────────────────────────────────────────────────────┘
```

## 📂 Abrir el Proyecto

### Paso 1: Navegar a la Carpeta

```
Explorador de Archivos / Finder:

SConE/
└── src/
    └── snes_esp32/
        ├── snes_esp32.ino  ◄── Hacer doble clic aquí
        └── pins_esp32.h
```

### Paso 2: Arduino IDE Abrirá Automáticamente

```
┌─────────────────────────────────────────────────────────┐
│ snes_esp32 - Arduino IDE                             [×]│
├─────────────────────────────────────────────────────────┤
│ File  Edit  Sketch  Tools  Help                         │
├─────────────────────────────────────────────────────────┤
│ Tabs:                                                    │
│ ┌─────────────┐┌─────────────┐                          │
│ │snes_esp32.ino││pins_esp32.h │                          │
│ └─────────────┘└─────────────┘                          │
│                                                          │
│ Código del archivo snes_esp32.ino aparecerá aquí        │
│ /*                                                       │
│  * SNES Controller Emulator for ESP32                   │
│  * ...                                                   │
│  */                                                      │
└──────────────────────────────────────────────────────────┘
```

## ⚙️ Configuración de la Placa

### Paso 1: Seleccionar la Placa ESP32

```
┌─────────────────────────────────────────────┐
│ Tools → Board → esp32 →                      │
├─────────────────────────────────────────────┤
│ ▶ ESP32 Arduino                              │
│   ├─ ESP32 Dev Module         ◄── Seleccionar│
│   ├─ ESP32-S2 Dev Module                     │
│   ├─ ESP32-C3 Dev Module                     │
│   └─ ...                                     │
└─────────────────────────────────────────────┘
```

### Paso 2: Conectar ESP32 y Seleccionar Puerto

```
1. Conectar ESP32 al PC via USB

┌─────────────────────────────────────────────┐
│ Tools → Port →                               │
├─────────────────────────────────────────────┤
│ ▶ /dev/ttyUSB0        ◄── Linux              │
│   /dev/cu.usbserial-0001  ◄── macOS          │
│   COM3                ◄── Windows            │
└─────────────────────────────────────────────┘
```

### Paso 3: Verificar Configuración

```
En la parte inferior de Arduino IDE verás:

┌──────────────────────────────────────────────────────────┐
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ ✅ ESP32 Dev Module on /dev/ttyUSB0                │  │
│ └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## 🔧 Configuraciones Avanzadas (Opcional)

```
Tools → (configuraciones opcionales)

Upload Speed:        921600  ◄── Más rápido
CPU Frequency:       240 MHz (default)
Flash Frequency:     80 MHz
Flash Mode:          QIO
Flash Size:          4MB (32Mb)
Partition Scheme:    Default 4MB
Core Debug Level:    None
PSRAM:               Disabled
```

## 📤 Compilar y Subir

### Método 1: Usando Botones de la Barra

```
┌──────────────────────────────────────────────────────────┐
│ ┌──┐ ┌──┐                                                │
│ │✓ │ │→ │  ◄── Botones principales                       │
│ └──┘ └──┘                                                │
│  │    │                                                   │
│  │    └─→ Upload (Compilar y Subir al ESP32)            │
│  └──────→ Verify (Solo compilar, no subir)               │
└──────────────────────────────────────────────────────────┘
```

### Método 2: Usando el Menú

```
Sketch → Upload                (o Ctrl+U)
Sketch → Verify/Compile        (o Ctrl+R)
```

### Durante la Subida

```
┌──────────────────────────────────────────────────────────┐
│ Output (consola en la parte inferior):                   │
├──────────────────────────────────────────────────────────┤
│ Sketch uses 234560 bytes (17%) of program storage space.│
│ Global variables use 13096 bytes (4%) of dynamic memory. │
│                                                          │
│ esptool.py v4.5.1                                        │
│ Serial port /dev/ttyUSB0                                 │
│ Connecting........_____....._____....._____              │
│                                                          │
│ Writing at 0x00010000... (50 %)                          │
│ Writing at 0x00020000... (100 %)                         │
│ Wrote 249872 bytes (123456 compressed) at 0x00010000     │
│                                                          │
│ Leaving...                                               │
│ Hard resetting via RTS pin...                            │
│                                                          │
│ ✅ Done uploading.                                       │
└──────────────────────────────────────────────────────────┘
```

### ⚠️ Si No Se Conecta

```
Si ves muchos puntos (..........) sin conectar:

1. Presiona y mantén el botón BOOT en el ESP32
2. Presiona brevemente el botón EN/RST
3. Suelta BOOT
4. Intenta subir de nuevo

O:

Mantén presionado BOOT durante todo el proceso de subida
```

## 📟 Abrir Serial Monitor

### Después de Subir Exitosamente

```
┌─────────────────────────────────────────────┐
│ Tools → Serial Monitor         (Ctrl+Shift+M)│
└─────────────────────────────────────────────┘

O hacer clic en el ícono:

┌──────────────────────────────────────────────────────────┐
│                                           ┌──┐           │
│                                           │🔍│ ◄── Clic  │
│                                           └──┘           │
└──────────────────────────────────────────────────────────┘
```

### Configurar Serial Monitor

```
┌──────────────────────────────────────────────────────────┐
│ Serial Monitor                                        [×]│
├──────────────────────────────────────────────────────────┤
│                                                          │
│ SNES Controller Emulator - ESP32                        │
│ Esperando datos uint32_t (4 bytes little-endian)        │
│ Mapeo de bits:                                           │
│   bit 0  = B      bit 8  = D-Up                          │
│   bit 1  = Y      bit 9  = D-Down                        │
│   ...                                                    │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Mensaje a enviar:                           [Send] │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ ┌──────────┐ ┌─────────────┐ [Clear Output] [Scroll]   │
│ │ Newline ▼│ │ 115200 baud ▼│                           │
│ └──────────┘ └─────────────┘                            │
│                    ▲                                     │
│                    └─────── ¡MUY IMPORTANTE: 115200!     │
└──────────────────────────────────────────────────────────┘
```

### ⚠️ Configuración Crítica

```
Baudrate DEBE ser: 115200

Si ves caracteres extraños (����), verifica el baudrate.
```

## 🎮 Enviar Comandos de Prueba

### Usando Serial Monitor (Limitado)

El Serial Monitor de Arduino IDE **NO es ideal** para enviar bytes binarios.

**Recomendado: Usar el script Python**

```bash
python test_snes_serial.py /dev/ttyUSB0
```

## 🔧 Editar el Código

### Cambiar Pines GPIO

```cpp
En la pestaña: pins_esp32.h

// Pines del protocolo SNES
#define LATCH_PIN 25  // ← Cambiar estos números
#define CLOCK_PIN 26  //    según tu hardware
#define DATA_PIN  27  //

// Guardar: Ctrl+S
// Subir de nuevo: Ctrl+U
```

### Activar Debug

```cpp
En la pestaña: snes_esp32.ino

Añadir al final de loop():

void loop() {
    // ... código existente ...
    
    // DEBUG: Mostrar estado
    if (buttonState != 0) {
        Serial.print("RX: 0x");
        Serial.println(buttonState, HEX);
    }
}
```

## 📊 Salida Esperada

### Compilación Exitosa

```
✅ Success
Sketch uses 234560 bytes (17%) of program storage space.
Global variables use 13096 bytes (4%) of dynamic memory.
```

### Serial Monitor Correcto

```
SNES Controller Emulator - ESP32
Esperando datos uint32_t (4 bytes little-endian)
Mapeo de bits:
  bit 0  = B      bit 8  = D-Up
  ...
```

## ❌ Errores Comunes

### Error: "espressif32 not found"

```
❌ Board esp32:esp32:esp32 is unknown

Solución:
1. Tools → Boards Manager
2. Buscar "esp32"
3. Instalar "esp32 by Espressif Systems"
```

### Error: "Port not available"

```
❌ Error opening serial port '/dev/ttyUSB0'

Solución:
- Linux: sudo usermod -a -G dialout $USER (logout/login)
- Windows: Instalar driver CH340 o CP2102
- macOS: Instalar driver USB-to-Serial
```

### Error: "Upload failed"

```
❌ Failed to connect to ESP32

Solución:
1. Presionar botón BOOT al subir
2. Verificar cable USB (debe ser de datos, no solo carga)
3. Probar otro puerto USB
```

## 🎯 Checklist de Verificación

Antes de subir código:

- [ ] Arduino IDE 2.x instalado
- [ ] ESP32 board instalado en Boards Manager
- [ ] Placa correcta seleccionada (ESP32 Dev Module)
- [ ] Puerto correcto seleccionado
- [ ] ESP32 conectado por USB
- [ ] Archivo snes_esp32.ino abierto
- [ ] Código compila sin errores (✓)

Después de subir:

- [ ] Upload exitoso (Done uploading)
- [ ] Serial Monitor abierto
- [ ] Baudrate en 115200
- [ ] Mensaje de inicio visible
- [ ] Sin caracteres extraños

## 📚 Recursos Adicionales

### Drivers USB-to-Serial

Si el puerto no aparece:

**Windows:**
- CH340: http://www.wch.cn/downloads/CH341SER_ZIP.html
- CP2102: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

**macOS:**
- CH340: https://github.com/adrianmihalko/ch340g-ch34g-ch34x-mac-os-x-driver
- CP2102: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

**Linux:**
Generalmente incluidos en el kernel, pero puede requerir permisos:
```bash
sudo usermod -a -G dialout $USER
```

### Links Útiles

- [Arduino IDE Download](https://www.arduino.cc/en/software)
- [ESP32 Arduino Core](https://github.com/espressif/arduino-esp32)
- [ESP32 Pinout Reference](https://randomnerdtutorials.com/esp32-pinout-reference-gpios/)

---

**¿Problemas?** Consulta el [README_ESP32.md](README_ESP32.md) o los archivos de documentación. 📖
