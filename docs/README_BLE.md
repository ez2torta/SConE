# SNES Controller Emulator - Bluetooth BLE Support

Esta extensión añade soporte para Bluetooth BLE al SNES Controller Emulator, permitiendo comunicación inalámbrica además del USB Serial tradicional.

## 📁 Archivos Nuevos

### Firmware ESP32
- **`snes_esp32_ble.ino`** - Firmware ESP32 con soporte dual:
  - USB Serial (115200 baud)
  - Bluetooth BLE (GATT Service)

### Script Python
- **`test_ble_input.py`** - Script de prueba que soporta:
  - Comunicación vía USB Serial
  - Comunicación vía Bluetooth BLE
  - Mismas funciones que `test_serial_input.py` (test, interactive, turbo)

## 🔧 Instalación

### 1. Firmware ESP32

#### Opción A: Arduino IDE
1. Abre `snes_esp32_ble.ino` en Arduino IDE
2. Instala la librería BLE:
   - Sketch → Include Library → Manage Libraries
   - Busca "ESP32 BLE Arduino"
   - Instala la librería oficial de Espressif
3. Selecciona tu placa ESP32
4. Compila y sube el sketch

#### Opción B: PlatformIO
Añade a tu `platformio.ini`:
```ini
[env:esp32_ble]
platform = espressif32
board = esp32dev
framework = arduino
lib_deps = 
    ESP32 BLE Arduino
```

### 2. Script Python

Instala las dependencias necesarias:

```bash
# Para soporte Serial
pip install pyserial

# Para soporte BLE
pip install bleak

# O instala ambas
pip install pyserial bleak
```

## 🚀 Uso

### Comunicación vía USB Serial

```bash
# Test automático
python test_ble_input.py serial /dev/ttyUSB0

# Modo interactivo
python test_ble_input.py serial /dev/ttyUSB0 interactive

# Modo turbo
python test_ble_input.py serial /dev/cu.usbserial-140 turbo
```

### Comunicación vía Bluetooth BLE

```bash
# Autodetección del dispositivo BLE
python test_ble_input.py ble

# Con dirección MAC específica
python test_ble_input.py ble AA:BB:CC:DD:EE:FF

# Modo interactivo
python test_ble_input.py ble interactive

# Modo turbo
python test_ble_input.py ble turbo
```

## 🔌 Protocolo de Comunicación

Ambos modos (Serial y BLE) usan el mismo protocolo:

- **Formato**: uint32_t (4 bytes, little-endian)
- **Cada bit representa un botón**:

```
bit 0  = B          bit 8  = D-Up
bit 1  = Y          bit 9  = D-Down
bit 2  = SELECT/X   bit 10 = D-Left
bit 3  = START      bit 11 = D-Right
bit 4  = (n/a)      bit 12 = A
bit 5  = (n/a)      bit 13 = X
bit 6  = L          bit 14 = (n/a)
bit 7  = R          bit 15 = (n/a)
```

## 📡 Especificaciones BLE

### Información del Dispositivo
- **Nombre del dispositivo**: `SNES-Controller`
- **Service UUID**: `4fafc201-1fb5-459e-8fcc-c5c9c331914b`
- **Characteristic UUID**: `beb5483e-36e1-4688-b7f5-ea07361b26a8`

### Características
- **Propiedades**: Read, Write, Notify
- **Tamaño de datos**: 4 bytes (uint32_t)
- **Formato**: Little-endian

### Proceso de Conexión
1. El ESP32 inicia advertising automáticamente al arrancar
2. El cliente (Python/app móvil) escanea dispositivos BLE
3. Encuentra el dispositivo "SNES-Controller"
4. Se conecta al servicio usando los UUIDs
5. Escribe comandos en la característica

## 🎮 Modos de Operación

### Test Automático (`test`)
Ejecuta una secuencia de prueba completa:
1. Botones de acción (B, Y, A, X)
2. D-Pad (UP, RIGHT, DOWN, LEFT)
3. Botones de hombro (L, R)
4. Botones de sistema (SELECT, START)
5. Combinaciones comunes
6. ¡Konami Code!

### Modo Interactivo (`interactive`)
Permite control manual desde la terminal:
```
> A B START       # Presiona A + B + START
> UP A            # Presiona UP + A
>                 # Suelta todos los botones
> quit            # Sale del programa
```

### Modo Turbo (`turbo`)
Presiona el botón A continuamente a ~60 Hz (rate del SNES)

## 🔍 Troubleshooting

### BLE no encuentra el dispositivo
1. Verifica que el ESP32 esté encendido
2. Comprueba que el LED de Bluetooth esté activo
3. Asegúrate de que no haya otro dispositivo conectado
4. Reinicia el ESP32 y vuelve a intentar
5. En Linux, verifica permisos de Bluetooth:
   ```bash
   sudo setcap cap_net_raw,cap_net_admin+eip $(which python3)
   ```

