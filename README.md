SConE
=====

[![Join the chat at https://gitter.im/jtrinklein/SConE](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/jtrinklein/SConE?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

**S**NES **Con**troller **E**mulator using Arduino (Uno)

---

## 🆕 Nueva Versión ESP32 con Control Serial y BLE

**¡Ahora disponible una versión para ESP32!** Esta nueva implementación permite controlar el SNES mediante comandos Serial usando `uint32_t` (4 bytes) o **Bluetooth BLE**.

### 🚀 [**→ IR A LA GUÍA DE INICIO RÁPIDO ESP32 ←**](docs/INICIO_RAPIDO_ESP32.md)

**Archivos de la versión ESP32:**
- 📁 `src/snes_esp32/` - Código principal para ESP32
- 📖 `docs/` - Documentación completa
- 🧪 `test_snes_serial.py` - Script de prueba en Python
- 💡 `examples/` - Ejemplos de uso (Serial y BLE)

**Características de la versión ESP32:**
- ✅ Control via Serial (USB) con protocolo `uint32_t`
- ✅ **Control via Bluetooth BLE con protocolo `uint32_t`**
- ✅ Compatible con ESP32 y Arduino IDE
- ✅ Soporte para los 12 botones del SNES
- ✅ Sin dependencias de registros AVR
- ✅ Ejemplos en Python y Arduino para BLE
- ✅ Sin necesidad de pines físicos para botones

### 📡 Control via Bluetooth BLE

La nueva versión BLE permite controlar el SNES de forma inalámbrica:

- **Servicio BLE:** `4fafc201-1fb5-459e-8fcc-c5c9c331914b`
- **Característica:** `beb5483e-36e1-4688-b7f5-ea07361b26a8`
- **Protocolo:** Envía 4 bytes (little-endian) formando un `uint32_t`
- **Mapeo de bits:** Ver documentación completa

**Ejemplos BLE:**
- 🐍 `examples/ble_snes_example.py` - Cliente Python con bleak
- 🧪 `examples/ble_test_simple.py` - Script de pruebas BLE
- 🧪 `examples/test_ble_input.py` - **Script completo de pruebas BLE (recomendado)**
- 🔧 `examples/ble_snes_client_arduino.ino` - Cliente Arduino/ESP32
- 📦 `requirements.txt` - Dependencias Python

**🧪 Script de Pruebas BLE Completo:**

Para probar la conexión BLE de forma completa, usa `test_ble_input.py`:

```bash
# Activar virtualenv
source .venv/bin/activate

# Ejecutar pruebas completas
python examples/test_ble_input.py test

# Modo interactivo
python examples/test_ble_input.py interactive

# Modo turbo (presiona A continuamente)
python examples/test_ble_input.py turbo
```

Este script incluye:
- ✅ Secuencia completa de pruebas (todos los botones)
- ✅ Código Konami completo
- ✅ Modo interactivo para control manual
- ✅ Modo turbo para pruebas continuas
- ✅ Manejo de errores y desconexión automática

**Documentación ESP32:**
- 📦 [**docs/INDICE.md**](docs/INDICE.md) - Navegación completa del proyecto
- ⚡ [**docs/REFERENCIA_RAPIDA.md**](docs/REFERENCIA_RAPIDA.md) - Cheatsheet de una página
- 📖 [**docs/README_ESP32.md**](docs/README_ESP32.md) - Documentación técnica completa
- 🖥️ [**docs/ARDUINO_IDE_VISUAL.md**](docs/ARDUINO_IDE_VISUAL.md) - Guía visual Arduino IDE

---

## 📜 Versión Original (Arduino Uno)

## Overview

This is a basic SNES controller emulator written for the Arduino Uno.

I got the timing data from this [Pinouts & Protocol FAQ](http://www.gamefaqs.com/snes/916396-super-nintendo/faqs/5395) on gamefaqs.com. I've extracted some of the important details to [snes-flow.md](snes-flow.md).

## Pin Assignments

| Pin | Purpose       | Pin Mode      |
|-----|---------------|---------------|
| A0  | Data Latch    | INPUT         |
| A1  | Data Clock    | INPUT         |
| A2  | Serial Data   | OUTPUT        |
|  2  | Button B      | INPUT Pull-Up |
|  3  | Button Y      | INPUT Pull-Up |
|  4  | Button Select | INPUT Pull-Up |
|  5  | Button Start  | INPUT Pull-Up |
|  6  | Pad UP        | INPUT Pull-Up |
|  7  | Pad Down      | INPUT Pull-Up |
|  8  | Pad Left      | INPUT Pull-Up |
|  9  | Pad Right     | INPUT Pull-Up |
| 10  | Button A      | INPUT Pull-Up |
| 11  | Button X      | INPUT Pull-Up |
| 12  | Button L      | INPUT Pull-Up |
| 13  | Button R      | INPUT Pull-Up |

## Building

I'm using [platformio](http://platformio.org/) to build and deploy the code simply so I didn't have to use the Arduino IDE. Instructions for how to install and set it up can be found on their site. [platformio.ini](platformio.ini) contains the configuration for platformio.

## Reading Buttons

When reading buttons, keep in mind that if a pin is HIGH, the button is not pressed. When a pin reads LOW, the pin is pressed.

## Future Plans

I'm also planning to provide data over USB using the [UnoJoy](https://github.com/AlanChatham/UnoJoy) project, which is where the files in UnoJoy/ come from. 

This will depend on 2 things:

- how much time is left after SNES protocol
- how much time the UnoJoy serial write takes

