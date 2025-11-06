# 🚀 Inicio Rápido - Bluetooth BLE

Guía rápida para empezar a usar el SNES Controller con Bluetooth BLE.

## ⏱️ Setup Rápido (5 minutos)

### 1️⃣ Preparar el ESP32

```bash
# Opción A: Arduino IDE
# 1. Abre src/snes_esp32/snes_esp32_ble.ino
# 2. Herramientas → Administrar Bibliotecas → Busca "ESP32 BLE Arduino"
# 3. Sube el código al ESP32

# Opción B: PlatformIO
cd /ruta/a/tu/proyecto
pio run -t upload
```

### 2️⃣ Instalar Python

```bash
# Instalar dependencias
pip install bleak pyserial

# O usar el archivo de requisitos
pip install -r requirements_ble.txt
```

### 3️⃣ Probar la Conexión

```bash
# Autodetección BLE (más fácil)
python examples/test_ble_input.py ble

# O con puerto serial si prefieres cable
python examples/test_ble_input.py serial /dev/ttyUSB0
```

¡Listo! 🎉

---

## 📱 Uso Básico

### Modo Test (automático)
```bash
# Ejecuta secuencia completa de tests
python examples/test_ble_input.py ble test
```

### Modo Interactivo
```bash
# Control manual desde terminal
python examples/test_ble_input.py ble interactive

# Ejemplos de comandos:
> A B          # Presiona A + B
> UP A         # Salta (UP + A)
> START        # Pausa
>              # Suelta todo
> quit         # Salir
```

### Modo Turbo
```bash
# Presiona A continuamente
python examples/test_ble_input.py ble turbo
```

---

## 🔧 Problemas Comunes

### ❌ "No se encuentra el dispositivo BLE"

**Solución:**
1. Verifica que el ESP32 esté encendido
2. Reinicia el ESP32 (botón RESET)
3. Asegúrate de que Bluetooth esté activo en tu PC
4. En Linux, ejecuta:
   ```bash
   sudo setcap cap_net_raw,cap_net_admin+eip $(which python3)
   ```

### ❌ "bleak no instalado"

**Solución:**
```bash
pip install bleak
```

### ❌ Latencia alta / desconexiones

**Soluciones:**
- Acerca el ESP32 a tu computadora (< 5 metros)
- Elimina obstáculos metálicos
- Usa USB Serial si necesitas latencia mínima:
  ```bash
  python examples/test_ble_input.py serial /dev/ttyUSB0
  ```

---

## 💻 Ejemplo de Código

### Python - Presionar un botón por BLE

```python
import asyncio
from examples.test_ble_input import SNESControllerBLE, BUTTONS

async def main():
    # Conectar
    controller = SNESControllerBLE()
    await controller.connect()
    
    # Presionar A
    await controller.send_buttons_async(BUTTONS['A'])
    await asyncio.sleep(0.5)
    
    # Soltar
    await controller.send_buttons_async(0)
    
    # Desconectar
    await controller.disconnect()

asyncio.run(main())
```

### Python - Presionar un botón por Serial

```python
from examples.test_ble_input import SNESControllerSerial, BUTTONS
import time

# Conectar
controller = SNESControllerSerial('/dev/ttyUSB0')

# Presionar A
controller.send_buttons(BUTTONS['A'])
time.sleep(0.5)

# Soltar
controller.send_buttons(0)

# Desconectar
controller.close()
```

---

## 📚 Más Ejemplos

```bash
# Ver todos los ejemplos disponibles
python examples/example_ble_usage.py

# Ejecutar todos los ejemplos BLE
python examples/example_ble_usage.py
# Luego selecciona opción 0
```

---

## 🎮 Mapeo de Botones

```
A       → Botón principal (aceptar)
B       → Botón secundario (saltar)
X, Y    → Botones auxiliares
L, R    → Gatillos de hombro
START   → Pausa/menú
SELECT  → Selección/atrás

UP, DOWN, LEFT, RIGHT → D-Pad direccional
```

---

## 🆚 BLE vs Serial USB

| Característica | BLE | Serial |
|---------------|-----|--------|
| **Latencia** | ~20ms | <1ms |
| **Alcance** | ~10m | 3m (cable) |
| **Portabilidad** | ✅ Inalámbrico | ❌ Cable |
| **Estabilidad** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Setup** | Pairing | Plug & Play |

**Recomendación:**
- 🎯 **Gaming casual/testing**: BLE (inalámbrico, cómodo)
- 🏆 **Gaming competitivo**: Serial USB (latencia mínima)

---

## 📖 Documentación Completa

- [README_BLE.md](README_BLE.md) - Guía completa de BLE
- [INICIO_RAPIDO_ESP32.md](INICIO_RAPIDO_ESP32.md) - Guía ESP32 general
- [BUTTON_MAPPING.md](BUTTON_MAPPING.md) - Mapeo de botones
- [FLUJO_DATOS.md](FLUJO_DATOS.md) - Protocolo SNES

---

## 🤝 ¿Necesitas Ayuda?

1. 📖 Lee la [documentación completa](README_BLE.md)
2. 🔍 Busca en los [issues](https://github.com/ez2torta/SConE/issues)
3. 💬 Abre un nuevo issue
4. 💡 Únete al [chat de Gitter](https://gitter.im/jtrinklein/SConE)

---

## ⚡ Tips Pro

### 1. Usar ambos modos simultáneamente
El ESP32 puede aceptar comandos por Serial y BLE al mismo tiempo. Útil para debugging.

### 2. Mejorar rendimiento BLE
```cpp
// En snes_esp32_ble.ino, ajusta estos valores:
pAdvertising->setMinPreferred(0x06);  // Intervalo mínimo
pAdvertising->setMinPreferred(0x12);  // Intervalo máximo
```

### 3. Crear macros de botones
```python
# Combo personalizado
COMBO_SUPER_JUMP = BUTTONS['UP'] | BUTTONS['A'] | BUTTONS['B']
controller.send_buttons(COMBO_SUPER_JUMP)
```

### 4. Scripts personalizados
Usa `test_ble_input.py` como librería en tus propios scripts:

```python
from examples.test_ble_input import SNESControllerBLE, BUTTONS

# Tu código aquí...
```

---

**¡Disfruta jugando! 🎮**