### Error al conectar por Serial
1. Verifica el puerto correcto:
   ```bash
   # Linux
   ls /dev/ttyUSB* /dev/ttyACM*
   
   # macOS
   ls /dev/cu.usbserial-*
   
   # Windows
   # Revisa en Device Manager
   ```
2. Comprueba permisos (Linux):
   ```bash
   sudo usermod -a -G dialout $USER
   # Luego cierra sesión y vuelve a entrar
   ```

### BLE se desconecta frecuentemente
1. Reduce la distancia entre el ESP32 y el cliente
2. Elimina obstáculos metálicos entre los dispositivos
3. Verifica que no haya interferencia WiFi
4. Considera usar Serial USB para máxima estabilidad

## 🆚 Diferencias entre Serial y BLE

| Característica | USB Serial | Bluetooth BLE |
|---------------|------------|---------------|
| Latencia | < 1 ms | 10-50 ms |
| Alcance | 3 m (cable) | ~10 m |
| Estabilidad | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Portabilidad | ❌ Cable | ✅ Inalámbrico |
| Consumo | Bajo | Medio |
| Setup | Simple | Requiere pairing |

## 💡 Ejemplos de Uso

### Python: Envío Básico por BLE
```python
import asyncio
from test_ble_input import SNESControllerBLE, BUTTONS

async def main():
    controller = SNESControllerBLE()
    await controller.connect()
    
    # Presionar A
    await controller.send_buttons_async(BUTTONS['A'])
    await asyncio.sleep(0.5)
    
    # Soltar
    await controller.send_buttons_async(0)
    
    await controller.disconnect()

asyncio.run(main())
```

### Python: Envío Básico por Serial
```python
from test_ble_input import SNESControllerSerial, BUTTONS

controller = SNESControllerSerial('/dev/ttyUSB0')

# Presionar A
controller.send_buttons(BUTTONS['A'])
time.sleep(0.5)

# Soltar
controller.send_buttons(0)

controller.close()
```

## 🔄 Migración desde Serial

Si ya tienes código usando `test_serial_input.py`, la migración es simple:

```python
# Antes (solo Serial)
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200)
data = struct.pack('<I', button_mask)
ser.write(data)

# Ahora (Serial o BLE)
from test_ble_input import SNESControllerSerial, SNESControllerBLE

# Opción 1: Serial (mismo comportamiento)
controller = SNESControllerSerial('/dev/ttyUSB0')
controller.send_buttons(button_mask)

# Opción 2: BLE (nuevo)
controller = SNESControllerBLE()
await controller.connect()
await controller.send_buttons_async(button_mask)
```

## 📱 App Móvil (Futuro)

El protocolo BLE está diseñado para ser compatible con apps móviles:
- **Android**: Usar Android BLE API
- **iOS**: Usar Core Bluetooth
- **React Native**: Usar react-native-ble-plx

Los UUIDs son estándar y pueden usarse en cualquier plataforma.

## 🛠️ Desarrollo Avanzado

### Personalizar UUIDs
Edita en `snes_esp32_ble.ino`:
```cpp
#define SERVICE_UUID        "tu-uuid-aqui"
#define CHARACTERISTIC_UUID "tu-uuid-aqui"
```

Y en `test_ble_input.py`:
```python
BLE_SERVICE_UUID = "tu-uuid-aqui"
BLE_CHARACTERISTIC_UUID = "tu-uuid-aqui"
```

### Añadir Notificaciones
El firmware soporta notificaciones BLE. Para recibir estado:

```python
async def notification_handler(sender, data):
    button_state = struct.unpack('<I', data)[0]
    print(f"Estado actual: 0x{button_state:04X}")

await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
```

## 📚 Referencias

- [ESP32 BLE Arduino Library](https://github.com/espressif/arduino-esp32/tree/master/libraries/BLE)
- [Bleak Python BLE Library](https://github.com/hbldh/bleak)
- [SNES Controller Protocol](../docs/FLUJO_DATOS.md)
- [Button Mapping](../docs/BUTTON_MAPPING.md)

## 📝 Notas

- El firmware puede aceptar comandos simultáneamente por Serial y BLE
- El último comando recibido (por cualquier canal) es el que se aplica
- BLE tiene mayor latencia que Serial pero es suficiente para gaming casual
- Para competitivo, se recomienda usar Serial USB

## 🤝 Contribuciones

¿Encuentras un bug o tienes una mejora? ¡Abre un issue o PR!

---

**Licencia**: Misma que el proyecto principal SConE
